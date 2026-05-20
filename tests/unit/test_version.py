"""Tests for ``shared.version``."""

from __future__ import annotations

import pytest

from debate_ai.shared.exceptions import ConfigVersionError
from debate_ai.shared.version import (
    CODE_VERSION,
    assert_config_version,
    code_version_tuple,
)


def test_code_version_is_set_to_one_zero() -> None:
    assert CODE_VERSION == "1.00"


def test_code_version_tuple_parses() -> None:
    assert code_version_tuple() == (1, 0)


def test_assert_config_version_match_returns_none() -> None:
    assert assert_config_version("setup", "1.00", "1.00") is None


def test_assert_config_version_mismatch_raises() -> None:
    with pytest.raises(ConfigVersionError) as exc:
        assert_config_version("setup", "0.99", "1.00")
    assert "setup" in str(exc.value)
    assert "0.99" in str(exc.value)
    assert "1.00" in str(exc.value)
