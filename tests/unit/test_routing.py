"""Tests for ``orchestration.routing``."""

from __future__ import annotations

import pytest

from debate_ai.constants import EnvelopeKind
from debate_ai.orchestration.routing import (
    is_round_complete,
    next_recipient,
    opponent_of,
    validate_route,
)
from debate_ai.shared.exceptions import RouteError


def test_debater_to_judge_valid() -> None:
    validate_route("debater-a", "judge")


def test_debater_to_debater_raises() -> None:
    with pytest.raises(RouteError):
        validate_route("debater-a", "debater-b")


def test_support_to_judge_valid() -> None:
    validate_route("commentator", "judge")


def test_support_to_debater_raises() -> None:
    with pytest.raises(RouteError):
        validate_route("crowd", "debater-a")


def test_opponent_of_a() -> None:
    assert opponent_of("debater-a") == "debater-b"


def test_opponent_of_b() -> None:
    assert opponent_of("debater-b") == "debater-a"


def test_opponent_of_invalid() -> None:
    with pytest.raises(RouteError):
        opponent_of("judge")


def test_next_recipient_a_sends() -> None:
    result = next_recipient("debater-a", EnvelopeKind.REBUTTAL, 1, 10)
    assert result == "debater-b"


def test_next_recipient_b_sends() -> None:
    result = next_recipient("debater-b", EnvelopeKind.REBUTTAL, 1, 10)
    assert result == "debater-a"


def test_next_recipient_judge_opening() -> None:
    result = next_recipient("judge", EnvelopeKind.OPENING, 0, 10)
    assert result == "debater-a"


def test_next_recipient_unknown_raises() -> None:
    with pytest.raises(RouteError):
        next_recipient("crowd", EnvelopeKind.REBUTTAL, 1, 10)


def test_round_complete() -> None:
    assert is_round_complete(1, 1)
    assert not is_round_complete(0, 1)
    assert not is_round_complete(1, 0)
