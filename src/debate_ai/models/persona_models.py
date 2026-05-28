"""Persona + era Pydantic models.

A persona is a swap-out: ``Messi``, ``Ronaldo``, ``Python``, ``JavaScript``
all share the same shape. Loaded from ``config/personas/<name>.json``.
Each persona declares ≥ 0 era variants used by the era-swap round mechanism.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Era(BaseModel):
    """One historical variant of a persona.

    For the era-swap round, the orchestrator picks one ``Era`` per persona
    and the debater's system prompt is extended with ``system_addendum``.
    """

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, max_length=32)
    system_addendum: str = Field(..., min_length=1)


class SkillOverrides(BaseModel):
    """Persona-specific extra instructions appended to its skill bundle."""

    model_config = ConfigDict(extra="allow")

    extra_instructions: list[str] = Field(default_factory=list)


class Persona(BaseModel):
    """A debater persona — name, system prompt, style, eras, UI color."""

    model_config = ConfigDict(extra="allow")

    version: str = Field(..., pattern=r"^\d+\.\d+$")
    name: str = Field(..., min_length=1, max_length=32)
    display_name: str = Field(..., min_length=1, max_length=64)
    color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    system_prompt: str = Field(..., min_length=20)
    style_notes: list[str] = Field(default_factory=list)
    eras: list[Era] = Field(default_factory=list)
    skill_overrides: SkillOverrides = Field(default_factory=SkillOverrides)

    @field_validator("eras")
    @classmethod
    def _era_labels_unique(cls, value: list[Era]) -> list[Era]:
        """Reject persona files that declare two eras with the same label."""
        labels = [e.label for e in value]
        if len(labels) != len(set(labels)):
            raise ValueError("Persona.eras: duplicate era labels detected")
        return value

    def has_eras(self) -> bool:
        """True iff at least one era variant exists (era-swap eligible)."""
        return len(self.eras) > 0

    def find_era(self, label: str) -> Era | None:
        """Return the era with the matching label or ``None``."""
        for era in self.eras:
            if era.label == label:
                return era
        return None

    def as_loggable(self) -> dict[str, Any]:
        """Trim fields not safe / useful in log records (system_prompt is huge)."""
        return {
            "name": self.name,
            "color_hex": self.color_hex,
            "eras": [e.label for e in self.eras],
        }
