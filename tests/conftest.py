"""Shared pytest fixtures.

The most important fixture is ``mock_anthropic_client`` — every unit test that
touches an agent should use it instead of hitting the live API.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Absolute path to ``tests/fixtures/``.

    Tests build canned envelopes / replies / personas under this dir.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Replacement for the Anthropic client used inside ``BaseAgent``.

    Returns a ``MagicMock`` configured so ``client.beta.messages.create(...)``
    returns a response with a single ``tool_use`` block whose ``input`` is
    JSON-decodable. Individual tests override the returned payload.
    """
    client = MagicMock()
    default_payload: dict[str, Any] = {
        "argument": "stub argument",
        "confidence": 0.5,
        "attack_points": ["stub-attack"],
        "defense_points": ["stub-defense"],
        "citations": ["https://example.com"],
        "references_opponent": "stub-opponent-quote",
    }
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=default_payload)]
    response.usage = MagicMock(input_tokens=10, output_tokens=20)
    client.beta.messages.create = MagicMock(return_value=response)
    return client


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Iterator[Path]:
    """Empty config dir tests can populate with minimal JSONs.

    Use this instead of mutating the real ``config/`` directory.
    """
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "personas").mkdir()
    yield cfg


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Tiny test helper — write a JSON file with 2-space indent."""
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
