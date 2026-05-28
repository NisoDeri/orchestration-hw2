"""Tests for ``services.scoring_service``."""

from __future__ import annotations

from debate_ai.constants import EnvelopeKind
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.message_models import DebaterReply, JudgeEnvelope, TurnScore
from debate_ai.services.scoring_service import ScoringService


def _reply(
    arg: str = "Strong claim with citation.",
    refs: str = "you said X",
    attack: list[str] | None = None,
) -> DebaterReply:
    return DebaterReply(
        argument="x" * 30 + " " + arg,
        confidence=0.7,
        attack_points=["counter-point"] if attack is None else attack,
        defense_points=["defense"],
        citations=["https://example.com"],
        references_opponent=refs,
    )


def _env(sender: str, payload: dict, round_idx: int = 1) -> JudgeEnvelope:
    return JudgeEnvelope(
        round=round_idx,
        kind=EnvelopeKind.REBUTTAL,
        sender=sender,
        recipient="judge",
        payload=payload,
    )


def test_lie_catch_bonus_floors_persuasion() -> None:
    svc = ScoringService(agreement_keywords=["yes,"], drift_window_turns=2)
    opp = _reply(arg="opponent says something wrong", refs="prior")
    me = _reply(refs="opponent says something wrong", attack=["attack"])
    score = TurnScore(logic=5, evidence=5, persuasion=5, counter=5)
    bumped = svc.apply_lie_catch_bonus(score, me, [opp])
    assert bumped.persuasion > score.persuasion


def test_lie_catch_bonus_no_change_without_attacks() -> None:
    svc = ScoringService(agreement_keywords=[], drift_window_turns=2)
    opp = _reply(arg="opponent says X")
    me = _reply(refs="opponent says X", attack=[])
    score = TurnScore(logic=5, evidence=5, persuasion=5, counter=5)
    assert svc.apply_lie_catch_bonus(score, me, [opp]) == score


def test_lie_catch_no_opponent_history() -> None:
    svc = ScoringService(agreement_keywords=[], drift_window_turns=2)
    me = _reply(attack=["x"])
    score = TurnScore(logic=5, evidence=5, persuasion=5, counter=5)
    assert svc.apply_lie_catch_bonus(score, me, []) == score


def test_detect_drift_true_when_agreement_sustained() -> None:
    svc = ScoringService(agreement_keywords=["yes,", "agreed"], drift_window_turns=2)
    mem = ConversationMemory("d1", "motion")
    mem.append(
        _env("debater-a", {"references_opponent": "yes, you are right", "argument": "I agree"})
    )
    mem.append(_env("debater-b", {"references_opponent": "agreed, exactly", "argument": "totally"}))
    assert svc.detect_drift(mem)


def test_detect_drift_false_when_only_one_turn_agrees() -> None:
    svc = ScoringService(agreement_keywords=["yes,"], drift_window_turns=2)
    mem = ConversationMemory("d1", "motion")
    mem.append(
        _env("debater-a", {"references_opponent": "yes, you are right", "argument": "I agree"})
    )
    mem.append(_env("debater-b", {"references_opponent": "no", "argument": "wrong because..."}))
    assert not svc.detect_drift(mem)


def test_detect_drift_false_when_window_unfilled() -> None:
    svc = ScoringService(agreement_keywords=["yes,"], drift_window_turns=3)
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", {"references_opponent": "yes,", "argument": "ok"}))
    assert not svc.detect_drift(mem)


def test_aggregate_score_sums_correctly() -> None:
    svc = ScoringService(agreement_keywords=[], drift_window_turns=2)
    history = [
        ("debater-a", TurnScore(logic=8, evidence=7, persuasion=9, counter=6)),
        ("debater-b", TurnScore(logic=7, evidence=8, persuasion=7, counter=8)),
    ]
    agg = svc.aggregate_score(history)
    assert agg.total_a() == 30
    assert agg.total_b() == 30
