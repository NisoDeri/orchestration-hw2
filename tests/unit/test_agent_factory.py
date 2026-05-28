"""Tests for ``agents.factory``."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate_ai.agents.commentator_agent import CommentatorAgent
from debate_ai.agents.crowd_agent import CrowdAgent
from debate_ai.agents.debater_agent import MessiAgent, RonaldoAgent
from debate_ai.agents.factchecker_agent import FactCheckerAgent
from debate_ai.agents.factory import create_agents
from debate_ai.agents.judge_agent import JudgeAgent
from debate_ai.constants import AgentRole
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
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
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.gatekeeper import Gatekeeper


def _agent_cfg() -> AgentModelConfig:
    return AgentModelConfig.model_validate(
        {
            "model": "claude-sonnet-4-6",
            "temperature": 0.7,
            "max_tokens": 1024,
            "skill_id": "sk_test",
            "tools": [],
            "tool_choice": {"type": "auto"},
        }
    )


def _models_cfg() -> ModelsConfig:
    agents = {r.value: _agent_cfg() for r in AgentRole}
    return ModelsConfig(
        version="1.00",
        default_model="claude-sonnet-4-6",
        default_betas=["skills-2025-10-02"],
        agents=agents,
    )


def _setup(enabled: dict[str, bool] | None = None) -> SetupConfig:
    defaults = {r.value: True for r in AgentRole}
    return SetupConfig(
        version="1.00",
        pings_per_side=5,
        agents_enabled=enabled or defaults,
        watchdog=WatchdogConfig(
            timeout_s_per_call=30,
            max_restarts_per_agent=2,
            keepalive_interval_s=5,
            on_unrecoverable="skip",
        ),
        judge=JudgeConfig(
            verdict_no_tie_retries=2,
            drift_window_turns=3,
            agreement_keywords=["agree"],
        ),
        ui=UIConfig(),
        replay=ReplayConfig(),
    )


def _persona(name: str) -> Persona:
    return Persona.model_validate(
        {
            "version": "1.00",
            "name": name,
            "display_name": f"{name} GOAT",
            "color_hex": "#123456",
            "system_prompt": f"You argue for {name}.",
            "style_notes": ["passionate"],
            "eras": [{"label": "2009", "system_addendum": "era"}],
        }
    )


def _facts_service() -> FactsService:
    cfg = FactsConfig(version="1.00", lookup_order=[], claims={}, patterns=[])
    return FactsService(cfg)


def test_all_agents_created() -> None:
    agents = create_agents(
        setup=_setup(),
        models=_models_cfg(),
        persona_a=_persona("Messi"),
        persona_b=_persona("Ronaldo"),
        facts_service=_facts_service(),
        gatekeeper=MagicMock(spec=Gatekeeper),
        memory=ConversationMemory("d1", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=MagicMock(),
    )
    assert isinstance(agents["judge"], JudgeAgent)
    assert isinstance(agents["debater-a"], MessiAgent)
    assert isinstance(agents["debater-b"], RonaldoAgent)
    assert isinstance(agents["commentator"], CommentatorAgent)
    assert isinstance(agents["crowd"], CrowdAgent)
    assert isinstance(agents["fact-checker"], FactCheckerAgent)


def test_optional_agents_skipped_when_disabled() -> None:
    enabled = {r.value: False for r in AgentRole}
    enabled["judge"] = True
    enabled["debater-a"] = True
    enabled["debater-b"] = True
    agents = create_agents(
        setup=_setup(enabled),
        models=_models_cfg(),
        persona_a=_persona("Messi"),
        persona_b=_persona("Ronaldo"),
        facts_service=_facts_service(),
        gatekeeper=MagicMock(spec=Gatekeeper),
        memory=ConversationMemory("d1", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=MagicMock(),
    )
    assert "commentator" not in agents
    assert "crowd" not in agents
    assert "fact-checker" not in agents
    assert "judge" in agents
