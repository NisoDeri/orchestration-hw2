"""Tests for ``ui.server`` — basic endpoint checks."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from debate_ai.models.message_models import UIEvent
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.ui.server import app, broadcast, set_emitter


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_index_returns_html(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "Messi vs Ronaldo" in r.text


def test_status_endpoint(client: TestClient) -> None:
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.json()["status"] == "running"


def test_set_emitter_wires_broadcast() -> None:
    emitter = EventEmitter("test-debate")
    set_emitter(emitter)
    ev = emitter.emit("debate_started", {"motion": "test"})
    assert ev.kind == "debate_started"


def test_broadcast_does_not_crash() -> None:
    ev = UIEvent(debate_id="d1", seq=0, kind="debate_started", payload={})
    broadcast(ev)
