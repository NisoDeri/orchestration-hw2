"""Deterministic RNG seeding for reproducible tests.

The era-swap picker and the Crowd agent's lean both use randomness. Tests
pin the seed via this module; production code calls ``default_rng()`` without
a seed.
"""

from __future__ import annotations

import os
import random
from collections.abc import Iterator
from contextlib import contextmanager


def seed_from_env(env_var: str = "DEBATE_AI_SEED") -> int | None:
    """Return the seed declared in the env, or ``None`` for non-deterministic mode.

    Production runs leave the env var unset; CI / tests set it to make era-swap
    picks deterministic.
    """
    raw = os.environ.get(env_var)
    if raw is None:
        return None
    return int(raw)


def default_rng(seed: int | None = None) -> random.Random:
    """Build a ``random.Random`` instance. Seed precedence: arg > env > None."""
    effective = seed if seed is not None else seed_from_env()
    rng = random.Random()
    if effective is not None:
        rng.seed(effective)
    return rng


@contextmanager
def temporarily_seeded(seed: int) -> Iterator[None]:
    """Pin the global ``random`` seed for the duration of a ``with`` block.

    Used in tests that touch code which calls ``random.choice`` directly
    rather than through a passed-in ``Random`` instance.
    """
    state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(state)
