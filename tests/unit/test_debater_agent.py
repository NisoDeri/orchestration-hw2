"""Tests for ``agents.debater_agent``."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from debate_ai.agents.debater_agent import MessiAgent, RonaldoAgent
from debate_ai.constants import AgentRole, EnvelopeKind
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.message_models import JudgeEnvelope
from debate_ai.models.persona_models import Era, Persona
from debate_ai.shared.exceptions import SchemaError
from debate_ai.shared.gatekeeper import Gatekeeper
from tests.unit.test_base_agent import _agent_model_cfg


def _persona(**kw) -> Persona:
    defaults = {
        "version": "1.00",
        "name": "Messi",
        "display_name": "Lionel Messi",
        "color_hex": "#7B1E3B",
        "system_prompt": "You argue for Messi.",
        "style_notes": ["calm"],
        "eras": [{"label": "2009", "system_addendum": "You are 2009 Messi."}],
    }
    defaults.update(kw)
    return Persona.model_validate(defaults)


def _gk_call(fn, *a, model="unknown", source="anthropic", **kw):
    return fn(*a, **kw)


def _ctx(client: MagicMock, role: str = "debater-a"):
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


def _envelope(round_idx: int = 1) -> JudgeEnvelope:
    return JudgeEnvelope(
        round=round_idx,
        kind=EnvelopeKind.REBUTTAL,
        sender="judge",
        recipient="debater-a",
        payload={"argument": "Ronaldo scores more CL goals."},
    )


def test_messi_side_role() -> None:
    assert MessiAgent(_ctx(MagicMock()), _persona()).side_role == AgentRole.DEBATER_A.value


def test_ronaldo_side_role() -> None:
    p = _persona(name="Ronaldo", color_hex="#0E3D6B")
    assert RonaldoAgent(_ctx(MagicMock(), "debater-b"), p).side_role == AgentRole.DEBATER_B.value


def test_respond_valid(mock_anthropic_client: MagicMock) -> None:
    valid_payload = {
        "argument": "Messi's eight Ballon d'Ors are unmatched.",
        "confidence": 0.8,
        "attack_points": ["CL is club-level"],
        "defense_points": ["8 BdO"],
        "citations": ["https://example.com"],
        "references_opponent": "you cited Ronaldo's CL record",
    }
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=valid_payload)]
    response.usage = MagicMock(input_tokens=10, output_tokens=20)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = MessiAgent(_ctx(mock_anthropic_client), _persona())
    reply = agent.respond(_envelope())
    assert "Ballon" in reply.argument
    assert reply.citations == ["https://example.com"]


def test_respond_rejects_empty_citations(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [
        MagicMock(
            type="tool_use",
            input={
                "argument": "x" * 25,
                "confidence": 0.5,
                "attack_points": [],
                "defense_points": [],
                "citations": [],
                "references_opponent": "ref",
            },
        )
    ]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = MessiAgent(_ctx(mock_anthropic_client), _persona())
    with pytest.raises(SchemaError):
        agent.respond(_envelope())


def test_respond_rejects_bad_schema(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"bad": "field"})]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    agent = MessiAgent(_ctx(mock_anthropic_client), _persona())
    with pytest.raises(SchemaError):
        agent.respond(_envelope())


def test_switch_era() -> None:
    agent = MessiAgent(_ctx(MagicMock()), _persona())
    era = Era(label="2009", system_addendum="You are 2009 Messi.")
    agent.switch_era(era)
    assert agent.current_era is era
    prompt = agent._effective_system_prompt()
    assert "[ERA OVERLAY]" in prompt
    agent.switch_era(None)
    assert "[ERA OVERLAY]" not in agent._effective_system_prompt()


def test_search_counter_bumped(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [
        MagicMock(
            type="tool_use",
            input={
                "argument": "x" * 25,
                "confidence": 0.5,
                "attack_points": ["a"],
                "defense_points": ["d"],
                "citations": ["https://x.com"],
                "references_opponent": "ref",
            },
        ),
        MagicMock(type="web_search_tool_result"),
    ]
    response.usage = MagicMock(input_tokens=5, output_tokens=10)
    mock_anthropic_client.beta.messages.create.return_value = response
    ctx = _ctx(mock_anthropic_client)
    agent = MessiAgent(ctx, _persona())
    agent.respond(_envelope())
    ctx.gatekeeper.record_search_use.assert_called_once_with(1)
