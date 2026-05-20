"""Tests for ``shared.exceptions``."""

from __future__ import annotations

from debate_ai.shared.exceptions import (
    AgentUnrecoverableError,
    CitationError,
    ConfigError,
    ConfigVersionError,
    CostCapExceededError,
    DebateAIError,
    RouteError,
    SchemaError,
    VerdictTieError,
    WatchdogTimeoutError,
)


def test_all_inherit_from_base() -> None:
    for sub in (
        ConfigError,
        ConfigVersionError,
        SchemaError,
        CitationError,
        RouteError,
        CostCapExceededError,
        AgentUnrecoverableError,
        VerdictTieError,
        WatchdogTimeoutError,
    ):
        assert issubclass(sub, DebateAIError), sub


def test_config_version_error_is_subclass_of_config_error() -> None:
    assert issubclass(ConfigVersionError, ConfigError)


def test_citation_error_is_subclass_of_schema_error() -> None:
    assert issubclass(CitationError, SchemaError)


def test_raise_and_catch_via_base() -> None:
    import pytest

    with pytest.raises(DebateAIError):
        raise CostCapExceededError("test")
