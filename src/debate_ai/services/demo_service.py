"""Demo service — runs a full debate with pre-scripted agents (no API key)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from debate_ai.agents.demo_agents import _MESSI_LINES, _RONALDO_LINES, DemoDebater, DemoJudge
from debate_ai.constants import AgentRole
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import JudgeConfig, SetupConfig, WatchdogConfig
from debate_ai.models.debate_models import DebateConfig, DebateResult, DebateState
from debate_ai.orchestration.debate_manager import DebateManager
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.orchestration.round_manager import RoundManager
from debate_ai.orchestration.watchdog import Watchdog
from debate_ai.services.scoring_service import ScoringService
from debate_ai.shared.config import ConfigLoader
from debate_ai.shared.logger import FifoLogger


def run_demo(config_dir: Path) -> DebateResult:
    """Assemble demo agents and run the full orchestration loop."""
    loader = ConfigLoader(config_dir)
    debate_json = loader.load("debate")
    persona_a = loader.load_persona(debate_json.persona_a)
    persona_b = loader.load_persona(debate_json.persona_b)
    pings = min(len(_MESSI_LINES), 5)
    setup = _demo_setup(pings)
    dcfg = DebateConfig(
        motion=debate_json.motion, persona_a=persona_a, persona_b=persona_b,
        pings_per_side=pings, agents_enabled={r.value: False for r in AgentRole},
    )
    state = DebateState(cfg=dcfg)
    memory = ConversationMemory("demo", debate_json.motion)
    logger = FifoLogger(directory=Path("logs"), max_files=5, lines_per_file=200)
    agents = {
        AgentRole.JUDGE.value: DemoJudge(),
        AgentRole.DEBATER_A.value: DemoDebater(_MESSI_LINES, "Ronaldo"),
        AgentRole.DEBATER_B.value: DemoDebater(_RONALDO_LINES, "Messi"),
    }
    watchdog = Watchdog(setup.watchdog, logger)
    emitter = EventEmitter(state.debate_id)
    from debate_ai.cli.demo_printer import demo_subscriber
    emitter.subscribe(demo_subscriber)
    scoring = ScoringService(["agree"], 2)
    mgr = DebateManager(
        agents=agents, state=state, memory=memory, rounds=RoundManager(setup),
        watchdog=watchdog, emitter=emitter, scoring=scoring, logger=logger,
    )
    final = mgr.run()
    watchdog.shutdown()
    return DebateResult(
        debate_id=final.debate_id, motion=dcfg.motion,
        persona_a_name=persona_a.name, persona_b_name=persona_b.name,
        verdict=final.verdict, scoreboard=final.scoreboard,
        started_at=final.started_at,
        ended_at=final.ended_at or datetime.now(timezone.utc),
        turn_count=len(memory.snapshot()), cost_usd=0.0,
    )


def _demo_setup(pings: int) -> SetupConfig:
    return SetupConfig(
        version="1.00", pings_per_side=pings,
        agents_enabled={r.value: False for r in AgentRole},
        watchdog=WatchdogConfig(
            timeout_s_per_call=30, max_restarts_per_agent=1,
            keepalive_interval_s=5, on_unrecoverable="skip",
        ),
        judge=JudgeConfig(verdict_no_tie_retries=1, drift_window_turns=2),
        ui={"host": "127.0.0.1", "port": 8000, "open_browser_on_start": False},
        replay={"dir": "replays", "playback_speed_default": 5.0},
    )
