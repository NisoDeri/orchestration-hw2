"""Tests for ``utils.formatting`` + ``utils.validators``."""

from __future__ import annotations

from debate_ai.utils.formatting import now_iso, percent_bar, truncate, two_decimals
from debate_ai.utils.validators import (
    contains_any,
    is_hex_color,
    is_non_empty_list,
    is_valid_url,
)


def test_now_iso_has_t_and_z_or_offset() -> None:
    stamp = now_iso()
    assert "T" in stamp
    assert stamp.endswith("+00:00") or stamp.endswith("Z")


def test_truncate_short_input_returns_input() -> None:
    assert truncate("hello", max_chars=200) == "hello"


def test_truncate_long_input_adds_ellipsis() -> None:
    out = truncate("x" * 50, max_chars=10)
    assert out.endswith("...")
    assert len(out) == 10


def test_percent_bar_full() -> None:
    assert percent_bar(1.0, width=5).count("▓") == 5


def test_percent_bar_empty() -> None:
    assert percent_bar(0.0, width=5).count("░") == 5


def test_percent_bar_clamps() -> None:
    assert percent_bar(2.0, width=5) == percent_bar(1.0, width=5)
    assert percent_bar(-0.5, width=5) == percent_bar(0.0, width=5)


def test_two_decimals_pads() -> None:
    assert two_decimals(7) == "7.00"
    assert two_decimals(7.4) == "7.40"


def test_is_valid_url_accepts_https() -> None:
    assert is_valid_url("https://example.com/path") is True


def test_is_valid_url_rejects_garbage() -> None:
    assert is_valid_url("not a url") is False
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("") is False


def test_is_non_empty_list_truthy() -> None:
    assert is_non_empty_list([1])
    assert is_non_empty_list(["a", "b"])


def test_is_non_empty_list_falsy() -> None:
    assert not is_non_empty_list([])
    assert not is_non_empty_list("not a list")
    assert not is_non_empty_list(None)


def test_is_hex_color_accepts_canonical() -> None:
    assert is_hex_color("#7B1E3B")
    assert is_hex_color("#abcdef")


def test_is_hex_color_rejects() -> None:
    assert not is_hex_color("7B1E3B")
    assert not is_hex_color("#7B1E3")
    assert not is_hex_color("#7B1E3BG")


def test_contains_any_case_insensitive() -> None:
    assert contains_any("Yes, that's true", ["yes,"])
    assert contains_any("I AGREE COMPLETELY", ["agreed", "agree"])


def test_contains_any_no_match() -> None:
    assert not contains_any("nope nothing here", ["correct,", "true,"])
