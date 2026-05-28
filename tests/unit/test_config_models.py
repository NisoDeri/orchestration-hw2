"""Tests for ``models.config_models``."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from debate_ai.models.config_models import (
    AgentModelConfig,
    DebateConfigJson,
    FactClaim,
    FactsConfig,
    LoggingConfig,
    ModelsConfig,
    RateLimitsConfig,
    SetupConfig,
    VersionsConfig,
)

_SETUP = {
    "version": "1.00",
    "pings_per_side": 10,
    "era_swap_round_index": 4,
    "era_swap_strategy": "contrasting",
    "agents_enabled": {
        "judge": True,
        "debater_a": True,
        "debater_b": True,
        "commentator": True,
        "crowd": True,
        "fact_checker": True,
    },
    "watchdog": {
        "timeout_s_per_call": 60.0,
        "max_restarts_per_agent": 3,
        "keepalive_interval_s": 5.0,
        "on_unrecoverable": "force_verdict_from_aggregate",
    },
    "judge": {"verdict_no_tie_retries": 1, "drift_window_turns": 2, "agreement_keywords": ["yes,"]},
    "ui": {"host": "127.0.0.1", "port": 8000, "open_browser_on_start": True},
    "replay": {"dir": "replays", "playback_speed_default": 5.0},
}


def test_setup_config_loads() -> None:
    SetupConfig.model_validate(_SETUP)


def test_setup_config_rejects_too_many_pings() -> None:
    bad = {**_SETUP, "pings_per_side": 999}
    with pytest.raises(ValidationError):
        SetupConfig.model_validate(bad)


def test_debate_config_loads() -> None:
    DebateConfigJson.model_validate(
        {
            "version": "1.00",
            "motion": "Are dogs better than cats?",
            "persona_a": "dog",
            "persona_b": "cat",
        }
    )


def test_models_config_agent_temperature_range() -> None:
    base = {
        "version": "1.00",
        "default_model": "claude-opus-4-7",
        "default_betas": ["skills-2025-10-02"],
        "agents": {
            "judge": {
                "model": "claude-opus-4-7",
                "temperature": 0.5,
                "max_tokens": 1000,
                "skill_id": "x",
                "tools": [],
                "tool_choice": {"type": "auto"},
                "cache_system": True,
            }
        },
    }
    ModelsConfig.model_validate(base)
    bad = {**base, "agents": {"judge": {**base["agents"]["judge"], "temperature": 3.0}}}
    with pytest.raises(ValidationError):
        ModelsConfig.model_validate(bad)


def test_rate_limits_config_loads() -> None:
    RateLimitsConfig.model_validate(
        {
            "version": "1.00",
            "web_search_provider": "anthropic_builtin",
            "anthropic": {
                "max_requests_per_second": 10.0,
                "max_concurrent": 4,
                "queue_max_depth": 64,
                "queue_max_block_s": 30.0,
            },
            "retry_policy": {
                "max_retries": 3,
                "backoff_base_s": 0.5,
                "backoff_factor": 2.0,
                "backoff_max_s": 8.0,
                "retry_on_status": [500, 503],
            },
            "cost_caps": {"max_cost_usd_per_debate": 10.0, "search_cost_usd_per_use": 0.01},
        }
    )


def test_logging_config_loads() -> None:
    LoggingConfig.model_validate(
        {
            "version": "1.00",
            "dir": "logs",
            "max_files": 20,
            "lines_per_file": 500,
            "default_level": "INFO",
            "level_overrides": {},
            "tail_default_n": 100,
        }
    )


def test_facts_config_loads() -> None:
    cfg = FactsConfig.model_validate(
        {
            "version": "1.00",
            "lookup_order": ["facts_json"],
            "claims": {
                "ballon_messi": {
                    "value": 8,
                    "as_of": "2024",
                    "source": "https://x.com",
                    "severity_on_mismatch": 0.6,
                }
            },
            "patterns": [],
        }
    )
    assert isinstance(cfg.claims["ballon_messi"], FactClaim)


def test_versions_config_loads() -> None:
    VersionsConfig.model_validate(
        {
            "version": "1.00",
            "code": "1.00",
            "configs": {"setup": "1.00"},
        }
    )


def test_agent_model_config_max_tokens_positive() -> None:
    with pytest.raises(ValidationError):
        AgentModelConfig.model_validate(
            {
                "model": "x",
                "temperature": 0.5,
                "max_tokens": 0,
                "skill_id": "x",
                "tools": [],
                "tool_choice": {"type": "auto"},
                "cache_system": False,
            }
        )
