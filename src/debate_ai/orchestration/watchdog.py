"""Watchdog — timeout + keep-alive for agent API calls.

Wraps every agent call in a ``ThreadPoolExecutor`` future with a hard
timeout. If the call stalls, the watchdog cancels it and optionally
restarts the agent. Per ``config/setup.json::watchdog``.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from debate_ai.models.config_models import WatchdogConfig
from debate_ai.shared.exceptions import AgentUnrecoverableError, WatchdogTimeoutError
from debate_ai.shared.logger import FifoLogger


class Watchdog:
    """Wrap agent calls with timeout and restart tracking."""

    def __init__(self, cfg: WatchdogConfig, logger: FifoLogger) -> None:
        self.cfg = cfg
        self.logger = logger
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="wd")
        self._restart_counts: dict[str, int] = {}
        self._lock = threading.Lock()

    def call_with_timeout(
        self,
        agent_role: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run *fn* in a thread with the configured timeout."""
        future: Future = self._executor.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=self.cfg.timeout_s_per_call)
        except TimeoutError as exc:
            future.cancel()
            self.logger.log(
                "WARN",
                source="watchdog",
                kind="timeout",
                agent=agent_role,
                timeout_s=self.cfg.timeout_s_per_call,
            )
            raise WatchdogTimeoutError(f"{agent_role} timed out") from exc

    def record_restart(self, agent_role: str) -> None:
        """Bump restart count; raise if limit exceeded."""
        with self._lock:
            count = self._restart_counts.get(agent_role, 0) + 1
            self._restart_counts[agent_role] = count
        if count > self.cfg.max_restarts_per_agent:
            raise AgentUnrecoverableError(
                f"{agent_role} exceeded max restarts ({self.cfg.max_restarts_per_agent})"
            )
        self.logger.log("WARN", source="watchdog", kind="restart", agent=agent_role, count=count)

    def restart_count(self, agent_role: str) -> int:
        with self._lock:
            return self._restart_counts.get(agent_role, 0)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
