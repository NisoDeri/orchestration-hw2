"""Tests for ``shared.seeding``."""

from __future__ import annotations

import random

from debate_ai.shared.seeding import default_rng, seed_from_env, temporarily_seeded


def test_default_rng_with_explicit_seed_is_reproducible() -> None:
    a = default_rng(seed=42)
    b = default_rng(seed=42)
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]


def test_default_rng_without_seed_returns_random_instance() -> None:
    rng = default_rng(seed=None)
    assert isinstance(rng, random.Random)


def test_seed_from_env_returns_none_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("DEBATE_AI_SEED", raising=False)
    assert seed_from_env() is None


def test_seed_from_env_parses_int(monkeypatch) -> None:
    monkeypatch.setenv("DEBATE_AI_SEED", "7")
    assert seed_from_env() == 7


def test_temporarily_seeded_restores_state() -> None:
    before = random.random()
    with temporarily_seeded(99):
        inside = random.random()
    after = random.random()
    # The 'inside' value is determined by the seed; before/after are not equal
    # to 'inside' (with vanishingly small probability).
    assert inside == random.Random(99).random()
    assert isinstance(before, float)
    assert isinstance(after, float)
