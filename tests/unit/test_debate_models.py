"""Tests for ``models.debate_models``."""

from __future__ import annotations

import pytest

from debate_ai.constants import RoundKind
from debate_ai.models.debate_models import (
    DebateConfig,
    DebateState,
    Round,
    ScoreAggregate,
)
from debate_ai.models.message_models import TurnScore
from debate_ai.models.persona_models import Persona


def _persona(name: str) -> Persona:
    return Persona.model_validate({
        "version": "1.00", "name": name, "display_name": name,
        "color_hex": "#112233", "system_prompt": "x" * 30,
        "style_notes": [], "eras": [],
    })


def test_round_kind_required() -> None:
    Round.model_validate({"index": 0, "kind": RoundKind.OPENING})


def test_score_aggregate_starts_at_zero() -> None:
    sa = ScoreAggregate()
    assert sa.total_a() == 0
    assert sa.total_b() == 0


def test_score_aggregate_add_turn() -> None:
    sa = ScoreAggregate()
    sa.add_turn("debater-a", TurnScore(logic=8, evidence=7, persuasion=9, counter=6))
    sa.add_turn("debater-b", TurnScore(logic=7, evidence=7, persuasion=7, counter=7))
    assert sa.total_a() == 30
    assert sa.total_b() == 28


def test_score_aggregate_rejects_unknown_debater() -> None:
    with pytest.raises(ValueError, match="unknown debater"):
        ScoreAggregate().add_turn("debater-c", TurnScore(logic=1, evidence=1,
                                                          persuasion=1, counter=1))


def test_winner_from_aggregate_total_decides() -> None:
    sa = ScoreAggregate()
    sa.a_logic = 10
    assert sa.winner_from_aggregate() == "debater-a"
    sa.b_evidence = 20
    assert sa.winner_from_aggregate() == "debater-b"


def test_winner_from_aggregate_truly_tied_falls_back_to_a() -> None:
    # All four axes equal -> total ties -> each tiebreak axis equal too ->
    # documented final fallback is debater-a (deterministic, never tie).
    sa = ScoreAggregate()
    for axis in ("logic", "evidence", "persuasion", "counter"):
        setattr(sa, f"a_{axis}", 5.0)
        setattr(sa, f"b_{axis}", 5.0)
    assert sa.winner_from_aggregate() == "debater-a"


def test_winner_from_aggregate_tiebreak_by_counter_axis() -> None:
    # Totals equal but counter differs -> the axis tiebreak picks the winner.
    sa = ScoreAggregate()
    sa.a_logic, sa.b_logic = 10.0, 5.0
    sa.a_evidence, sa.b_evidence = 5.0, 10.0
    sa.a_persuasion, sa.b_persuasion = 5.0, 10.0
    sa.a_counter, sa.b_counter = 10.0, 5.0
    # totals are 30 vs 30 -> tiebreak by counter -> A wins.
    assert sa.total_a() == sa.total_b()
    assert sa.winner_from_aggregate() == "debater-a"


def test_confidence_a_half_when_zero() -> None:
    assert ScoreAggregate().confidence_a() == 0.5


def test_confidence_a_in_unit_range() -> None:
    sa = ScoreAggregate()
    sa.a_logic = 30
    sa.b_persuasion = 20
    c = sa.confidence_a()
    assert 0 <= c <= 1
    assert c == pytest.approx(30 / 50)


def test_debate_state_round_trip() -> None:
    cfg = DebateConfig.model_validate({
        "motion": "Are dogs better than cats for a first pet?",
        "persona_a": _persona("dog").model_dump(),
        "persona_b": _persona("cat").model_dump(),
        "pings_per_side": 10, "era_swap_round_index": 4,
        "era_swap_strategy": "contrasting",
        "agents_enabled": {"judge": True, "debater_a": True, "debater_b": True,
                           "commentator": False, "crowd": False, "fact_checker": False},
    })
    state = DebateState(cfg=cfg)
    assert state.current_round == 0
    assert state.verdict is None
    assert state.debate_id  # auto-generated
