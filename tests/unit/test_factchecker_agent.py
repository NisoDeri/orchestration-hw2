"""Tests for ``agents.factchecker_agent``."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from debate_ai.agents.factchecker_agent import FactCheckerAgent, _extract_argument_text
from debate_ai.constants import EnvelopeKind
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import FactsConfig
from debate_ai.models.message_models import JudgeEnvelope
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.exceptions import SchemaError
from debate_ai.shared.gatekeeper import Gatekeeper
from tests.unit.test_base_agent import _agent_model_cfg


def _gk_call(fn, *a, model="unknown", source="anthropic", **kw):
    return fn(*a, **kw)


def _ctx(client: MagicMock):
    gk = MagicMock(spec=Gatekeeper)
    gk.call = MagicMock(side_effect=_gk_call)
    from debate_ai.agents.base_agent import AgentContext
    return AgentContext(
        role="fact-checker", config=_agent_model_cfg(),
        default_betas=["skills-2025-10-02"], gatekeeper=gk,
        memory=ConversationMemory("test-debate", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=client,
    )


def _facts_service() -> FactsService:
    cfg = FactsConfig(version="1.00", lookup_order=["facts_json"], claims={}, patterns=[])
    return FactsService(cfg)


def _envelope() -> JudgeEnvelope:
    return JudgeEnvelope(
        round=1, kind=EnvelopeKind.REBUTTAL,
        sender="debater-a", recipient="fact-checker",
        payload={"argument": "Messi won 8 Ballon d'Ors."},
    )


def test_respond_valid(mock_anthropic_client: MagicMock) -> None:
    payload = {
        "envelope_ref": "e1",
        "claims": [{
            "quote": "8 Ballon d'Ors", "verdict": "correct", "severity": 0.0,
            "source_kind": "facts_json", "source_ref": "ballon_dor_count_messi",
        }],
    }
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = FactCheckerAgent(_ctx(mock_anthropic_client), _facts_service())
    reply = agent.respond(_envelope())
    assert len(reply.claims) == 1
    assert reply.claims[0].verdict == "correct"


def test_respond_defaults_envelope_ref(mock_anthropic_client: MagicMock) -> None:
    payload = {"claims": []}
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=payload)]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = FactCheckerAgent(_ctx(mock_anthropic_client), _facts_service())
    env = _envelope()
    reply = agent.respond(env)
    assert reply.envelope_ref == env.envelope_id


def test_respond_rejects_bad_schema(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"bad": True})]
    response.usage = MagicMock(input_tokens=5, output_tokens=5)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = FactCheckerAgent(_ctx(mock_anthropic_client), _facts_service())
    with pytest.raises(SchemaError):
        agent.respond(_envelope())


def test_extract_argument_text() -> None:
    env = _envelope()
    assert _extract_argument_text(env) == "Messi won 8 Ballon d'Ors."


def test_extract_argument_text_missing() -> None:
    env = JudgeEnvelope(
        round=1, kind=EnvelopeKind.REBUTTAL,
        sender="debater-a", recipient="fact-checker", payload={},
    )
    assert _extract_argument_text(env) == ""
