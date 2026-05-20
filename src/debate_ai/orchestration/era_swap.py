"""Era-swap mechanism — forces debaters to argue as historical versions.

During the era-swap round, each debater receives an ``Era`` overlay that
shifts their persona to a specific historical period (e.g. "2009 Messi"
or "2014 Ronaldo"). The strategy for choosing eras is config-driven.
"""

from __future__ import annotations

import random

from debate_ai.models.persona_models import Era, Persona


def pick_era(persona: Persona, strategy: str) -> Era | None:
    """Select an era for the given persona based on strategy."""
    if not persona.has_eras():
        return None
    eras = persona.eras
    if strategy == "first":
        return eras[0]
    if strategy == "latest":
        return eras[-1]
    if strategy == "random":
        return random.choice(eras)  # noqa: S311
    if strategy == "contrasting":
        return _pick_contrasting(eras)
    return eras[0]


def _pick_contrasting(eras: list[Era]) -> Era:
    """Pick the most 'historical' era — first in the list by convention."""
    return eras[0]


def apply_era_swap(
    persona_a: Persona, persona_b: Persona, strategy: str,
) -> tuple[Era | None, Era | None]:
    """Return (era_a, era_b) for the era-swap round."""
    return pick_era(persona_a, strategy), pick_era(persona_b, strategy)
