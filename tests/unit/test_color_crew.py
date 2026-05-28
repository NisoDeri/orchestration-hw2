"""Tests for commentator + crowd agents."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from debate_ai.agents.commentator_agent import CommentatorAgent
from debate_ai.agents.crowd_agent import CrowdAgent
from debate_ai.constants import EnvelopeKind
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.message_models import JudgeEnvelope
from debate_ai.shared.exceptions import SchemaError
from debate_ai.shared.gatekeeper import Gatekeeper
from tests.unit.test_base_agent import _agent_model_cfg


def _gk_call(fn, *a, model="unknown", source="anthropic", **kw):
    return fn(*a, **kw)


def _ctx(client: MagicMock, role: str = "commentator"):
    gk = MagicMock(spec=Gatekeeper)
    gk.call = MagicMock(side_effect=_gk_call)
    from debate_ai.agents.base_agent import AgentContext

    return AgentContext(
        role=role,
        config=_agent_model_cfg(),
        default_betas=["skills-2025-10-02"],
        gatekeeper=gk,
        memory=ConversationMemory("test-debate", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=client,
    )


def _envelope() -> JudgeEnvelope:
    return JudgeEnvelope(
        round=2,
        kind=EnvelopeKind.REBUTTAL,
        sender="debater-a",
        recipient="commentator",
        payload={"argument": "Messi's dribbling is art."},
    )


def test_commentator_respond_valid(mock_anthropic_client: MagicMock) -> None:
    payload = {"commentary": "Messi lands a rhetorical nutmeg!", "tone": "neutral", "round_ref": 2}
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CommentatorAgent(_ctx(mock_anthropic_client))
    reply = agent.respond(_envelope())
    assert reply.commentary == "Messi lands a rhetorical nutmeg!"
    assert reply.round_ref == 2


def test_commentator_defaults_round_ref(mock_anthropic_client: MagicMock) -> None:
    payload = {"commentary": "What a round!", "tone": "neutral"}
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CommentatorAgent(_ctx(mock_anthropic_client))
    reply = agent.respond(_envelope())
    assert reply.round_ref == 2


def test_commentator_rejects_bad_schema(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"bad": True})]
    response.usage = MagicMock(input_tokens=5, output_tokens=5)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CommentatorAgent(_ctx(mock_anthropic_client))
    with pytest.raises(SchemaError):
        agent.respond(_envelope())


def test_crowd_respond_valid(mock_anthropic_client: MagicMock) -> None:
    payload = {
        "envelope_ref": "e1",
        "emojis": ["⚽", "🔥"],
        "one_liner": "Messi magic!",
        "lean": -0.5,
    }
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CrowdAgent(_ctx(mock_anthropic_client, role="crowd"))
    reply = agent.respond(_envelope())
    assert reply.one_liner == "Messi magic!"
    assert reply.lean == -0.5


def test_crowd_defaults_envelope_ref(mock_anthropic_client: MagicMock) -> None:
    payload = {"emojis": ["🎯"], "one_liner": "wow", "lean": 0.0}
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CrowdAgent(_ctx(mock_anthropic_client, role="crowd"))
    env = _envelope()
    reply = agent.respond(env)
    assert reply.envelope_ref == env.envelope_id


def test_crowd_rejects_bad_schema(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"invalid": True})]
    response.usage = MagicMock(input_tokens=5, output_tokens=5)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = CrowdAgent(_ctx(mock_anthropic_client, role="crowd"))
    with pytest.raises(SchemaError):
        agent.respond(_envelope())
