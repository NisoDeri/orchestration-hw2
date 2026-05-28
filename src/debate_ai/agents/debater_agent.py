"""Shared base for the two concrete debater classes.

``DebaterAgent`` is abstract — it owns the citations + mutual-reference
enforcement and the JSON contract. ``MessiAgent`` and ``RonaldoAgent`` are
the concrete subclasses (one per persona JSON), kept as explicit classes
per the HW2 prompt's class layout.
"""

from __future__ import annotations

from abc import abstractmethod

from debate_ai.agents.base_agent import AgentContext, BaseAgent
from debate_ai.constants import AgentRole
from debate_ai.models.message_models import DebaterReply, JudgeEnvelope
from debate_ai.models.persona_models import Era, Persona
from debate_ai.shared.exceptions import CitationError, SchemaError


class DebaterAgent(BaseAgent):
    """Abstract debater. Concrete: ``MessiAgent``, ``RonaldoAgent``."""

    def __init__(self, ctx: AgentContext, persona: Persona) -> None:
        super().__init__(ctx, system_prompt=persona.system_prompt)
        self.persona = persona
        self.current_era: Era | None = None

    @property
    @abstractmethod
    def side_role(self) -> str:
        """Return ``"debater-a"`` or ``"debater-b"``."""

    def switch_era(self, era: Era | None) -> None:
        """Enter / leave the era-swap round."""
        self.current_era = era

    def _effective_system_prompt(self) -> str:
        base = self.persona.system_prompt
        if self.current_era is not None:
            return base + "\n\n[ERA OVERLAY] " + self.current_era.system_addendum
        return base

    def _build_system_blocks(self) -> list[dict]:
        text = self._effective_system_prompt()
        block: dict = {"type": "text", "text": text}
        if self.cfg.cache_system:
            block["cache_control"] = {"type": "ephemeral"}
        return [block]

    def respond(self, envelope: JudgeEnvelope) -> DebaterReply:
        """Produce one debater reply against the latest relayed envelope."""
        messages = self._build_messages() or [{"role": "user", "content": _prompt_text(envelope)}]
        response = self._call_anthropic(messages=messages)
        payload = self._extract_payload(response)
        reply = self._validate_reply(payload)
        self._update_search_counter(response)
        return reply

    def _validate_reply(self, payload: dict) -> DebaterReply:
        try:
            reply = DebaterReply.model_validate(payload)
        except Exception as e:  # noqa: BLE001 — re-raise as SchemaError
            raise SchemaError(f"{self.role}: invalid DebaterReply: {e}") from e
        if not reply.citations:
            raise CitationError(f"{self.role}: empty citations[]")
        return reply

    def _update_search_counter(self, response: object) -> None:
        """Bump the Gatekeeper's search counter by the number of search calls used."""
        count = 0
        for block in getattr(response, "content", None) or []:
            kind = block.get("type") if isinstance(block, dict) else getattr(block, "type", "")
            if kind == "web_search_tool_result":
                count += 1
        if count:
            self.gatekeeper.record_search_use(count)


def _prompt_text(envelope: JudgeEnvelope) -> str:
    """First-turn prompt when memory is empty."""
    return (
        f"Round {envelope.round}, kind={envelope.kind.value}. "
        f"Judge relays: {envelope.payload!r}. "
        f"Reply ONLY with a valid DebaterReply JSON object."
    )


class MessiAgent(DebaterAgent):
    """Concrete debater arguing the Messi side."""

    @property
    def side_role(self) -> str:
        return AgentRole.DEBATER_A.value


class RonaldoAgent(DebaterAgent):
    """Concrete debater arguing the Ronaldo side."""

    @property
    def side_role(self) -> str:
        return AgentRole.DEBATER_B.value
