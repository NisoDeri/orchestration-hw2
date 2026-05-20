"""Tiny pure validators.

Used by Pydantic field validators and ad-hoc checks. Each function is one
liner-level decision; no side effects, no I/O.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

_HEX_COLOR_RX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def is_valid_url(value: str) -> bool:
    """Loose URL check — has a scheme in {http, https} and a non-empty netloc."""
    try:
        parsed = urlparse(value)
    except (ValueError, AttributeError):
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_non_empty_list(value: object) -> bool:
    """True iff ``value`` is a list with at least one element."""
    return isinstance(value, list) and len(value) > 0


def is_hex_color(value: str) -> bool:
    """``#RRGGBB`` 6-digit hex check (case-insensitive)."""
    return bool(_HEX_COLOR_RX.match(value))


def contains_any(text: str, needles: list[str], case_insensitive: bool = True) -> bool:
    """True iff ``text`` contains any string from ``needles``.

    Used by the drift detector to spot agreement keywords.
    """
    haystack = text.lower() if case_insensitive else text
    return any((n.lower() if case_insensitive else n) in haystack for n in needles)
