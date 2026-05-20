"""Event emitter — broadcasts UIEvents to subscribers.

Both the CLI watch loop and the HTML SSE endpoint subscribe here. The
emitter is thread-safe; events are appended to a list and pushed to
registered callbacks.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from debate_ai.models.message_models import UIEvent


class EventEmitter:
    """Publish UIEvents to zero-or-more subscribers."""

    def __init__(self, debate_id: str) -> None:
        self.debate_id = debate_id
        self._subscribers: list[Callable[[UIEvent], None]] = []
        self._events: list[UIEvent] = []
        self._lock = threading.Lock()
        self._seq = 0

    def subscribe(self, callback: Callable[[UIEvent], None]) -> None:
        with self._lock:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[UIEvent], None]) -> None:
        with self._lock:
            self._subscribers = [s for s in self._subscribers if s is not callback]

    def emit(self, kind: str, payload: dict[str, Any] | None = None) -> UIEvent:
        """Create, store, and broadcast a UIEvent."""
        with self._lock:
            event = UIEvent(
                debate_id=self.debate_id, seq=self._seq,
                kind=kind, payload=payload or {},
            )
            self._events.append(event)
            self._seq += 1
            subs = list(self._subscribers)
        for cb in subs:
            cb(event)
        return event

    def history(self) -> list[UIEvent]:
        with self._lock:
            return list(self._events)

    def event_count(self) -> int:
        with self._lock:
            return len(self._events)
