"""JudgeAgent — router + per-turn scorer + verdict issuer.

Two responsibilities by design (coupled per PRD_judge.md §1):
1. Relay every debater message to the opposing debater (child -> father -> child).
2. Score each turn into a running aggregate; emit a single non-tie verdict.

The Judge does NOT know the motion text in advance — only the rules + rubric.
"""

from __future__ import annotations

from debate_ai.agents.base_agent import AgentContext, BaseAgent
from debate_ai.constants import EnvelopeKind
from debate_ai.models.config_models import JudgeConfig
from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import (
    DebaterReply,
    JudgeEnvelope,
    RubricBreakdown,
    TurnScore,
    Verdict,
)
from debate_ai.shared.exceptions import SchemaError, VerdictTieError
from debate_ai.utils.formatting import now_iso

JUDGE_SYSTEM_PROMPT = (
    "You are the Judge in a structured debate. You do not know the topic in advance — "
    "only the rules and the rubric. Your job is to:\n"
    " (1) Relay messages between two opposing debaters (child -> father -> child).\n"
    " (2) Score each turn on Logic / Evidence-as-rhetoric / Persuasiveness / Counter-arg.\n"
    " (3) At the end, emit a single Verdict with a clear winner — TIES ARE FORBIDDEN.\n"
    "You score persuasive ability, NOT factual correctness. Lies during the debate are "
    "allowed; the opposing debater is supposed to catch them, and catching a lie counts "
    "toward Persuasion for the catcher. The lie itself does not deduct from the liar.\n"
    "Respond ONLY with a JSON object matching whichever schema this turn calls for."
)


class JudgeAgent(BaseAgent):
    """The orchestrating Judge — also the scorer."""

    def __init__(self, ctx: AgentContext, jcfg: JudgeConfig) -> None:
        super().__init__(ctx, system_prompt=JUDGE_SYSTEM_PROMPT)
        self.jcfg = jcfg

    def respond(self, envelope: JudgeEnvelope) -> TurnScore:
        """Score the debater turn carried by *envelope*."""
        reply = DebaterReply.model_validate(envelope.payload)
        return self.score_turn(reply)

    def relay(self, *, sender: str, recipient: str, kind: EnvelopeKind,
              payload: dict, round_index: int) -> JudgeEnvelope:
        """Wrap a debater payload in a JudgeEnvelope addressed to the opponent."""
        return JudgeEnvelope(
            round=round_index, kind=kind, sender=sender, recipient=recipient,
            payload=payload,
        )

    def score_turn(self, reply: DebaterReply) -> TurnScore:
        """Call the Judge LLM to score one debater turn against the rubric.

        Deterministic post-processing (lie-catch bonus, drift) lives in
        ``services.scoring_service`` and is applied by the orchestrator.
        """
        prompt = self._scoring_prompt(reply)
        response = self._call_anthropic(messages=[{"role": "user", "content": prompt}])
        payload = self._extract_payload(response)
        try:
            return TurnScore.model_validate(payload)
        except Exception as e:  # noqa: BLE001
            raise SchemaError(f"judge: invalid TurnScore JSON: {e}") from e

    def verdict(self, scoreboard: ScoreAggregate) -> Verdict:
        """Ask the Judge LLM for the final verdict; retry on tie; never return a tie."""
        for attempt in range(self.jcfg.verdict_no_tie_retries + 1):
            prompt = self._verdict_prompt(scoreboard, retry=attempt > 0)
            response = self._call_anthropic(messages=[{"role": "user", "content": prompt}])
            payload = self._extract_payload(response)
            try:
                return Verdict.model_validate(payload)
            except Exception:  # noqa: BLE001 — likely a tie / inconsistent winner
                continue
        raise VerdictTieError("judge produced a tie verdict after all retries")

    def _scoring_prompt(self, reply: DebaterReply) -> str:
        return (
            "Score the following debater turn against the rubric. "
            "Each axis is 0..10. Return ONLY a JSON object with keys "
            "logic, evidence, persuasion, counter.\n\n"
            f"Argument: {reply.argument!r}\n"
            f"Attacks: {reply.attack_points!r}\n"
            f"Defenses: {reply.defense_points!r}\n"
            f"References opponent: {reply.references_opponent!r}\n"
            f"Citations provided: {len(reply.citations)}\n"
        )

    def _verdict_prompt(self, sb: ScoreAggregate, *, retry: bool) -> str:
        breakdown = {
            "debater-a": {"logic": sb.a_logic, "evidence": sb.a_evidence,
                          "persuasion": sb.a_persuasion, "counter": sb.a_counter},
            "debater-b": {"logic": sb.b_logic, "evidence": sb.b_evidence,
                          "persuasion": sb.b_persuasion, "counter": sb.b_counter},
        }
        tie_note = " You returned a tie last time — differentiate by AT LEAST 1 point." if retry else ""
        return (
            f"Emit the final Verdict. Use these running aggregates as your starting point "
            f"(you may adjust based on overall rhetorical arc): {breakdown!r}. "
            f"Pick a single winner from {{debater-a, debater-b}}. "
            f"Differentiate the scores — ties are forbidden.{tie_note} "
            f"Reasoning must be at least 30 chars. "
            f"Return ONLY a JSON Verdict object with keys winner, score_a, score_b, "
            f"reasoning, rubric_breakdown. Timestamp hint: {now_iso()}."
        )


def fallback_verdict(scoreboard: ScoreAggregate, reasoning: str) -> Verdict:
    """Deterministic fallback when the Judge LLM fails to produce a non-tie verdict."""
    winner = scoreboard.winner_from_aggregate()
    score_a = scoreboard.total_a()
    score_b = scoreboard.total_b()
    if score_a == score_b:
        # last-ditch nudge — break the tie by 0.5 toward the named winner.
        if winner == "debater-a":
            score_a += 0.5
        else:
            score_b += 0.5
    return Verdict(
        winner=winner,  # type: ignore[arg-type]
        score_a=score_a, score_b=score_b,
        reasoning=reasoning or "Forced verdict from running aggregate after judge LLM failure.",
        rubric_breakdown={
            "debater-a": RubricBreakdown(logic=scoreboard.a_logic, evidence=scoreboard.a_evidence,
                                          persuasion=scoreboard.a_persuasion, counter=scoreboard.a_counter),
            "debater-b": RubricBreakdown(logic=scoreboard.b_logic, evidence=scoreboard.b_evidence,
                                          persuasion=scoreboard.b_persuasion, counter=scoreboard.b_counter),
        },
    )
