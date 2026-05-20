"""Typed Pydantic models for every JSON file under ``config/``."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

_VERSION_RX = r"^\d+\.\d+$"


class _Versioned(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: str = Field(..., pattern=_VERSION_RX)


class VersionsConfig(_Versioned):
    code: str = Field(..., pattern=_VERSION_RX)
    configs: dict[str, str] = Field(...)


class WatchdogConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timeout_s_per_call: float = Field(..., gt=0)
    max_restarts_per_agent: int = Field(..., ge=0)
    keepalive_interval_s: float = Field(..., gt=0)
    on_unrecoverable: str


class JudgeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict_no_tie_retries: int = Field(..., ge=0)
    drift_window_turns: int = Field(..., ge=1)
    agreement_keywords: list[str] = Field(default_factory=list)


class UIConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    host: str = "127.0.0.1"
    port: int = Field(8000, ge=1, le=65535)
    open_browser_on_start: bool = True


class ReplayConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dir: str = "replays"
    playback_speed_default: float = Field(5.0, gt=0)


class SetupConfig(_Versioned):
    pings_per_side: int = Field(..., ge=1, le=50)
    era_swap_round_index: int | None = Field(None)
    era_swap_strategy: str = "contrasting"
    agents_enabled: dict[str, bool]
    watchdog: WatchdogConfig
    judge: JudgeConfig
    ui: UIConfig
    replay: ReplayConfig


class DebateConfigJson(_Versioned):
    motion: str = Field(..., min_length=10)
    persona_a: str = Field(..., min_length=1)
    persona_b: str = Field(..., min_length=1)


class AgentModelConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    model: str
    temperature: float = Field(..., ge=0, le=2)
    max_tokens: int = Field(..., gt=0)
    skill_id: str
    tools: list[dict] = Field(default_factory=list)
    tool_choice: dict
    cache_system: bool = False


class ModelsConfig(_Versioned):
    default_model: str
    default_betas: list[str]
    agents: dict[str, AgentModelConfig]


class _AnthropicLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_requests_per_second: float = Field(..., gt=0)
    max_concurrent: int = Field(..., ge=1)
    queue_max_depth: int = Field(..., ge=1)
    queue_max_block_s: float = Field(..., gt=0)


class _RetryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_retries: int = Field(..., ge=0)
    backoff_base_s: float = Field(..., gt=0)
    backoff_factor: float = Field(..., ge=1)
    backoff_max_s: float = Field(..., gt=0)
    retry_on_status: list[int]


class _CostCaps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_cost_usd_per_debate: float = Field(..., gt=0)
    search_cost_usd_per_use: float = Field(..., ge=0)


class RateLimitsConfig(_Versioned):
    web_search_provider: str = "anthropic_builtin"
    anthropic: _AnthropicLimits
    retry_policy: _RetryPolicy
    cost_caps: _CostCaps


class LoggingConfig(_Versioned):
    dir: str = "logs"
    max_files: int = Field(..., ge=1)
    lines_per_file: int = Field(..., ge=10)
    default_level: str = "INFO"
    level_overrides: dict[str, str] = Field(default_factory=dict)
    tail_default_n: int = Field(100, ge=1)


class FactClaim(BaseModel):
    model_config = ConfigDict(extra="allow")
    value: int | float | str
    as_of: str
    source: str
    severity_on_mismatch: float = Field(..., ge=0, le=1)


class FactPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    regex: str
    claim_id: str


class FactsConfig(_Versioned):
    lookup_order: list[str]
    claims: dict[str, FactClaim] = Field(default_factory=dict)
    patterns: list[FactPattern] = Field(default_factory=list)
