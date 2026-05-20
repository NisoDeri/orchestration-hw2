"""Tiny formatting helpers reused across CLI menu + log records.

Kept dependency-free so any layer can import without dragging models in.
"""

from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    """UTC timestamp in ISO 8601 with millisecond precision."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def truncate(text: str, max_chars: int = 200, ellipsis: str = "...") -> str:
    """Cut ``text`` to ``max_chars`` minus the ellipsis length.

    Used by log records and the CLI ``tail`` view so a single huge argument
    doesn't blow out the terminal width.
    """
    if max_chars <= len(ellipsis):
        return ellipsis[:max_chars]
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(ellipsis)] + ellipsis


def percent_bar(value: float, width: int = 10, fill: str = "▓", empty: str = "░") -> str:
    """Render a 0..1 value as a Unicode progress bar.

    Used in the CLI scoreboard panel. ``value`` is clamped into ``[0, 1]``.
    """
    clamped = max(0.0, min(1.0, value))
    filled = int(round(clamped * width))
    return fill * filled + empty * (width - filled)


def two_decimals(value: float) -> str:
    """Format a float with exactly two decimals for scoreboard display."""
    return f"{value:.2f}"
