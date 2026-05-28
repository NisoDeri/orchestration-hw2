"""Pre-scripted demo agents for running without an API key."""

from __future__ import annotations

from debate_ai.agents.demo_data import SCORES_A, SCORES_B
from debate_ai.constants import EnvelopeKind
from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import (
    DebaterReply,
    JudgeEnvelope,
    RubricBreakdown,
    TurnScore,
    Verdict,
)


def _reply(args: list[dict], idx: int) -> DebaterReply:
    d = args[idx % len(args)]
    return DebaterReply(
        argument=d["arg"],
        confidence=d["conf"],
        attack_points=d["attack"],
        defense_points=d["defense"],
        citations=[d["cite"]],
        references_opponent=f"Directly countering opponent's Round {max(0, idx - 1)} claims",
    )


class DemoDebater:
    def __init__(self, args: list[dict]) -> None:
        self._args = args
        self._idx = 0

    def respond(self, _envelope: JudgeEnvelope) -> DebaterReply:
        reply = _reply(self._args, self._idx)
        self._idx += 1
        return reply


class DemoJudge:
    def __init__(self) -> None:
        self._idx = 0

    def relay(
        self, *, sender: str, recipient: str, kind: EnvelopeKind, payload: dict, round_index: int
    ) -> JudgeEnvelope:
        return JudgeEnvelope(
            round=round_index,
            kind=kind,
            sender=sender,
            recipient=recipient,
            payload=payload,
        )

    def score_turn(self, _reply: DebaterReply) -> TurnScore:
        scores = SCORES_A if self._idx % 2 == 0 else SCORES_B
        t = scores[(self._idx // 2) % len(scores)]
        self._idx += 1
        return TurnScore(logic=t[0], evidence=t[1], persuasion=t[2], counter=t[3])

    def verdict(self, sb: ScoreAggregate) -> Verdict:
        return Verdict(
            winner="debater-a",
            score_a=sb.total_a() + 2,
            score_b=sb.total_b(),
            reasoning=(
                "Messi demonstrated superior rhetorical range throughout the debate, weaving "
                "statistical evidence with emotional narrative. His World Cup argument in Round 5 "
                "was the decisive blow — Ronaldo had no equivalent counter. While Ronaldo scored "
                "well on evidence and counter-arguments, Messi's persuasion scores were consistently "
                "higher, reflecting a more compelling overall narrative arc."
            ),
            rubric_breakdown={
                "debater-a": RubricBreakdown(
                    logic=sb.a_logic,
                    evidence=sb.a_evidence,
                    persuasion=sb.a_persuasion,
                    counter=sb.a_counter,
                ),
                "debater-b": RubricBreakdown(
                    logic=sb.b_logic,
                    evidence=sb.b_evidence,
                    persuasion=sb.b_persuasion,
                    counter=sb.b_counter,
                ),
            },
        )
