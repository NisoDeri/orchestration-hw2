"""Tests for ``models.persona_models``."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from debate_ai.models.persona_models import Era, Persona


def _minimal_persona_dict() -> dict:
    return {
        "version": "1.00",
        "name": "Messi",
        "display_name": "Lionel Messi",
        "color_hex": "#7B1E3B",
        "system_prompt": "x" * 30,
        "style_notes": [],
        "eras": [],
    }


def test_persona_loads_minimal() -> None:
    p = Persona.model_validate(_minimal_persona_dict())
    assert p.name == "Messi"
    assert p.has_eras() is False


def test_persona_with_eras_distinct_labels() -> None:
    d = _minimal_persona_dict()
    d["eras"] = [
        {"label": "2009", "system_addendum": "young"},
        {"label": "2022", "system_addendum": "veteran"},
    ]
    p = Persona.model_validate(d)
    assert p.has_eras()
    assert p.find_era("2009") is not None
    assert p.find_era("9999") is None


def test_persona_duplicate_era_labels_rejected() -> None:
    d = _minimal_persona_dict()
    d["eras"] = [
        {"label": "2009", "system_addendum": "a"},
        {"label": "2009", "system_addendum": "b"},
    ]
    with pytest.raises(ValidationError) as exc:
        Persona.model_validate(d)
    assert "duplicate era labels" in str(exc.value)


def test_persona_rejects_bad_color() -> None:
    d = _minimal_persona_dict()
    d["color_hex"] = "not-a-color"
    with pytest.raises(ValidationError):
        Persona.model_validate(d)


def test_persona_version_must_match_pattern() -> None:
    d = _minimal_persona_dict()
    d["version"] = "1"
    with pytest.raises(ValidationError):
        Persona.model_validate(d)


def test_as_loggable_drops_system_prompt() -> None:
    d = _minimal_persona_dict()
    p = Persona.model_validate(d)
    payload = p.as_loggable()
    assert "system_prompt" not in payload
    assert payload["name"] == "Messi"


def test_era_requires_nonempty_strings() -> None:
    with pytest.raises(ValidationError):
        Era.model_validate({"label": "", "system_addendum": "x"})
    with pytest.raises(ValidationError):
        Era.model_validate({"label": "2009", "system_addendum": ""})
