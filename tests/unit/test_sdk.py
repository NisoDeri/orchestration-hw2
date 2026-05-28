"""Tests for ``sdk.sdk``."""

from __future__ import annotations

from pathlib import Path

import pytest

from debate_ai.sdk.sdk import get_config, list_personas

_CONFIG = Path(__file__).parents[2] / "config"


def test_get_config_returns_dict() -> None:
    cfg = get_config(_CONFIG)
    assert "motion" in cfg
    assert "pings_per_side" in cfg
    assert cfg["pings_per_side"] == 10


def test_list_personas_returns_names() -> None:
    names = list_personas(_CONFIG)
    assert "messi" in names
    assert "ronaldo" in names


def test_run_debate_needs_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from debate_ai.sdk.sdk import _make_client

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        _make_client()
