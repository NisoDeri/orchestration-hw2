"""Tests for ``agents.base_agent``."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from debate_ai.agents.base_agent import AgentContext, BaseAgent, _attr
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import AgentModelConfig
from debate_ai.shared.exceptions import SchemaError
from debate_ai.shared.gatekeeper import Gatekeeper


def _agent_model_cfg(**kw) -> AgentModelConfig:
    defaults = {
        "model": "claude-sonnet-4-6",
        "temperature": 0.7,
        "max_tokens": 1024,
        "skill_id": "sk_test",
        "tools": [],
        "tool_choice": {"type": "auto"},
        "cache_system": False,
    }
    defaults.update(kw)
    return AgentModelConfig.model_validate(defaults)


def _gatekeeper_side_effect(fn, *a, model="unknown", source="anthropic", **kw):
    return fn(*a, **kw)


def _make_ctx(client: MagicMock, **overrides) -> AgentContext:
    gk = MagicMock(spec=Gatekeeper)
    gk.call = MagicMock(side_effect=_gatekeeper_side_effect)
    return AgentContext(
        role=overrides.get("role", "judge"),
        config=overrides.get("config", _agent_model_cfg()),
        default_betas=["skills-2025-10-02"],
        gatekeeper=gk,
        memory=ConversationMemory("test-debate", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=client,
    )


class StubAgent(BaseAgent):
    def respond(self, envelope):
        return self._extract_payload(
            self._call_anthropic(messages=[{"role": "user", "content": "hi"}])
        )


def test_extract_payload_tool_use(mock_anthropic_client: MagicMock) -> None:
    ctx = _make_ctx(mock_anthropic_client)
    agent = StubAgent(ctx, system_prompt="test")
    result = agent.respond(None)
    assert result["argument"] == "stub argument"


def test_extract_payload_text_json(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="text", text='{"key": "val"}')]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    ctx = _make_ctx(mock_anthropic_client)
    agent = StubAgent(ctx, system_prompt="test")
    assert agent.respond(None) == {"key": "val"}


def test_extract_payload_raises_on_garbage(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="text", text="not json")]
    mock_anthropic_client.beta.messages.create.return_value = response
    ctx = _make_ctx(mock_anthropic_client)
    agent = StubAgent(ctx, system_prompt="test")
    with pytest.raises(SchemaError):
        agent.respond(None)


def test_alive_returns_true(mock_anthropic_client: MagicMock) -> None:
    ctx = _make_ctx(mock_anthropic_client)
    agent = StubAgent(ctx, system_prompt="test")
    assert agent.alive()


def test_cache_system_adds_cache_control(mock_anthropic_client: MagicMock) -> None:
    cfg = _agent_model_cfg(cache_system=True)
    ctx = _make_ctx(mock_anthropic_client, config=cfg)
    agent = StubAgent(ctx, system_prompt="test")
    blocks = agent._build_system_blocks()
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_container_param_uses_skill_id(mock_anthropic_client: MagicMock) -> None:
    ctx = _make_ctx(mock_anthropic_client)
    agent = StubAgent(ctx, system_prompt="test")
    cp = agent._container_param()
    assert cp["skills"][0]["skill_id"] == "sk_test"


def test_attr_dict_and_object() -> None:
    assert _attr({"type": "tool_use"}, "type") == "tool_use"
    obj = MagicMock()
    obj.type = "text"
    assert _attr(obj, "type") == "text"
    assert _attr({}, "missing", "default") == "default"
