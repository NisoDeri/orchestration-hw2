"""Tests for ``models.message_models``."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from debate_ai.constants import EnvelopeKind
from debate_ai.models.message_models import (
    CommentaryReply,
    CrowdReply,
    DebaterReply,
    FactCheckReply,
    FactClaimAnnotation,
    JudgeEnvelope,
    RubricBreakdown,
    TurnScore,
    UIEvent,
    Verdict,
)


def _debater_reply(**overrides) -> dict:
    base = {
        "argument": "Messi's eight Ballon d'Ors plus the 2022 World Cup are decisive.",
        "confidence": 0.8,
        "attack_points": ["Champions League is a club competition"],
        "defense_points": ["Eight Ballon d'Ors"],
        "citations": ["https://francefootball.fr/article"],
        "references_opponent": "you claimed Ronaldo's longevity proves greatness",
    }
    base.update(overrides)
    return base


def test_debater_reply_valid() -> None:
    DebaterReply.model_validate(_debater_reply())


def test_debater_reply_rejects_empty_citations() -> None:
    with pytest.raises(ValidationError):
        DebaterReply.model_validate(_debater_reply(citations=[]))


def test_debater_reply_rejects_empty_references_opponent() -> None:
    with pytest.raises(ValidationError):
        DebaterReply.model_validate(_debater_reply(references_opponent=""))


def test_debater_reply_confidence_range() -> None:
    with pytest.raises(ValidationError):
        DebaterReply.model_validate(_debater_reply(confidence=1.5))


def test_commentary_reply_valid() -> None:
    CommentaryReply.model_validate({
        "commentary": "Ronaldo just landed a haymaker on the CL run.",
        "tone": "favouring_b", "round_ref": 3,
    })


def test_crowd_reply_emoji_count() -> None:
    with pytest.raises(ValidationError):
        CrowdReply.model_validate({
            "envelope_ref": "e1", "emojis": [], "one_liner": "wow", "lean": 0.0,
        })
    with pytest.raises(ValidationError):
        CrowdReply.model_validate({
            "envelope_ref": "e1", "emojis": ["🔥"] * 6, "one_liner": "ok", "lean": 0.0,
        })


def test_crowd_reply_lean_range() -> None:
    with pytest.raises(ValidationError):
        CrowdReply.model_validate({
            "envelope_ref": "e1", "emojis": ["🔥"], "one_liner": "wow", "lean": 2.0,
        })


def test_factcheck_reply_multi_claim() -> None:
    reply = FactCheckReply.model_validate({
        "envelope_ref": "e1",
        "claims": [
            {"quote": "8 BdO", "verdict": "correct", "severity": 0.1,
             "source_kind": "facts_json", "source_ref": "facts.json#ballon_dor_count_messi"},
            {"quote": "5 CL", "verdict": "incorrect", "severity": 0.6, "actual": "4 CL",
             "source_kind": "facts_json"},
        ],
    })
    assert len(reply.claims) == 2
    assert isinstance(reply.claims[0], FactClaimAnnotation)


def test_turn_score_total() -> None:
    assert TurnScore(logic=8, evidence=7, persuasion=9, counter=6).total() == 30.0


def test_verdict_rejects_tie() -> None:
    payload = {
        "winner": "debater-a", "score_a": 70.0, "score_b": 70.0,
        "reasoning": "x" * 40,
        "rubric_breakdown": {"debater-a": _rb(), "debater-b": _rb()},
    }
    with pytest.raises(ValidationError):
        Verdict.model_validate(payload)


def test_verdict_winner_must_match_scores() -> None:
    payload = {
        "winner": "debater-b", "score_a": 80.0, "score_b": 70.0,
        "reasoning": "x" * 40,
        "rubric_breakdown": {"debater-a": _rb(), "debater-b": _rb()},
    }
    with pytest.raises(ValidationError):
        Verdict.model_validate(payload)


def test_verdict_valid() -> None:
    Verdict.model_validate({
        "winner": "debater-a", "score_a": 80.0, "score_b": 70.0,
        "reasoning": "x" * 40,
        "rubric_breakdown": {"debater-a": _rb(), "debater-b": _rb()},
    })


def test_envelope_requires_nonempty_sender_recipient() -> None:
    with pytest.raises(ValidationError):
        JudgeEnvelope.model_validate({
            "round": 1, "kind": EnvelopeKind.REBUTTAL, "sender": "  ", "recipient": "x",
            "payload": {},
        })


def test_envelope_valid() -> None:
    env = JudgeEnvelope.model_validate({
        "round": 2, "kind": EnvelopeKind.REBUTTAL,
        "sender": "debater-a", "recipient": "debater-b", "payload": {"argument": "x"},
    })
    assert env.envelope_id  # auto-generated


def test_ui_event_basic() -> None:
    ev = UIEvent.model_validate({
        "debate_id": "d1", "seq": 0, "kind": "debate_started", "payload": {},
    })
    assert ev.kind == "debate_started"


def _rb() -> dict:
    return RubricBreakdown(logic=20, evidence=20, persuasion=20, counter=20).model_dump()
