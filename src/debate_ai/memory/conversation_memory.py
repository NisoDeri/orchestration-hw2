"""Append-only debate transcript.

Owns the canonical history of ``JudgeEnvelope``s. ``ContextBuilder`` consumes
this through ``view_for`` to compute per-agent visibility — agents never
read the transcript directly.
"""

from __future__ import annotations

import threading

from pydantic import BaseModel, ConfigDict, Field

from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import JudgeEnvelope


class TranscriptEntry(BaseModel):
    """One row in the transcript: an envelope + ordering metadata."""

    model_config = ConfigDict(extra="forbid")
    envelope: JudgeEnvelope
    seq: int
    in_round: int


class ConversationMemory:
    """Mutable, thread-safe transcript store for a single debate."""

    def __init__(self, debate_id: str, motion: str) -> None:
        self.debate_id = debate_id
        self.motion = motion
        self.entries: list[TranscriptEntry] = []
        self.scoreboard = ScoreAggregate()
        self._lock = threading.RLock()
        self._next_seq = 0

    def append(self, envelope: JudgeEnvelope) -> TranscriptEntry:
        """Stamp ``seq`` + ``in_round`` and append."""
        with self._lock:
            entry = TranscriptEntry(envelope=envelope, seq=self._next_seq, in_round=envelope.round)
            self.entries.append(entry)
            self._next_seq += 1
            return entry

    def latest(self) -> TranscriptEntry | None:
        with self._lock:
            return self.entries[-1] if self.entries else None

    def latest_from(self, sender: str) -> TranscriptEntry | None:
        with self._lock:
            for entry in reversed(self.entries):
                if entry.envelope.sender == sender:
                    return entry
        return None

    def entries_in_round(self, round_index: int) -> list[TranscriptEntry]:
        with self._lock:
            return [e for e in self.entries if e.in_round == round_index]

    def snapshot(self) -> list[TranscriptEntry]:
        """Return a copy of all entries (safe to iterate without the lock)."""
        with self._lock:
            return list(self.entries)


class MemorySummary(BaseModel):
    """Light snapshot — used in log records and the replay export header."""

    model_config = ConfigDict(extra="forbid")
    debate_id: str
    motion: str
    turn_count: int = Field(..., ge=0)
    rounds_observed: int = Field(..., ge=0)


def summarize(memory: ConversationMemory) -> MemorySummary:
    """Build a MemorySummary from a live ConversationMemory."""
    snapshot = memory.snapshot()
    rounds = {e.in_round for e in snapshot}
    return MemorySummary(
        debate_id=memory.debate_id,
        motion=memory.motion,
        turn_count=len(snapshot),
        rounds_observed=len(rounds),
    )
