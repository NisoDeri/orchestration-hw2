"""DebateService — assembles all components and runs a debate.

This is the bridge between the SDK (which knows nothing about agents or
orchestration internals) and the DebateManager (which knows nothing about
config loading). The SDK calls ``DebateService.run_debate()``; this module
wires everything up.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from debate_ai.agents.factory import create_agents
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import SetupConfig
from debate_ai.models.debate_models import (
    DebateConfig,
    DebateResult,
    DebateState,
)
from debate_ai.models.persona_models import Persona
from debate_ai.orchestration.debate_manager import DebateManager
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.orchestration.round_manager import RoundManager
from debate_ai.orchestration.watchdog import Watchdog
from debate_ai.services.facts_service import FactsService
from debate_ai.services.scoring_service import ScoringService
from debate_ai.shared.gatekeeper import Gatekeeper
from debate_ai.shared.logger import FifoLogger


class DebateService:
    """Assemble and run one complete debate."""

    def __init__(
        self,
        setup: SetupConfig,
        models_cfg: Any,
        persona_a: Persona,
        persona_b: Persona,
        motion: str,
        gatekeeper: Gatekeeper,
        logger: FifoLogger,
        facts_service: FactsService,
        anthropic_client: Any,
    ) -> None:
        self.setup = setup
        self.models_cfg = models_cfg
        self.persona_a = persona_a
        self.persona_b = persona_b
        self.motion = motion
        self.gatekeeper = gatekeeper
        self.logger = logger
        self.facts = facts_service
        self.client = anthropic_client

    def run_debate(self) -> DebateResult:
        """Assemble all components and run the debate to completion."""
        memory = ConversationMemory(debate_id="d1", motion=self.motion)
        ctx_builder = ContextBuilder()
        agents = create_agents(
            setup=self.setup, models=self.models_cfg,
            persona_a=self.persona_a, persona_b=self.persona_b,
            facts_service=self.facts, gatekeeper=self.gatekeeper,
            memory=memory, context_builder=ctx_builder,
            anthropic_client=self.client,
        )
        dcfg = DebateConfig(
            motion=self.motion, persona_a=self.persona_a,
            persona_b=self.persona_b, pings_per_side=self.setup.pings_per_side,
            era_swap_round_index=self.setup.era_swap_round_index,
            agents_enabled=self.setup.agents_enabled,
        )
        state = DebateState(cfg=dcfg)
        rounds = RoundManager(self.setup)
        watchdog = Watchdog(self.setup.watchdog, self.logger)
        emitter = EventEmitter(state.debate_id)
        scoring = ScoringService(
            self.setup.judge.agreement_keywords,
            self.setup.judge.drift_window_turns,
        )
        mgr = DebateManager(
            agents=agents, state=state, memory=memory,
            rounds=rounds, watchdog=watchdog, emitter=emitter,
            scoring=scoring, logger=self.logger,
        )
        final = mgr.run()
        watchdog.shutdown()
        return _to_result(final, memory, self.gatekeeper.cost_so_far_usd())


def _to_result(
    state: DebateState, memory: ConversationMemory, cost_usd: float,
) -> DebateResult:
    return DebateResult(
        debate_id=state.debate_id, motion=state.cfg.motion,
        persona_a_name=state.cfg.persona_a.name,
        persona_b_name=state.cfg.persona_b.name,
        verdict=state.verdict,
        scoreboard=state.scoreboard,
        started_at=state.started_at,
        ended_at=state.ended_at or datetime.now(timezone.utc),
        turn_count=len(memory.snapshot()),
        cost_usd=cost_usd,
    )
