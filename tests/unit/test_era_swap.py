"""Tests for ``orchestration.era_swap``."""

from __future__ import annotations

from debate_ai.models.persona_models import Persona
from debate_ai.orchestration.era_swap import apply_era_swap, pick_era


def _persona(eras: list[dict] | None = None) -> Persona:
    return Persona.model_validate({
        "version": "1.00", "name": "Test", "display_name": "Test Player",
        "color_hex": "#123456",
        "system_prompt": "You argue passionately for the Test side of the debate.",
        "style_notes": ["bold"],
        "eras": [
            {"label": "2009", "system_addendum": "You are 2009."},
            {"label": "2014", "system_addendum": "You are 2014."},
        ] if eras is None else eras,
    })


def test_pick_first() -> None:
    era = pick_era(_persona(), "first")
    assert era is not None
    assert era.label == "2009"


def test_pick_latest() -> None:
    era = pick_era(_persona(), "latest")
    assert era is not None
    assert era.label == "2014"


def test_pick_contrasting() -> None:
    era = pick_era(_persona(), "contrasting")
    assert era is not None
    assert era.label == "2009"


def test_pick_random() -> None:
    era = pick_era(_persona(), "random")
    assert era is not None
    assert era.label in ("2009", "2014")


def test_no_eras_returns_none() -> None:
    p = _persona(eras=[])
    assert pick_era(p, "first") is None


def test_apply_era_swap() -> None:
    pa = _persona()
    pb = _persona()
    era_a, era_b = apply_era_swap(pa, pb, "first")
    assert era_a is not None
    assert era_b is not None
