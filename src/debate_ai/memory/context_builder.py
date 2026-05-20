"""Per-agent context window builder.

Encodes the visibility rules from ``docs/PRD_memory.md`` §2. Agents call
``ContextBuilder.build(agent_id, memory)`` to get a list of ``messages``
ready for the Anthropic Messages API.
"""

from __future__ import annotations

import json

from debate_ai.constants import AgentRole
from debate_ai.memory.conversation_memory import ConversationMemory, TranscriptEntry


def _opposite_debater(agent_id: str) -> str | None:
    if agent_id == AgentRole.DEBATER_A.value:
        return AgentRole.DEBATER_B.value
    if agent_id == AgentRole.DEBATER_B.value:
        return AgentRole.DEBATER_A.value
    return None


def _is_visible_to(agent_id: str, entry: TranscriptEntry) -> bool:
    """Per-agent visibility check — single source of truth."""
    env = entry.envelope
    if agent_id == AgentRole.JUDGE.value:
        return True
    if agent_id in (AgentRole.DEBATER_A.value, AgentRole.DEBATER_B.value):
        # Debaters see envelopes addressed to them OR judge-broadcasts.
        return env.recipient == agent_id or (
            env.sender == AgentRole.JUDGE.value and env.recipient == "all"
        )
    # Commentator, Crowd, Fact-Checker — see only the latest debater envelope.
    # ContextBuilder.build is responsible for trimming; here we say "in scope".
    return env.sender in (AgentRole.DEBATER_A.value, AgentRole.DEBATER_B.value)


class ContextBuilder:
    """Translate transcript entries into Anthropic ``messages`` lists."""

    def visible_entries(
        self, agent_id: str, memory: ConversationMemory
    ) -> list[TranscriptEntry]:
        """Filter the transcript according to per-agent visibility rules."""
        snapshot = memory.snapshot()
        entries = [e for e in snapshot if _is_visible_to(agent_id, e)]
        if agent_id in (
            AgentRole.COMMENTATOR.value,
            AgentRole.CROWD.value,
            AgentRole.FACT_CHECKER.value,
        ):
            # Take only the most recent visible debater envelope.
            entries = entries[-1:]
        return entries

    def build(self, agent_id: str, memory: ConversationMemory) -> list[dict]:
        """Build the ``messages`` array for an Anthropic call.

        The N-1 entries become alternating ``user`` / ``assistant`` messages
        so the cache prefix is stable; the latest entry becomes the freshest
        ``user`` message (the agent's prompt for this turn).
        """
        entries = self.visible_entries(agent_id, memory)
        return [self._entry_to_message(agent_id, e) for e in entries]

    def _entry_to_message(self, agent_id: str, entry: TranscriptEntry) -> dict:
        env = entry.envelope
        # The agent's *own* past replies become 'assistant' messages.
        role = "assistant" if env.sender == agent_id else "user"
        content = {
            "envelope_id": env.envelope_id,
            "round": env.round,
            "kind": env.kind.value,
            "from": env.sender,
            "to": env.recipient,
            "payload": env.payload,
        }
        return {"role": role, "content": json.dumps(content, ensure_ascii=False)}
