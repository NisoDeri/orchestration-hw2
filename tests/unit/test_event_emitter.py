"""Tests for ``orchestration.event_emitter``."""

from __future__ import annotations

from debate_ai.orchestration.event_emitter import EventEmitter


def test_emit_increments_seq() -> None:
    ee = EventEmitter("d1")
    e1 = ee.emit("debate_started", {"motion": "Messi vs Ronaldo"})
    e2 = ee.emit("round_changed", {"round": 0})
    assert e1.seq == 0
    assert e2.seq == 1


def test_history_accumulates() -> None:
    ee = EventEmitter("d1")
    ee.emit("debate_started")
    ee.emit("round_changed")
    assert ee.event_count() == 2
    assert len(ee.history()) == 2


def test_subscribe_callback() -> None:
    ee = EventEmitter("d1")
    received = []
    ee.subscribe(lambda ev: received.append(ev))
    ee.emit("debate_started")
    assert len(received) == 1
    assert received[0].kind == "debate_started"


def test_unsubscribe() -> None:
    ee = EventEmitter("d1")
    received = []
    cb = lambda ev: received.append(ev)  # noqa: E731
    ee.subscribe(cb)
    ee.emit("debate_started")
    ee.unsubscribe(cb)
    ee.emit("round_changed")
    assert len(received) == 1


def test_debate_id_set() -> None:
    ee = EventEmitter("my-debate")
    ev = ee.emit("debate_started")
    assert ev.debate_id == "my-debate"
