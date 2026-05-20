"""Demo service — runs a full debate with pre-scripted agents (no API key)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from debate_ai.agents.demo_agents import DemoDebater, DemoJudge
from debate_ai.agents.demo_data import MESSI_ARGS, RONALDO_ARGS
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

DEMO_PINGS = 10


def run_demo(config_dir: Path) -> DebateResult:
    """Assemble demo agents and run the full orchestration loop."""
    emitter = EventEmitter("demo-cli")
    from debate_ai.cli.demo_printer import demo_subscriber
    emitter.subscribe(demo_subscriber)
    return _run_core(config_dir, emitter)


def run_demo_with_emitter(config_dir: Path, emitter: EventEmitter) -> DebateResult:
    """Run demo wired to an external emitter (for the web UI)."""
    _attach_ui_support(emitter)
    import time
    time.sleep(1)
    return _run_core(config_dir, emitter)


def _run_core(config_dir: Path, emitter: EventEmitter) -> DebateResult:
    loader = ConfigLoader(config_dir)
    dj = loader.load("debate")
    pa, pb = loader.load_persona(dj.persona_a), loader.load_persona(dj.persona_b)
    setup = _demo_setup(DEMO_PINGS)
    dcfg = DebateConfig(
        motion=dj.motion, persona_a=pa, persona_b=pb,
        pings_per_side=DEMO_PINGS, era_swap_round_index=4,
        agents_enabled={r.value: False for r in AgentRole},
    )
    state = DebateState(cfg=dcfg)
    memory = ConversationMemory("demo", dj.motion)
    logger = FifoLogger(directory=Path("logs"), max_files=5, lines_per_file=200)
    agents = {
        AgentRole.JUDGE.value: DemoJudge(),
        AgentRole.DEBATER_A.value: DemoDebater(MESSI_ARGS),
        AgentRole.DEBATER_B.value: DemoDebater(RONALDO_ARGS),
    }
    watchdog = Watchdog(setup.watchdog, logger)
    mgr = DebateManager(
        agents=agents, state=state, memory=memory,
        rounds=RoundManager(setup), watchdog=watchdog,
        emitter=emitter, scoring=ScoringService(["agree"], 2), logger=logger,
    )
    final = mgr.run()
    watchdog.shutdown()
    return DebateResult(
        debate_id=final.debate_id, motion=dj.motion,
        persona_a_name=pa.name, persona_b_name=pb.name,
        verdict=final.verdict, scoreboard=final.scoreboard,
        started_at=final.started_at,
        ended_at=final.ended_at or datetime.now(timezone.utc),
        turn_count=len(memory.snapshot()), cost_usd=0.0,
    )


def _attach_ui_support(emitter: EventEmitter) -> None:
    from debate_ai.agents.demo_support_data import (
        COMMENTATOR_LINES,
        CROWD_REACTIONS,
        FACT_CHECKS,
        JUDGE_PROMPTS,
    )
    turn = {"idx": 0}

    def _on_event(event: Any) -> None:
        import time
        if event.kind == "debate_started":
            time.sleep(0.5)
            emitter.emit("judge_guidance", {"text": JUDGE_PROMPTS[0]})
            return
        if event.kind == "agent_started_typing":
            agent = event.payload.get("agent", "")
            if agent not in ("debater-a", "debater-b"):
                return
            jp = min(turn["idx"] + 1, len(JUDGE_PROMPTS) - 1)
            time.sleep(0.3)
            emitter.emit("judge_guidance", {"text": JUDGE_PROMPTS[jp]})
            return
        if event.kind != "agent_message":
            return
        if event.payload.get("agent", "") not in ("debater-a", "debater-b"):
            return
        idx = turn["idx"]
        time.sleep(0.3)
        if idx < len(COMMENTATOR_LINES):
            emitter.emit("commentary", {"commentary": COMMENTATOR_LINES[idx]})
            time.sleep(0.2)
        if idx < len(CROWD_REACTIONS):
            emojis, liner, lean = CROWD_REACTIONS[idx]
            d = "Messi" if lean > 0 else "Ronaldo" if lean < 0 else "split"
            emitter.emit("crowd_reaction", {"emojis": emojis, "one_liner": f"{liner} (leaning {d})"})
            time.sleep(0.2)
        if idx < len(FACT_CHECKS) and FACT_CHECKS[idx]:
            claims = [{"quote": fc["claim"], "verdict": fc["verdict"], "note": fc["note"]}
                      for fc in FACT_CHECKS[idx]]
            emitter.emit("fact_check", {"claims": claims})
        turn["idx"] += 1

    emitter.subscribe(_on_event)


def _demo_setup(pings: int) -> SetupConfig:
    return SetupConfig(
        version="1.00", pings_per_side=pings, era_swap_round_index=4,
        agents_enabled={r.value: False for r in AgentRole},
        watchdog=WatchdogConfig(
            timeout_s_per_call=30, max_restarts_per_agent=1,
            keepalive_interval_s=5, on_unrecoverable="skip",
        ),
        judge=JudgeConfig(verdict_no_tie_retries=1, drift_window_turns=2),
        ui={"host": "127.0.0.1", "port": 8000, "open_browser_on_start": False},
        replay={"dir": "replays", "playback_speed_default": 5.0},
    )
