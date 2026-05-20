"""Agent factory — builds every agent from config + shared resources.

Single function: ``create_agents`` returns a dict keyed by ``AgentRole``
value. Keeps the orchestrator ignorant of per-agent constructor
signatures.
"""

from __future__ import annotations

from typing import Any

from debate_ai.agents.base_agent import AgentContext
from debate_ai.agents.commentator_agent import CommentatorAgent
from debate_ai.agents.crowd_agent import CrowdAgent
from debate_ai.agents.debater_agent import MessiAgent, RonaldoAgent
from debate_ai.agents.factchecker_agent import FactCheckerAgent
from debate_ai.agents.judge_agent import JudgeAgent
from debate_ai.constants import AgentRole
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import ModelsConfig, SetupConfig
from debate_ai.models.persona_models import Persona
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.gatekeeper import Gatekeeper


def create_agents(
    *,
    setup: SetupConfig,
    models: ModelsConfig,
    persona_a: Persona,
    persona_b: Persona,
    facts_service: FactsService,
    gatekeeper: Gatekeeper,
    memory: ConversationMemory,
    context_builder: ContextBuilder,
    anthropic_client: Any,
) -> dict[str, Any]:
    """Construct all enabled agents and return them keyed by role string."""
    betas = models.default_betas
    agents: dict[str, Any] = {}

    def _ctx(role: AgentRole) -> AgentContext:
        return AgentContext(
            role=role.value,
            config=models.agents[role.value],
            default_betas=betas,
            gatekeeper=gatekeeper,
            memory=memory,
            context_builder=context_builder,
            anthropic_client=anthropic_client,
        )

    agents[AgentRole.JUDGE.value] = JudgeAgent(
        _ctx(AgentRole.JUDGE), jcfg=setup.judge,
    )
    agents[AgentRole.DEBATER_A.value] = MessiAgent(
        _ctx(AgentRole.DEBATER_A), persona=persona_a,
    )
    agents[AgentRole.DEBATER_B.value] = RonaldoAgent(
        _ctx(AgentRole.DEBATER_B), persona=persona_b,
    )
    _add_optional(agents, setup, AgentRole.COMMENTATOR, lambda: CommentatorAgent(
        _ctx(AgentRole.COMMENTATOR),
    ))
    _add_optional(agents, setup, AgentRole.CROWD, lambda: CrowdAgent(
        _ctx(AgentRole.CROWD),
    ))
    _add_optional(agents, setup, AgentRole.FACT_CHECKER, lambda: FactCheckerAgent(
        _ctx(AgentRole.FACT_CHECKER), facts_service=facts_service,
    ))
    return agents


def _add_optional(
    agents: dict, setup: SetupConfig, role: AgentRole, builder: Any,
) -> None:
    if setup.agents_enabled.get(role.value, False):
        agents[role.value] = builder()
