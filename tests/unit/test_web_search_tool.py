"""Tests for ``tools.web_search_tool``."""

from __future__ import annotations

from debate_ai.models.config_models import RateLimitsConfig
from debate_ai.tools.web_search_tool import (
    Citation,
    anthropic_builtin_tool_spec,
    build_tools_for_role,
    parse_citations,
    web_fetch_tool_spec,
)


def _rl(provider: str = "anthropic_builtin") -> RateLimitsConfig:
    return RateLimitsConfig.model_validate({
        "version": "1.00", "web_search_provider": provider,
        "anthropic": {"max_requests_per_second": 10.0, "max_concurrent": 4,
                      "queue_max_depth": 64, "queue_max_block_s": 5.0},
        "retry_policy": {"max_retries": 1, "backoff_base_s": 0.01,
                         "backoff_factor": 2.0, "backoff_max_s": 0.1,
                         "retry_on_status": [500]},
        "cost_caps": {"max_cost_usd_per_debate": 10.0, "search_cost_usd_per_use": 0.01},
    })


def test_builtin_tool_spec_shape() -> None:
    spec = anthropic_builtin_tool_spec(max_uses=3)
    assert spec["type"] == "web_search_20260209"
    assert spec["name"] == "web_search"
    assert spec["max_uses"] == 3


def test_web_fetch_tool_spec_shape() -> None:
    spec = web_fetch_tool_spec()
    assert spec["type"] == "web_fetch_20250910"
    assert spec["name"] == "web_fetch"


def test_build_tools_debater_gets_web_search() -> None:
    tools = build_tools_for_role("debater-a", _rl())
    assert len(tools) == 1
    assert tools[0]["name"] == "web_search"


def test_build_tools_judge_gets_search_and_fetch() -> None:
    tools = build_tools_for_role("judge", _rl())
    names = [t["name"] for t in tools]
    assert "web_search" in names
    assert "web_fetch" in names


def test_build_tools_fallback_provider_yields_empty() -> None:
    tools = build_tools_for_role("debater-a", _rl(provider="tavily"))
    assert tools == []


def test_build_tools_color_crew_gets_nothing() -> None:
    assert build_tools_for_role("commentator", _rl()) == []
    assert build_tools_for_role("crowd", _rl()) == []


def test_parse_citations_extracts_url_title_snippet() -> None:
    fake_response_content = [
        {"type": "text", "text": "thinking..."},
        {"type": "web_search_tool_result", "content": [
            {"url": "https://example.com/a", "title": "A", "snippet": "ay"},
            {"url": "https://example.com/b", "title": "B", "snippet": "bee"},
        ]},
    ]
    cites = parse_citations(fake_response_content)
    assert len(cites) == 2
    assert cites[0] == Citation(url="https://example.com/a", title="A", snippet="ay")


def test_parse_citations_handles_empty() -> None:
    assert parse_citations([]) == []
    assert parse_citations([{"type": "text", "text": "no search"}]) == []
