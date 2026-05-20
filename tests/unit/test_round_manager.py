"""Tests for ``orchestration.round_manager``."""

from __future__ import annotations

from debate_ai.constants import RoundKind
from debate_ai.models.config_models import (
    JudgeConfig,
    ReplayConfig,
    SetupConfig,
    UIConfig,
    WatchdogConfig,
)
from debate_ai.orchestration.round_manager import RoundManager


def _setup(pings: int = 5, era: int | None = 2) -> SetupConfig:
    return SetupConfig(
        version="1.00", pings_per_side=pings, era_swap_round_index=era,
        agents_enabled={"judge": True, "debater_a": True, "debater_b": True},
        watchdog=WatchdogConfig(
            timeout_s_per_call=30, max_restarts_per_agent=2,
            keepalive_interval_s=5, on_unrecoverable="skip",
        ),
        judge=JudgeConfig(verdict_no_tie_retries=1, drift_window_turns=2,
                          agreement_keywords=["agree"]),
        ui=UIConfig(), replay=ReplayConfig(),
    )


def test_opening_round() -> None:
    rm = RoundManager(_setup())
    assert rm.current_kind() == RoundKind.OPENING


def test_closing_round() -> None:
    rm = RoundManager(_setup(pings=3))
    rm._current = 2
    assert rm.current_kind() == RoundKind.CLOSING


def test_era_swap_round() -> None:
    rm = RoundManager(_setup(pings=5, era=2))
    rm._current = 2
    assert rm.current_kind() == RoundKind.ERA_SWAP
    assert rm.is_era_swap_round()


def test_rebuttal_round() -> None:
    rm = RoundManager(_setup(pings=5, era=2))
    rm._current = 1
    assert rm.current_kind() == RoundKind.REBUTTAL


def test_advance_increments() -> None:
    rm = RoundManager(_setup(pings=3))
    assert rm.current_round == 0
    new_idx = rm.advance()
    assert new_idx == 1
    assert rm.current_round == 1


def test_is_debate_over() -> None:
    rm = RoundManager(_setup(pings=3))
    assert not rm.is_debate_over()
    rm._current = 3
    assert rm.is_debate_over()


def test_is_last_round() -> None:
    rm = RoundManager(_setup(pings=3))
    rm._current = 2
    assert rm.is_last_round()
    rm._current = 1
    assert not rm.is_last_round()


def test_no_era_swap_when_disabled() -> None:
    rm = RoundManager(_setup(pings=5, era=None))
    rm._current = 2
    assert not rm.is_era_swap_round()
    assert rm.current_kind() == RoundKind.REBUTTAL
