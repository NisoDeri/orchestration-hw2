"""Pre-scripted demo agents for running without an API key."""
from __future__ import annotations

from debate_ai.constants import EnvelopeKind
from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import (
    DebaterReply,
    JudgeEnvelope,
    RubricBreakdown,
    TurnScore,
    Verdict,
)

_MESSI_LINES = [
    "Messi has 8 Ballon d'Or trophies — more than any player in football history, proving sustained individual excellence over nearly two decades.",
    "While Ronaldo chases individual records, Messi orchestrates entire teams. His 2014-15 treble with Barcelona saw him create 29 assists alongside 58 goals.",
    "Messi's World Cup triumph in 2022 cemented his legacy. He scored 7 goals and provided 3 assists across the tournament, winning the Golden Ball.",
    "The 91-goal calendar year in 2012 is a record that may never be broken. That's almost a goal every 3.5 days for an entire year.",
    "Messi's dribbling success rate of 68% is unmatched. He completed over 3,000 successful dribbles in La Liga alone — a dimension Ronaldo cannot replicate.",
]

_RONALDO_LINES = [
    "Cristiano Ronaldo holds the all-time international scoring record with 130+ goals for Portugal — no player in history has matched that across competitive matches.",
    "Ronaldo won league titles in England, Spain, and Italy — proving he can dominate in any league. Messi spent his prime in one league with one superteam.",
    "In Champions League knockout rounds, Ronaldo scored 67 goals. When the pressure is highest, Ronaldo delivers. That's 20 more than Messi in the same stages.",
    "Ronaldo transformed his game from a winger to a striker and maintained elite production into his late 30s. That physical and tactical adaptability is unprecedented.",
    "Five Champions League titles across two different clubs. Ronaldo was the leading scorer in four of those campaigns — he owns Europe's biggest stage.",
]

_SCORES_A = [
    TurnScore(logic=8.5, evidence=7.5, persuasion=9.0, counter=7.0),
    TurnScore(logic=8.0, evidence=8.0, persuasion=8.5, counter=7.5),
    TurnScore(logic=9.0, evidence=7.0, persuasion=8.0, counter=8.0),
    TurnScore(logic=7.5, evidence=8.5, persuasion=8.5, counter=7.0),
    TurnScore(logic=8.0, evidence=7.5, persuasion=9.0, counter=8.5),
]

_SCORES_B = [
    TurnScore(logic=8.0, evidence=8.0, persuasion=7.5, counter=7.5),
    TurnScore(logic=7.5, evidence=8.5, persuasion=7.0, counter=8.0),
    TurnScore(logic=8.0, evidence=7.5, persuasion=7.5, counter=7.0),
    TurnScore(logic=8.5, evidence=7.0, persuasion=8.0, counter=7.5),
    TurnScore(logic=7.0, evidence=8.0, persuasion=7.5, counter=8.0),
]


def _reply(lines: list[str], idx: int, opp_name: str) -> DebaterReply:
    text = lines[idx % len(lines)]
    return DebaterReply(
        argument=text, confidence=0.85,
        attack_points=[f"Countering {opp_name}'s narrative"],
        defense_points=["Statistical evidence supports this claim"],
        citations=[f"https://en.wikipedia.org/wiki/{opp_name.replace(' ', '_')}"],
        references_opponent=f"Directly addressing {opp_name}'s previous argument",
    )


class DemoDebater:
    def __init__(self, lines: list[str], opp_name: str) -> None:
        self._lines, self._opp = lines, opp_name
        self._idx = 0

    def respond(self, _envelope: JudgeEnvelope) -> DebaterReply:
        reply = _reply(self._lines, self._idx, self._opp)
        self._idx += 1
        return reply


class DemoJudge:
    def __init__(self) -> None:
        self._idx = 0

    def relay(self, *, sender: str, recipient: str, kind: EnvelopeKind,
              payload: dict, round_index: int) -> JudgeEnvelope:
        return JudgeEnvelope(
            round=round_index, kind=kind, sender=sender,
            recipient=recipient, payload=payload,
        )

    def score_turn(self, _reply: DebaterReply) -> TurnScore:
        scores = _SCORES_A if self._idx % 2 == 0 else _SCORES_B
        score = scores[(self._idx // 2) % len(scores)]
        self._idx += 1
        return score

    def verdict(self, scoreboard: ScoreAggregate) -> Verdict:
        return Verdict(
            winner="debater-a", score_a=scoreboard.total_a() + 2,
            score_b=scoreboard.total_b(),
            reasoning="Messi demonstrated superior rhetorical range, weaving statistical evidence "
            "with emotional narrative across multiple dimensions of football excellence.",
            rubric_breakdown={
                "debater-a": RubricBreakdown(logic=41, evidence=38.5, persuasion=43, counter=38),
                "debater-b": RubricBreakdown(logic=39, evidence=39, persuasion=37.5, counter=38),
            },
        )
