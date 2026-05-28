"""Pydantic message contracts for all agent JSON shapes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from debate_ai.constants import EnvelopeKind


def _new_id() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DebaterReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    argument: str = Field(..., min_length=20, max_length=4000)
    confidence: float = Field(..., ge=0.0, le=1.0)
    attack_points: list[str] = Field(default_factory=list)
    defense_points: list[str] = Field(default_factory=list)
    citations: list[str] = Field(..., min_length=1)
    references_opponent: str = Field(..., min_length=1)


class CommentaryReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commentary: str = Field(..., min_length=5, max_length=400)
    tone: Literal["neutral", "favouring_a", "favouring_b"] = "neutral"
    round_ref: int = Field(..., ge=0)


class CrowdReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    envelope_ref: str
    emojis: list[str] = Field(..., min_length=1, max_length=5)
    one_liner: str = Field(..., min_length=1, max_length=80)
    lean: float = Field(..., ge=-1.0, le=1.0)


class FactClaimAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quote: str = Field(..., min_length=1)
    verdict: Literal["incorrect", "correct", "misleading", "unverifiable"]
    severity: float = Field(..., ge=0.0, le=1.0)
    actual: str | None = None
    source_kind: Literal["facts_json", "wikipedia_mcp", "web_search"]
    source_ref: str | None = None


class FactCheckReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    envelope_ref: str
    claims: list[FactClaimAnnotation] = Field(default_factory=list)


class TurnScore(BaseModel):
    model_config = ConfigDict(extra="forbid")
    logic: float = Field(..., ge=0.0, le=10.0)
    evidence: float = Field(..., ge=0.0, le=10.0)
    persuasion: float = Field(..., ge=0.0, le=10.0)
    counter: float = Field(..., ge=0.0, le=10.0)

    def total(self) -> float:
        return self.logic + self.evidence + self.persuasion + self.counter


class RubricBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")
    logic: float
    evidence: float
    persuasion: float
    counter: float


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    winner: Literal["debater-a", "debater-b"]
    score_a: float = Field(..., ge=0.0)
    score_b: float = Field(..., ge=0.0)
    reasoning: str = Field(..., min_length=30)
    rubric_breakdown: dict[str, RubricBreakdown]

    @model_validator(mode="after")
    def _no_tie(self) -> Verdict:
        if self.score_a == self.score_b:
            raise ValueError("Verdict ties are forbidden — score_a must differ from score_b")
        named_winner = "debater-a" if self.score_a > self.score_b else "debater-b"
        if self.winner != named_winner:
            raise ValueError(
                f"winner={self.winner!r} contradicts scores (a={self.score_a}, b={self.score_b})"
            )
        return self


AgentPayload = Annotated[
    DebaterReply | CommentaryReply | CrowdReply | FactCheckReply | Verdict | dict,
    Field(description="Discriminated by JudgeEnvelope.kind on the way out."),
]


class JudgeEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    envelope_id: str = Field(default_factory=_new_id)
    round: int = Field(..., ge=0)
    kind: EnvelopeKind
    sender: str
    recipient: str
    payload: dict[str, Any]
    ts: datetime = Field(default_factory=_now)

    @field_validator("sender", "recipient")
    @classmethod
    def _nonempty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("sender/recipient must be non-empty")
        return value


class UIEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    debate_id: str
    seq: int = Field(..., ge=0)
    ts: datetime = Field(default_factory=_now)
    kind: Literal[
        "debate_started",
        "round_changed",
        "agent_started_typing",
        "agent_message",
        "score_update",
        "drift_warning",
        "fact_check",
        "commentary",
        "crowd_reaction",
        "judge_guidance",
        "verdict",
        "debate_ended",
        "error",
    ]
    payload: dict[str, Any] = Field(default_factory=dict)
