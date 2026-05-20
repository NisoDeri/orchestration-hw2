"""Tests for ``services.debate_service``."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate_ai.models.config_models import (
    AgentModelConfig,
    FactsConfig,
    JudgeConfig,
    ModelsConfig,
    ReplayConfig,
    SetupConfig,
    UIConfig,
    WatchdogConfig,
)
from debate_ai.models.persona_models import Persona
from debate_ai.services.debate_service import DebateService
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.gatekeeper import Gatekeeper
from debate_ai.shared.logger import FifoLogger


def _agent_cfg() -> AgentModelConfig:
    return AgentModelConfig.model_validate({
        "model": "claude-sonnet-4-6", "temperature": 0.7, "max_tokens": 1024,
        "skill_id": "sk_test", "tools": [], "tool_choice": {"type": "auto"},
    })


def _setup() -> SetupConfig:
    from debate_ai.constants import AgentRole
    return SetupConfig(
        version="1.00", pings_per_side=2,
        agents_enabled={r.value: r.value in ("judge", "debater-a", "debater-b") for r in AgentRole},
        watchdog=WatchdogConfig(
            timeout_s_per_call=5, max_restarts_per_agent=1,
            keepalive_interval_s=5, on_unrecoverable="skip",
        ),
        judge=JudgeConfig(verdict_no_tie_retries=1, drift_window_turns=2,
                          agreement_keywords=["agree"]),
        ui=UIConfig(), replay=ReplayConfig(),
    )


def _models() -> ModelsConfig:
    from debate_ai.constants import AgentRole
    return ModelsConfig(
        version="1.00", default_model="claude-sonnet-4-6",
        default_betas=["skills-2025-10-02"],
        agents={r.value: _agent_cfg() for r in AgentRole},
    )


def _persona(name: str) -> Persona:
    return Persona.model_validate({
        "version": "1.00", "name": name, "display_name": f"{name} GOAT",
        "color_hex": "#123456",
        "system_prompt": f"You argue passionately for {name} being the best.",
        "style_notes": ["bold"],
        "eras": [{"label": "2009", "system_addendum": "era overlay"}],
    })


def test_debate_service_instantiates() -> None:
    """Smoke test — construction succeeds with mocked deps."""
    gk = MagicMock(spec=Gatekeeper)
    logger = MagicMock(spec=FifoLogger)
    facts_cfg = FactsConfig(version="1.00", lookup_order=[], claims={}, patterns=[])
    svc = DebateService(
        setup=_setup(), models_cfg=_models(),
        persona_a=_persona("Messi"), persona_b=_persona("Ronaldo"),
        motion="Who is the GOAT?", gatekeeper=gk, logger=logger,
        facts_service=FactsService(facts_cfg), anthropic_client=MagicMock(),
    )
    assert svc.motion == "Who is the GOAT?"
