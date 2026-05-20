"""Tests for ``orchestration.debate_manager``."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate_ai.agents.judge_agent import JudgeAgent
from debate_ai.constants import AgentRole, EnvelopeKind
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import (
    JudgeConfig,
    ReplayConfig,
    SetupConfig,
    UIConfig,
    WatchdogConfig,
)
from debate_ai.models.debate_models import DebateConfig, DebateState
from debate_ai.models.message_models import (
    JudgeEnvelope,
    RubricBreakdown,
    TurnScore,
    Verdict,
)
from debate_ai.models.persona_models import Persona
from debate_ai.orchestration.debate_manager import (
    DebateManager,
    _opponent,
    _support_event_kind,
)
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.orchestration.round_manager import RoundManager
from debate_ai.orchestration.watchdog import Watchdog
from debate_ai.services.scoring_service import ScoringService
from debate_ai.shared.logger import FifoLogger


def _persona(name: str) -> Persona:
    return Persona.model_validate({
        "version": "1.00", "name": name, "display_name": f"{name} GOAT",
        "color_hex": "#123456",
        "system_prompt": f"You argue passionately for {name} being the best.",
        "style_notes": ["bold"],
        "eras": [{"label": "2009", "system_addendum": "era overlay"}],
    })


def _setup(pings: int = 2) -> SetupConfig:
    return SetupConfig(
        version="1.00", pings_per_side=pings,
        agents_enabled={r.value: True for r in AgentRole},
        watchdog=WatchdogConfig(
            timeout_s_per_call=5, max_restarts_per_agent=1,
            keepalive_interval_s=5, on_unrecoverable="skip",
        ),
        judge=JudgeConfig(verdict_no_tie_retries=1, drift_window_turns=2,
                          agreement_keywords=["agree"]),
        ui=UIConfig(), replay=ReplayConfig(),
    )


def test_opponent() -> None:
    assert _opponent("debater-a") == "debater-b"
    assert _opponent("debater-b") == "debater-a"


def test_support_event_kind() -> None:
    assert _support_event_kind("commentator") == "commentary"
    assert _support_event_kind("crowd") == "crowd_reaction"
    assert _support_event_kind("fact-checker") == "fact_check"
    assert _support_event_kind("unknown") == "agent_message"


def _verdict() -> Verdict:
    return Verdict(
        winner="debater-a", score_a=80, score_b=70,
        reasoning="x" * 35,
        rubric_breakdown={
            "debater-a": RubricBreakdown(logic=20, evidence=20, persuasion=20, counter=20),
            "debater-b": RubricBreakdown(logic=18, evidence=18, persuasion=18, counter=16),
        },
    )


def _mock_judge() -> MagicMock:
    judge = MagicMock(spec=JudgeAgent)
    judge.relay.return_value = JudgeEnvelope(
        round=0, kind=EnvelopeKind.OPENING,
        sender="judge", recipient="debater-a", payload={"prompt": "go"},
    )
    judge.score_turn.return_value = TurnScore(logic=8, evidence=7, persuasion=9, counter=6)
    judge.verdict.return_value = _verdict()
    return judge


def _make_manager(pings: int = 1) -> DebateManager:
    setup = _setup(pings)
    dcfg = DebateConfig(
        motion="Who is the GOAT?", persona_a=_persona("Messi"),
        persona_b=_persona("Ronaldo"), pings_per_side=pings,
        agents_enabled={r.value: False for r in AgentRole},
    )
    state = DebateState(cfg=dcfg)
    memory = ConversationMemory("d1", "Who is the GOAT?")
    rounds = RoundManager(setup)
    logger = MagicMock(spec=FifoLogger)
    watchdog = MagicMock(spec=Watchdog)
    watchdog.call_with_timeout = MagicMock(side_effect=lambda role, fn, *a, **kw: fn(*a, **kw))
    emitter = EventEmitter("d1")
    scoring = ScoringService(setup.judge.agreement_keywords, setup.judge.drift_window_turns)
    debater_a = MagicMock()
    debater_a.respond.return_value = MagicMock(
        argument="Messi is the best player ever in football history.",
        model_dump=lambda: {"argument": "Messi is the GOAT."},
    )
    debater_b = MagicMock()
    debater_b.respond.return_value = MagicMock(
        argument="Ronaldo's record speaks for itself in all competitions.",
        model_dump=lambda: {"argument": "Ronaldo is the GOAT."},
    )
    agents = {
        AgentRole.JUDGE.value: _mock_judge(),
        AgentRole.DEBATER_A.value: debater_a,
        AgentRole.DEBATER_B.value: debater_b,
    }
    return DebateManager(
        agents=agents, state=state, memory=memory, rounds=rounds,
        watchdog=watchdog, emitter=emitter, scoring=scoring, logger=logger,
    )


def test_run_produces_verdict() -> None:
    mgr = _make_manager(pings=1)
    state = mgr.run()
    assert state.verdict is not None
    assert state.verdict.winner == "debater-a"


def test_run_emits_events() -> None:
    mgr = _make_manager(pings=1)
    mgr.run()
    events = mgr.emitter.history()
    kinds = [e.kind for e in events]
    assert "debate_started" in kinds
    assert "debate_ended" in kinds
    assert "verdict" in kinds
