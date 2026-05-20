"""Debate-state Pydantic models — Round, ScoreAggregate, DebateState, DebateResult."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from debate_ai.constants import RoundKind
from debate_ai.models.message_models import JudgeEnvelope, TurnScore, Verdict
from debate_ai.models.persona_models import Era, Persona


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid4())


class Round(BaseModel):
    """One round in a debate. Index is 1-based; opening is round 0."""

    model_config = ConfigDict(extra="forbid")
    index: int = Field(..., ge=0)
    kind: RoundKind
    era_a: Era | None = None
    era_b: Era | None = None


class ScoreAggregate(BaseModel):
    """Running per-debater totals across all turns of a debate."""

    model_config = ConfigDict(extra="forbid")
    a_logic: float = 0.0
    a_evidence: float = 0.0
    a_persuasion: float = 0.0
    a_counter: float = 0.0
    b_logic: float = 0.0
    b_evidence: float = 0.0
    b_persuasion: float = 0.0
    b_counter: float = 0.0

    def add_turn(self, debater: str, ts: TurnScore) -> None:
        """Add one turn's score into the running aggregate."""
        if debater == "debater-a":
            self.a_logic += ts.logic
            self.a_evidence += ts.evidence
            self.a_persuasion += ts.persuasion
            self.a_counter += ts.counter
        elif debater == "debater-b":
            self.b_logic += ts.logic
            self.b_evidence += ts.evidence
            self.b_persuasion += ts.persuasion
            self.b_counter += ts.counter
        else:
            raise ValueError(f"unknown debater: {debater!r}")

    def total_a(self) -> float:
        return self.a_logic + self.a_evidence + self.a_persuasion + self.a_counter

    def total_b(self) -> float:
        return self.b_logic + self.b_evidence + self.b_persuasion + self.b_counter

    def confidence_a(self) -> float:
        """``total_a`` normalized into 0..1 vs combined total. 0.5 means even."""
        total = self.total_a() + self.total_b()
        return 0.5 if total == 0 else self.total_a() / total

    def winner_from_aggregate(self) -> str:
        """Fallback winner when the LLM verdict is rejected as a tie."""
        if self.total_a() > self.total_b():
            return "debater-a"
        if self.total_b() > self.total_a():
            return "debater-b"
        # truly equal — break by counter-arg, then by persuasion, then by logic.
        for key in ("counter", "persuasion", "logic"):
            a_val = getattr(self, f"a_{key}")
            b_val = getattr(self, f"b_{key}")
            if a_val != b_val:
                return "debater-a" if a_val > b_val else "debater-b"
        return "debater-a"  # arbitrary final fallback; nondeterminism is unacceptable


class DebateConfig(BaseModel):
    """In-memory debate config — passed to DebateManager.start."""

    model_config = ConfigDict(extra="forbid")
    motion: str
    persona_a: Persona
    persona_b: Persona
    pings_per_side: int = Field(..., ge=1)
    era_swap_round_index: int | None = None
    era_swap_strategy: str = "contrasting"
    agents_enabled: dict[str, bool]


class DebateState(BaseModel):
    """Mutable state mutated by the orchestrator while a debate runs."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    debate_id: str = Field(default_factory=_new_id)
    started_at: datetime = Field(default_factory=_now)
    cfg: DebateConfig
    history: list[JudgeEnvelope] = Field(default_factory=list)
    scoreboard: ScoreAggregate = Field(default_factory=ScoreAggregate)
    rounds: list[Round] = Field(default_factory=list)
    current_round: int = 0
    verdict: Verdict | None = None
    ended_at: datetime | None = None


class DebateResult(BaseModel):
    """What the SDK returns to its caller — debate is over, verdict is final."""

    model_config = ConfigDict(extra="allow")
    debate_id: str
    motion: str
    persona_a_name: str
    persona_b_name: str
    verdict: Verdict
    scoreboard: ScoreAggregate
    started_at: datetime
    ended_at: datetime
    turn_count: int
    cost_usd: float = 0.0
    extras: dict[str, Any] = Field(default_factory=dict)
