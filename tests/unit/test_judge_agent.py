"""Tests for ``agents.judge_agent``."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from debate_ai.agents.judge_agent import JudgeAgent, fallback_verdict
from debate_ai.constants import EnvelopeKind
from debate_ai.memory.context_builder import ContextBuilder
from debate_ai.memory.conversation_memory import ConversationMemory
from debate_ai.models.config_models import JudgeConfig
from debate_ai.models.debate_models import ScoreAggregate
from debate_ai.models.message_models import DebaterReply, TurnScore
from debate_ai.shared.exceptions import SchemaError, VerdictTieError
from debate_ai.shared.gatekeeper import Gatekeeper
from tests.unit.test_base_agent import _agent_model_cfg


def _jcfg() -> JudgeConfig:
    return JudgeConfig(
        verdict_no_tie_retries=2, drift_window_turns=3,
        agreement_keywords=["agree", "correct"],
    )


def _gk_call(fn, *a, model="unknown", source="anthropic", **kw):
    return fn(*a, **kw)


def _ctx(client: MagicMock):
    gk = MagicMock(spec=Gatekeeper)
    gk.call = MagicMock(side_effect=_gk_call)
    from debate_ai.agents.base_agent import AgentContext
    return AgentContext(
        role="judge", config=_agent_model_cfg(cache_system=True),
        default_betas=["skills-2025-10-02"], gatekeeper=gk,
        memory=ConversationMemory("test-debate", "Messi vs Ronaldo"),
        context_builder=ContextBuilder(),
        anthropic_client=client,
    )


def _reply() -> DebaterReply:
    return DebaterReply(
        argument="Messi's 8 Ballon d'Ors are unmatched in history.",
        confidence=0.9, attack_points=["CL is a club metric"],
        defense_points=["8 BdO"], citations=["https://example.com"],
        references_opponent="you said Ronaldo's CL record",
    )


def test_relay_creates_envelope() -> None:
    judge = JudgeAgent(_ctx(MagicMock()), _jcfg())
    env = judge.relay(
        sender="debater-a", recipient="debater-b",
        kind=EnvelopeKind.REBUTTAL, payload={"arg": "test"}, round_index=3,
    )
    assert env.sender == "debater-a"
    assert env.recipient == "debater-b"
    assert env.round == 3


def test_score_turn_valid(mock_anthropic_client: MagicMock) -> None:
    score_payload = {"logic": 8, "evidence": 7, "persuasion": 9, "counter": 6}
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input=score_payload)]
    response.usage = MagicMock(input_tokens=10, output_tokens=20)
    mock_anthropic_client.beta.messages.create.return_value = response
    judge = JudgeAgent(_ctx(mock_anthropic_client), _jcfg())
    ts = judge.score_turn(_reply())
    assert isinstance(ts, TurnScore)
    assert ts.total() == 30.0


def test_score_turn_invalid_schema(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"bad": 1})]
    response.usage = MagicMock(input_tokens=5, output_tokens=5)
    mock_anthropic_client.beta.messages.create.return_value = response
    judge = JudgeAgent(_ctx(mock_anthropic_client), _jcfg())
    with pytest.raises(SchemaError):
        judge.score_turn(_reply())


def test_verdict_tie_retry_exhausted(mock_anthropic_client: MagicMock) -> None:
    response = MagicMock()
    response.content = [MagicMock(type="tool_use", input={"bad": True})]
    response.usage = MagicMock(input_tokens=5, output_tokens=5)
    mock_anthropic_client.beta.messages.create.return_value = response
    judge = JudgeAgent(_ctx(mock_anthropic_client), _jcfg())
    sb = ScoreAggregate()
    with pytest.raises(VerdictTieError):
        judge.verdict(sb)


def test_fallback_verdict_breaks_tie() -> None:
    sb = ScoreAggregate()
    sb.a_logic = 10
    sb.b_logic = 10
    sb.a_persuasion = 5
    sb.b_persuasion = 5
    v = fallback_verdict(sb, "Forced verdict from aggregate scores.")
    assert v.score_a != v.score_b
    assert v.winner in ("debater-a", "debater-b")


def test_fallback_verdict_clear_winner() -> None:
    sb = ScoreAggregate()
    sb.a_logic = 20
    sb.b_logic = 10
    v = fallback_verdict(sb, "x" * 35)
    assert v.winner == "debater-a"
    assert v.score_a > v.score_b
