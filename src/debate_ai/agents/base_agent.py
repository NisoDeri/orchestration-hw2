"""BaseAgent ABC + AgentContext.

Every agent inherits from this. Subclasses override ``respond`` and the
``_validate_reply`` parse step. Anthropic calls go through the gatekeeper —
that's the chokepoint per HW2 brief §8.6.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import AgentModelConfig
from debate_ai.models.message_models import JudgeEnvelope
from debate_ai.shared.exceptions import SchemaError
from debate_ai.shared.gatekeeper import Gatekeeper


@dataclass
class AgentContext:
    """The set of resources every agent needs at construction time."""

    role: str
    config: AgentModelConfig
    default_betas: list[str]
    gatekeeper: Gatekeeper
    memory: ConversationMemory
    context_builder: ContextBuilder
    anthropic_client: Any  # `anthropic.Anthropic` at runtime; ``Any`` for testability


class BaseAgent(ABC):
    """Abstract base for every agent class."""

    def __init__(self, ctx: AgentContext, system_prompt: str) -> None:
        self.role = ctx.role
        self.cfg = ctx.config
        self.default_betas = ctx.default_betas
        self.gatekeeper = ctx.gatekeeper
        self.memory = ctx.memory
        self.context_builder = ctx.context_builder
        self.client = ctx.anthropic_client
        self.system_prompt = system_prompt

    @abstractmethod
    def respond(self, envelope: JudgeEnvelope) -> BaseModel:
        """Subclasses implement turn-taking + reply schema validation."""

    def alive(self) -> bool:
        """Heartbeat hook polled by the watchdog. True iff agent is responsive."""
        return self.client is not None

    def _build_system_blocks(self) -> list[dict[str, Any]]:
        """System prompt blocks. Caches the prefix when ``cache_system`` is true."""
        block = {"type": "text", "text": self.system_prompt}
        if self.cfg.cache_system:
            block["cache_control"] = {"type": "ephemeral"}
        return [block]

    def _build_messages(self) -> list[dict[str, Any]]:
        """Per-agent visible transcript turned into Anthropic messages."""
        return self.context_builder.build(self.role, self.memory)

    def _container_param(self) -> dict[str, Any]:
        """Anthropic Agent-Skill binding for this agent's role."""
        return {"skills": [
            {"type": "anthropic", "skill_id": self.cfg.skill_id, "version": "latest"}
        ]}

    def _call_anthropic(self, *, messages: list[dict], **extra: Any) -> Any:
        """Single chokepoint — every API call routes here."""
        api_kwargs: dict[str, Any] = {
            "model": self.cfg.model,
            "betas": self.default_betas,
            "container": self._container_param(),
            "system": self._build_system_blocks(),
            "tools": self.cfg.tools,
            "tool_choice": self.cfg.tool_choice,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
            "messages": messages,
        }
        api_kwargs.update(extra)
        return self.gatekeeper.call(
            self.client.beta.messages.create,
            model=api_kwargs.pop("model"),
            source=f"agent.{self.role}",
            **api_kwargs,
        )

    def _extract_payload(self, response: Any) -> dict[str, Any]:
        """Extract JSON payload from the response.

        Strategy: first ``tool_use`` block with non-empty ``input`` wins. If
        none, parse the first ``text`` block as JSON. Any failure raises
        ``SchemaError`` (the watchdog catches it and retries with a stricter
        prompt suffix).
        """
        content = getattr(response, "content", None) or []
        for block in content:
            btype = _attr(block, "type")
            if btype == "tool_use":
                payload = _attr(block, "input")
                if isinstance(payload, dict) and payload:
                    return payload
        for block in content:
            if _attr(block, "type") == "text":
                text = _attr(block, "text", "")
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as e:
                    raise SchemaError(f"agent {self.role}: non-JSON text reply") from e
                if isinstance(parsed, dict):
                    return parsed
        raise SchemaError(f"agent {self.role}: no usable content block in response")


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    return obj.get(name, default) if isinstance(obj, dict) else getattr(obj, name, default)
