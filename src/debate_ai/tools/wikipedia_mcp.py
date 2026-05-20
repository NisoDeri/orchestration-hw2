"""Wikipedia MCP wrapper — used by the Fact-Checker as priority-2 source.

The MCP server is launched via ``uvx wikipedia-mcp`` as a stdio subprocess
on demand. We keep a single shared subprocess across the debate to avoid
spawn cost. If the subprocess is unavailable (uvx missing, package not
installable), the wrapper silently degrades to returning ``None`` and the
Fact-Checker falls through to its next priority source.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class WikipediaMCPUnavailableError(RuntimeError):
    """Raised when uvx / the wikipedia-mcp package is not installable."""


class WikipediaMCP:
    """Tiny stdio JSON-RPC client for the Wikipedia MCP server.

    This is a deliberately simple implementation: each call spawns the
    subprocess fresh, sends one request, reads one response. Faster designs
    keep the subprocess alive across calls; we trade ~200ms per call for
    process-management simplicity.
    """

    def __init__(self, command: str = "uvx", package: str = "wikipedia-mcp") -> None:
        self.command = command
        self.package = package

    def available(self) -> bool:
        """True iff ``uvx`` is on PATH (the MCP can at least be attempted)."""
        return shutil.which(self.command) is not None

    def summary(self, title: str) -> dict[str, Any] | None:
        """Return the summary for an article, or ``None`` if not found / error."""
        return self._call_tool("summary", {"title": title})

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """Search article titles. Returns ``[]`` on any error."""
        result = self._call_tool("search", {"query": query, "limit": limit})
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "results" in result:
            return list(result["results"])
        return []

    def _call_tool(self, tool: str, args: dict[str, Any]) -> Any | None:
        if not self.available():
            return None
        request = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
        try:
            proc = subprocess.run(  # noqa: S603
                [self.command, self.package],
                input=(json.dumps(request) + "\n").encode("utf-8"),
                capture_output=True,
                timeout=15,
                check=False,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
        try:
            response = json.loads(proc.stdout.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            return None
        return response.get("result")
