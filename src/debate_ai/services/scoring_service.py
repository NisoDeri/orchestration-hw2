"""Deterministic scoring helpers — drift detector + lie-catch bonus + aggregation.

The per-turn rubric scoring itself is the Judge LLM's job (see PRD_judge.md
§4). Everything in this module is *deterministic* logic the orchestrator runs
around those LLM calls so that lie-catch credit and drift detection are
consistent and testable.
"""

from __future__ import annotations

from debate_ai.constants import AgentRole
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import DebaterReply, TurnScore
from debate_ai.utils.validators import contains_any


class ScoringService:
    """Stateless helpers used by the orchestrator + JudgeAgent."""

    def __init__(self, agreement_keywords: list[str], drift_window_turns: int = 2) -> None:
        self.agreement_keywords = agreement_keywords
        self.drift_window_turns = drift_window_turns

    def apply_lie_catch_bonus(
        self,
        score: TurnScore,
        reply: DebaterReply,
        opponent_replies: list[DebaterReply],
    ) -> TurnScore:
        """Floor a debater's persuasion at +1 if they referenced + attacked an opponent claim.

        Per PRD_judge.md §4: catching the opponent's previous statement (true
        OR false — judge doesn't care which) is rewarded.
        """
        if not opponent_replies:
            return score
        if not reply.attack_points:
            return score
        last_opponent = opponent_replies[-1]
        # Did the reply reference any part of the opponent's previous claims?
        opponent_text = (
            last_opponent.argument + " "
            + " ".join(last_opponent.attack_points)
            + " ".join(last_opponent.defense_points)
        )
        if reply.references_opponent and reply.references_opponent.lower() in (
            opponent_text.lower()
        ):
            return score.model_copy(update={"persuasion": max(score.persuasion, score.persuasion + 1.0)})
        return score

    def detect_drift(self, memory: ConversationMemory) -> bool:
        """True if the last ``drift_window_turns`` debater turns BOTH show agreement.

        Per PRD_judge.md §7: one-off agreement is fine; sustained agreement
        triggers a re-anchor ruling from the Judge.
        """
        debater_envs = [
            e for e in memory.snapshot()
            if e.envelope.sender in (AgentRole.DEBATER_A.value, AgentRole.DEBATER_B.value)
        ]
        window = debater_envs[-self.drift_window_turns:]
        if len(window) < self.drift_window_turns:
            return False
        return all(self._envelope_shows_agreement(e.envelope.payload) for e in window)

    def _envelope_shows_agreement(self, payload: dict) -> bool:
        text = payload.get("references_opponent", "") + " " + payload.get("argument", "")
        return contains_any(text, self.agreement_keywords)

    def aggregate_score(self, history: list[tuple[str, TurnScore]]) -> ScoreAggregate:
        """Roll a list of (debater_id, TurnScore) into a ScoreAggregate."""
        agg = ScoreAggregate()
        for debater, ts in history:
            agg.add_turn(debater, ts)
        return agg
