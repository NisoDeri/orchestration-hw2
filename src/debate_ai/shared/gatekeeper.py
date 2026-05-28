"""Gatekeeper — single chokepoint for every Anthropic call.

Responsibilities (per HW2 brief §8.6 + ``docs/PRD_tools.md`` §5):

- **Rate-limit** outgoing calls (token bucket on requests/sec, semaphore on
  concurrent calls).
- **Retry** transient HTTP failures with exponential backoff.
- **Track cost** from Anthropic response usage + a per-search counter.
- **Enforce cost cap** — raise ``CostCapExceededError`` when the running tally for
  the active debate exceeds the configured ceiling.
- **Log** every call (started + finished) via ``FifoLogger``.

Concurrency model: thread-safe via ``RLock``. The Gatekeeper itself does NOT
manage the worker thread that runs the Anthropic call — that's the Watchdog's
job. The Gatekeeper merely wraps the call.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

from debate_ai.models.config_models import RateLimitsConfig
from debate_ai.shared.exceptions import CostCapExceededError
from debate_ai.shared.logger import FifoLogger


class Gatekeeper:
    """Wrap every outbound Anthropic call with rate limit + retry + cost."""

    def __init__(self, cfg: RateLimitsConfig, logger: FifoLogger) -> None:
        self.cfg = cfg
        self.logger = logger
        self._lock = threading.RLock()
        self._cost_usd = 0.0
        self._search_uses = 0
        self._semaphore = threading.Semaphore(cfg.anthropic.max_concurrent)
        self._min_interval_s = 1.0 / cfg.anthropic.max_requests_per_second
        self._last_call_ts = 0.0

    def call(
        self,
        fn: Callable[..., Any],
        *args: Any,
        model: str = "unknown",
        source: str = "anthropic",
        **kwargs: Any,
    ) -> Any:
        """Run ``fn(*args, **kwargs)`` under the gatekeeper.

        ``model`` is required for cost accounting. ``source`` ends up in log
        records so we can grep for "who called the API".
        """
        self._raise_if_cost_capped()
        attempt = 0
        last_exc: Exception | None = None
        while attempt <= self.cfg.retry_policy.max_retries:
            self._throttle()
            with self._semaphore:
                self.logger.log(
                    "DEBUG",
                    source=source,
                    kind="anthropic_call_started",
                    attempt=attempt,
                    model=model,
                )
                try:
                    response = fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 — we re-raise after retry exhausted
                    last_exc = exc
                    self.logger.log(
                        "WARN",
                        source=source,
                        kind="anthropic_call_failed",
                        attempt=attempt,
                        error=str(exc),
                    )
                    self._backoff(attempt)
                    attempt += 1
                    continue
            self._account(response, model, source)
            return response
        assert last_exc is not None
        raise last_exc

    def record_search_use(self, count: int = 1) -> None:
        """Tick the search counter; the cost is added on each tick."""
        with self._lock:
            self._search_uses += count
            self._cost_usd += count * self.cfg.cost_caps.search_cost_usd_per_use

    def cost_so_far_usd(self) -> float:
        with self._lock:
            return self._cost_usd

    def search_uses_so_far(self) -> int:
        with self._lock:
            return self._search_uses

    def reset_per_debate(self) -> None:
        """Zero the cost + search counters between debates."""
        with self._lock:
            self._cost_usd = 0.0
            self._search_uses = 0

    def _raise_if_cost_capped(self) -> None:
        cap = self.cfg.cost_caps.max_cost_usd_per_debate
        with self._lock:
            if self._cost_usd >= cap:
                raise CostCapExceededError(  # noqa: TRY003
                    f"per-debate cap reached: ${self._cost_usd:.2f} >= ${cap:.2f}"
                )

    def _throttle(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._last_call_ts + self._min_interval_s - now
            if wait > 0:
                time.sleep(wait)
            self._last_call_ts = time.monotonic()

    def _backoff(self, attempt: int) -> None:
        base = self.cfg.retry_policy.backoff_base_s
        factor = self.cfg.retry_policy.backoff_factor
        cap = self.cfg.retry_policy.backoff_max_s
        delay = min(base * (factor**attempt), cap)
        time.sleep(delay)

    def _account(self, response: Any, model: str, source: str) -> None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        input_tok = int(getattr(usage, "input_tokens", 0))
        output_tok = int(getattr(usage, "output_tokens", 0))
        pricing = self.cfg.pricing_usd_per_1m_tokens.get(model)
        if pricing is not None:
            added = (input_tok * pricing.input + output_tok * pricing.output) / 1_000_000.0
            with self._lock:
                self._cost_usd += added
        self.logger.log(
            "DEBUG",
            source=source,
            kind="anthropic_call_finished",
            model=model,
            input_tokens=input_tok,
            output_tokens=output_tok,
            cost_so_far_usd=round(self._cost_usd, 4),
        )
