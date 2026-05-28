"""Tests for ``memory.conversation_memory`` + ``memory.context_builder``."""

from __future__ import annotations

import json

from debate_ai.constants import EnvelopeKind
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory, summarize
from debate_ai.models.message_models import JudgeEnvelope


def _env(
    sender: str,
    recipient: str,
    kind: EnvelopeKind = EnvelopeKind.REBUTTAL,
    round_index: int = 1,
    payload: dict | None = None,
) -> JudgeEnvelope:
    return JudgeEnvelope(
        round=round_index,
        kind=kind,
        sender=sender,
        recipient=recipient,
        payload=payload or {"argument": f"{sender}->{recipient}"},
    )


def test_memory_append_stamps_seq() -> None:
    mem = ConversationMemory("d1", "motion")
    e1 = mem.append(_env("debater-a", "debater-b"))
    e2 = mem.append(_env("debater-b", "debater-a"))
    assert e1.seq == 0
    assert e2.seq == 1


def test_memory_latest_and_latest_from() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b"))
    mem.append(_env("debater-b", "debater-a"))
    assert mem.latest().envelope.sender == "debater-b"
    assert mem.latest_from("debater-a").envelope.sender == "debater-a"
    assert mem.latest_from("nobody") is None


def test_memory_entries_in_round() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b", round_index=1))
    mem.append(_env("debater-b", "debater-a", round_index=2))
    assert len(mem.entries_in_round(1)) == 1
    assert len(mem.entries_in_round(2)) == 1
    assert mem.entries_in_round(99) == []


def test_summarize() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b", round_index=1))
    mem.append(_env("debater-b", "debater-a", round_index=2))
    s = summarize(mem)
    assert s.turn_count == 2
    assert s.rounds_observed == 2


def test_visibility_judge_sees_everything() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b"))
    mem.append(_env("debater-b", "debater-a"))
    mem.append(_env("judge", "all", kind=EnvelopeKind.RULING))
    cb = ContextBuilder()
    visible = cb.visible_entries("judge", mem)
    assert len(visible) == 3


def test_visibility_debater_a_only_sees_own_addressed() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b"))  # NOT visible to A
    mem.append(_env("debater-b", "debater-a"))  # visible to A
    mem.append(_env("judge", "all", kind=EnvelopeKind.RULING))  # visible (broadcast)
    cb = ContextBuilder()
    visible = cb.visible_entries("debater-a", mem)
    senders = [e.envelope.sender for e in visible]
    assert "debater-b" in senders
    assert "judge" in senders
    assert "debater-a" not in senders


def test_visibility_crowd_sees_only_latest_debater_envelope() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b"))
    mem.append(_env("debater-b", "debater-a"))
    mem.append(_env("judge", "all", kind=EnvelopeKind.RULING))
    cb = ContextBuilder()
    visible = cb.visible_entries("crowd", mem)
    assert len(visible) == 1
    assert visible[0].envelope.sender == "debater-b"


def test_visibility_factchecker_sees_only_latest() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-a", "debater-b"))
    mem.append(_env("debater-b", "debater-a"))
    visible = ContextBuilder().visible_entries("fact-checker", mem)
    assert len(visible) == 1


def test_context_builder_emits_messages_with_role() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("debater-b", "debater-a"))  # opponent
    mem.append(_env("debater-a", "debater-b"))  # own past reply (won't be visible to A)
    cb = ContextBuilder()
    messages = cb.build("debater-a", mem)
    # debater-a only sees the opponent message.
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    decoded = json.loads(messages[0]["content"])
    assert decoded["from"] == "debater-b"


def test_context_builder_self_message_is_assistant_role() -> None:
    mem = ConversationMemory("d1", "motion")
    mem.append(_env("judge", "all", kind=EnvelopeKind.RULING))
    mem.append(_env("debater-a", "debater-b"))  # A spoke to B
    cb = ContextBuilder()
    messages = cb.build("judge", mem)
    roles = [m["role"] for m in messages]
    # Judge's own RULING envelope -> assistant; debater message -> user.
    assert "assistant" in roles
    assert "user" in roles
