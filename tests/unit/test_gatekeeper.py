"""Tests for ``shared.gatekeeper.Gatekeeper``."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from debate_ai.models.config_models import RateLimitsConfig
from debate_ai.shared.exceptions import CostCapExceededError
from debate_ai.shared.gatekeeper import Gatekeeper
from debate_ai.shared.logger import FifoLogger


def _limits(max_cost: float = 10.0, max_retries: int = 2) -> RateLimitsConfig:
    return RateLimitsConfig.model_validate(
        {
            "version": "1.00",
            "web_search_provider": "anthropic_builtin",
            "anthropic": {
                "max_requests_per_second": 1000.0,
                "max_concurrent": 4,
                "queue_max_depth": 64,
                "queue_max_block_s": 5.0,
            },
            "retry_policy": {
                "max_retries": max_retries,
                "backoff_base_s": 0.01,
                "backoff_factor": 2.0,
                "backoff_max_s": 0.05,
                "retry_on_status": [500],
            },
            "cost_caps": {"max_cost_usd_per_debate": max_cost, "search_cost_usd_per_use": 0.01},
            "pricing_usd_per_1m_tokens": {
                "claude-opus-4-7": {"input": 15.0, "output": 75.0},
                "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
                "claude-haiku-4-5-20251001": {"input": 0.8, "output": 4.0},
            },
        }
    )


def _gk(tmp_path: Path, **kwargs) -> Gatekeeper:
    lg = FifoLogger(tmp_path / "logs", max_files=5, lines_per_file=100)
    return Gatekeeper(_limits(**kwargs), lg)


def test_call_returns_function_result(tmp_path: Path) -> None:
    gk = _gk(tmp_path)
    fn = MagicMock(return_value=MagicMock(usage=MagicMock(input_tokens=10, output_tokens=5)))
    result = gk.call(fn, model="claude-opus-4-7", source="t")
    assert result is fn.return_value
    fn.assert_called_once()


def test_call_tracks_cost(tmp_path: Path) -> None:
    gk = _gk(tmp_path)
    response = MagicMock(usage=MagicMock(input_tokens=1_000_000, output_tokens=1_000_000))
    gk.call(lambda **_: response, model="claude-opus-4-7", source="t")
    # opus-4-7: $15 in + $75 out per 1M  = $90.
    assert gk.cost_so_far_usd() == pytest.approx(90.0, abs=0.001)


def test_call_retries_on_exception_then_returns(tmp_path: Path) -> None:
    gk = _gk(tmp_path, max_retries=2)
    response = MagicMock(usage=MagicMock(input_tokens=0, output_tokens=0))
    fn = MagicMock(side_effect=[RuntimeError("boom"), RuntimeError("boom"), response])
    result = gk.call(fn, model="claude-opus-4-7", source="t")
    assert result is response
    assert fn.call_count == 3


def test_call_raises_when_retries_exhausted(tmp_path: Path) -> None:
    gk = _gk(tmp_path, max_retries=1)
    fn = MagicMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        gk.call(fn, model="claude-opus-4-7", source="t")
    assert fn.call_count == 2


def test_record_search_use_adds_cost(tmp_path: Path) -> None:
    gk = _gk(tmp_path)
    gk.record_search_use(count=3)
    assert gk.cost_so_far_usd() == pytest.approx(0.03, abs=0.001)
    assert gk.search_uses_so_far() == 3


def test_cost_cap_raises(tmp_path: Path) -> None:
    gk = _gk(tmp_path, max_cost=0.05)
    gk.record_search_use(count=10)  # 10 * $0.01 = $0.10 > $0.05
    with pytest.raises(CostCapExceededError):
        gk.call(MagicMock(), model="x", source="t")


def test_reset_per_debate_clears_counters(tmp_path: Path) -> None:
    gk = _gk(tmp_path)
    gk.record_search_use(count=5)
    gk.reset_per_debate()
    assert gk.cost_so_far_usd() == 0.0
    assert gk.search_uses_so_far() == 0
