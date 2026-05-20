"""Tests for ``tools.wikipedia_mcp``."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from debate_ai.tools.wikipedia_mcp import WikipediaMCP


def test_available_true_when_uvx_on_path() -> None:
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value="/usr/bin/uvx"):
        assert WikipediaMCP().available() is True


def test_available_false_when_uvx_missing() -> None:
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value=None):
        assert WikipediaMCP().available() is False


def test_summary_returns_none_when_unavailable() -> None:
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value=None):
        assert WikipediaMCP().summary("Lionel Messi") is None


def test_summary_returns_result_field_on_success() -> None:
    fake_stdout = b'{"jsonrpc": "2.0", "id": 1, "result": {"title": "Messi", "extract": "..."}}\n'
    completed = MagicMock(stdout=fake_stdout, returncode=0)
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value="/usr/bin/uvx"), \
         patch("debate_ai.tools.wikipedia_mcp.subprocess.run", return_value=completed):
        wiki = WikipediaMCP()
        result = wiki.summary("Lionel Messi")
        assert result == {"title": "Messi", "extract": "..."}


def test_summary_handles_malformed_json() -> None:
    completed = MagicMock(stdout=b"not json", returncode=0)
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value="/usr/bin/uvx"), \
         patch("debate_ai.tools.wikipedia_mcp.subprocess.run", return_value=completed):
        assert WikipediaMCP().summary("anything") is None


def test_search_returns_empty_on_unavailable() -> None:
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value=None):
        assert WikipediaMCP().search("messi") == []


def test_search_returns_list_when_provided_directly() -> None:
    fake = b'{"jsonrpc": "2.0", "id": 1, "result": [{"title": "Messi"}]}\n'
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value="/usr/bin/uvx"), \
         patch("debate_ai.tools.wikipedia_mcp.subprocess.run",
               return_value=MagicMock(stdout=fake)):
        out = WikipediaMCP().search("messi")
        assert out == [{"title": "Messi"}]


def test_search_returns_results_key_when_nested() -> None:
    fake = b'{"jsonrpc": "2.0", "id": 1, "result": {"results": [{"title": "X"}]}}\n'
    with patch("debate_ai.tools.wikipedia_mcp.shutil.which", return_value="/usr/bin/uvx"), \
         patch("debate_ai.tools.wikipedia_mcp.subprocess.run",
               return_value=MagicMock(stdout=fake)):
        assert WikipediaMCP().search("x") == [{"title": "X"}]
