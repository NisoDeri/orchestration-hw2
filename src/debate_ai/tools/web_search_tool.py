"""Web-search tool wrapper.

Default provider is Anthropic's built-in ``web_search`` server tool: we don't
make our own HTTP call — we just emit the right ``tools`` + ``tool_choice``
block for the Anthropic Messages API request, and Anthropic does the search
server-side. The model receives a ``web_search_tool_result`` content block
which the agent parses into ``Citation`` objects.

Fallback providers (Tavily / Exa) are wired the same way: the Gatekeeper sees
the same uniform ``search(query)`` surface; only the implementation differs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from debate_ai.models.config_models import RateLimitsConfig


class Citation(BaseModel):
    """One URL + snippet + title returned by a web search."""

    model_config = ConfigDict(extra="forbid")
    url: str
    title: str = ""
    snippet: str = ""


def anthropic_builtin_tool_spec(max_uses: int = 3) -> dict[str, Any]:
    """Return the ``tools`` element a debater should include in their request."""
    return {"type": "web_search_20260209", "name": "web_search", "max_uses": max_uses}


def web_fetch_tool_spec(max_uses: int = 2) -> dict[str, Any]:
    """Return the ``web_fetch`` server-tool spec used by the Judge."""
    return {"type": "web_fetch_20250910", "name": "web_fetch", "max_uses": max_uses}


def build_tools_for_role(role: str, rl_cfg: RateLimitsConfig | None = None) -> list[dict]:
    """Return the per-agent tool list per ``config/models.json`` semantics.

    Debaters: ``web_search``. Judge + Fact-Checker: ``web_search`` for ad-hoc
    probes plus ``web_fetch`` for citation verification.
    """
    provider = rl_cfg.web_search_provider if rl_cfg else "anthropic_builtin"
    if provider != "anthropic_builtin":
        # Fallback providers do NOT use server-side tools — the agent emits a
        # client-side function call which our gatekeeper handles. Returning
        # an empty list signals "no server tool"; the agent's prompt is
        # adjusted accordingly.
        return []
    if role in {"debater-a", "debater-b"}:
        return [anthropic_builtin_tool_spec()]
    if role in {"judge", "fact-checker"}:
        return [anthropic_builtin_tool_spec(max_uses=2), web_fetch_tool_spec()]
    return []


def parse_citations(content_blocks: list[Any]) -> list[Citation]:
    """Parse Anthropic ``web_search_tool_result`` blocks into ``Citation``s.

    ``content_blocks`` is the ``response.content`` list from the Anthropic SDK.
    Non-search blocks are ignored. Returns an empty list if nothing was found.
    """
    citations: list[Citation] = []
    for block in content_blocks:
        kind = _get(block, "type")
        if kind != "web_search_tool_result":
            continue
        for hit in _get(block, "content", []) or []:
            citations.append(
                Citation(
                    url=_get(hit, "url", ""),
                    title=_get(hit, "title", ""),
                    snippet=_get(hit, "snippet", ""),
                )
            )
    return citations


def _get(obj: Any, attr: str, default: Any = None) -> Any:
    """Unified attribute access — works for SDK objects (attrs) and dicts."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


class SearchRequest(BaseModel):
    """Used by fallback providers (Tavily/Exa) where we issue the HTTP call."""

    model_config = ConfigDict(extra="forbid")
    query: str
    max_results: int = Field(5, ge=1, le=20)
