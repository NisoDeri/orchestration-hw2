"""DebateManager — the core orchestration loop.

Owns the debate lifecycle: opening -> (rebuttal | era_swap)* -> closing ->
verdict. Routes envelopes child -> father -> child, drives the watchdog,
fires events, and delegates scoring to the Judge.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from debate_ai.agents.judge_agent import JudgeAgent, fallback_verdict
from debate_ai.constants import AgentRole, EnvelopeKind
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.debate_models import DebateState
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.orchestration.round_manager import RoundManager
from debate_ai.orchestration.watchdog import Watchdog
from debate_ai.services.scoring_service import ScoringService
from debate_ai.shared.exceptions import (
    AgentUnrecoverableError,
    VerdictTieError,
    WatchdogTimeoutError,
)
from debate_ai.shared.logger import FifoLogger


class DebateManager:
    """Run one complete debate from opening to verdict."""

    def __init__(
        self,
        agents: dict[str, Any],
        state: DebateState,
        memory: ConversationMemory,
        rounds: RoundManager,
        watchdog: Watchdog,
        emitter: EventEmitter,
        scoring: ScoringService,
        logger: FifoLogger,
    ) -> None:
        self.agents = agents
        self.state = state
        self.memory = memory
        self.rounds = rounds
        self.watchdog = watchdog
        self.emitter = emitter
        self.scoring = scoring
        self.logger = logger

    @property
    def judge(self) -> JudgeAgent:
        return self.agents[AgentRole.JUDGE.value]

    def run(self) -> DebateState:
        """Execute the full debate and return the final state."""
        self.emitter.emit("debate_started", {"motion": self.state.cfg.motion})
        self._run_rounds()
        self._issue_verdict()
        winner = self.state.verdict.winner if self.state.verdict else "unknown"
        self.emitter.emit("debate_ended", {"winner": winner})
        self.state.ended_at = datetime.now(timezone.utc)
        return self.state

    def _run_rounds(self) -> None:
        while not self.rounds.is_debate_over():
            kind = self.rounds.current_kind()
            self.emitter.emit("round_changed", {
                "round": self.rounds.current_round,
                "kind": kind.value,
            })
            self._run_one_round(kind)
            self.rounds.advance()

    def _run_one_round(self, kind: Any) -> None:
        rnd = self.rounds.current_round
        env_kind = EnvelopeKind(kind.value)
        for debater_role in (AgentRole.DEBATER_A.value, AgentRole.DEBATER_B.value):
            self._debater_turn(debater_role, env_kind, rnd)

    def _debater_turn(self, role: str, kind: EnvelopeKind, rnd: int) -> None:
        debater = self.agents[role]
        envelope = self.judge.relay(
            sender=_opponent(role), recipient=role,
            kind=kind, payload=self._last_payload(role), round_index=rnd,
        )
        self.memory.append(envelope)
        self.emitter.emit("agent_started_typing", {"agent": role})
        try:
            reply = self.watchdog.call_with_timeout(role, debater.respond, envelope)
        except (WatchdogTimeoutError, AgentUnrecoverableError):
            self.logger.log("ERROR", source="debate_manager",
                            kind="agent_failed", agent=role)
            return
        reply_env = self.judge.relay(
            sender=role, recipient=_opponent(role),
            kind=kind, payload=reply.model_dump(), round_index=rnd,
        )
        self.memory.append(reply_env)
        self.state.history.append(reply_env)
        self.emitter.emit("agent_message", {
            "agent": role, "round": rnd, "argument": reply.argument,
        })
        self._score_turn(role, reply)
        self._run_support_agents(reply_env)

    def _score_turn(self, role: str, reply: Any) -> None:
        try:
            score = self.watchdog.call_with_timeout(
                "judge", self.judge.score_turn, reply,
            )
        except (WatchdogTimeoutError, AgentUnrecoverableError):
            return
        adjusted = self.scoring.apply_lie_catch_bonus(score, reply, [])
        self.state.scoreboard.add_turn(role, adjusted)
        self.emitter.emit("score_update", {
            "agent": role, "score": adjusted.model_dump(),
        })

    def _run_support_agents(self, envelope: Any) -> None:
        for role in (AgentRole.COMMENTATOR.value, AgentRole.CROWD.value,
                     AgentRole.FACT_CHECKER.value):
            if role not in self.agents:
                continue
            try:
                result = self.watchdog.call_with_timeout(
                    role, self.agents[role].respond, envelope,
                )
                self.emitter.emit(_support_event_kind(role), result.model_dump())
            except (WatchdogTimeoutError, AgentUnrecoverableError):
                self.logger.log("WARN", source="debate_manager",
                                kind="support_failed", agent=role)

    def _issue_verdict(self) -> None:
        scoreboard = self.state.scoreboard
        try:
            verdict = self.watchdog.call_with_timeout(
                "judge", self.judge.verdict, scoreboard,
            )
        except (WatchdogTimeoutError, VerdictTieError, AgentUnrecoverableError):
            verdict = fallback_verdict(
                scoreboard, "Deterministic fallback after judge failure.",
            )
        self.state.verdict = verdict
        self.emitter.emit("verdict", verdict.model_dump())

    def _last_payload(self, for_role: str) -> dict:
        entry = self.memory.latest_from(_opponent(for_role))
        if entry is None:
            return {"prompt": "You go first. State your opening argument."}
        return entry.envelope.payload


def _opponent(role: str) -> str:
    if role == AgentRole.DEBATER_A.value:
        return AgentRole.DEBATER_B.value
    return AgentRole.DEBATER_A.value


def _support_event_kind(role: str) -> str:
    mapping = {
        AgentRole.COMMENTATOR.value: "commentary",
        AgentRole.CROWD.value: "crowd_reaction",
        AgentRole.FACT_CHECKER.value: "fact_check",
    }
    return mapping.get(role, "agent_message")
