"""Tests for ``orchestration.watchdog``."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from debate_ai.models.config_models import WatchdogConfig
from debate_ai.orchestration.watchdog import Watchdog
from debate_ai.shared.exceptions import AgentUnrecoverableError, WatchdogTimeoutError
from debate_ai.shared.logger import FifoLogger


def _cfg(timeout: float = 2.0, restarts: int = 2) -> WatchdogConfig:
    return WatchdogConfig(
        timeout_s_per_call=timeout,
        max_restarts_per_agent=restarts,
        keepalive_interval_s=5,
        on_unrecoverable="skip",
    )


def _logger() -> FifoLogger:
    return MagicMock(spec=FifoLogger)


def test_call_succeeds() -> None:
    wd = Watchdog(_cfg(), _logger())
    result = wd.call_with_timeout("judge", lambda: 42)
    assert result == 42
    wd.shutdown()


def test_call_timeout() -> None:
    wd = Watchdog(_cfg(timeout=0.1), _logger())
    with pytest.raises(WatchdogTimeoutError):
        wd.call_with_timeout("judge", time.sleep, 5)
    wd.shutdown()


def test_restart_count() -> None:
    wd = Watchdog(_cfg(restarts=2), _logger())
    wd.record_restart("judge")
    assert wd.restart_count("judge") == 1
    wd.record_restart("judge")
    assert wd.restart_count("judge") == 2
    with pytest.raises(AgentUnrecoverableError):
        wd.record_restart("judge")
    wd.shutdown()


def test_restart_independent_per_agent() -> None:
    wd = Watchdog(_cfg(restarts=1), _logger())
    wd.record_restart("judge")
    wd.record_restart("debater-a")
    assert wd.restart_count("judge") == 1
    assert wd.restart_count("debater-a") == 1
    wd.shutdown()
