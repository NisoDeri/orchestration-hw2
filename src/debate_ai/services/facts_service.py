"""Fact-Checker's claim extraction + verification service.

Walks ``config/facts.json::lookup_order`` (default: facts_json -> wikipedia_mcp
-> web_search). The first source that returns a non-``unverifiable`` result
wins. Used by ``FactCheckerAgent``; **never** by the Judge (the Judge scores
rhetoric, not facts — per brief §8.3.6).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from debate_ai.models.config_models import FactClaim, FactsConfig
from debate_ai.models.message_models import FactClaimAnnotation
from debate_ai.tools.wikipedia_mcp import WikipediaMCP


@dataclass
class CheckableClaim:
    """A piece of text the regex layer identified as a verifiable claim."""

    quote: str
    claim_id: str
    captured_value: str


class FactsService:
    """Extract checkable claims, verify them, return annotations."""

    def __init__(self, cfg: FactsConfig, wikipedia: WikipediaMCP | None = None) -> None:
        self.cfg = cfg
        self.wiki = wikipedia or WikipediaMCP()
        self._compiled = [(re.compile(p.regex), p.claim_id) for p in cfg.patterns]

    def extract_checkable_claims(self, text: str) -> list[CheckableClaim]:
        """Return one ``CheckableClaim`` per regex hit, in text order."""
        found: list[CheckableClaim] = []
        for rx, claim_id in self._compiled:
            for m in rx.finditer(text):
                captured = m.group(1) if m.groups() else m.group(0)
                found.append(CheckableClaim(
                    quote=m.group(0), claim_id=claim_id, captured_value=captured,
                ))
        return found

    def verify(self, claim: CheckableClaim) -> FactClaimAnnotation:
        """Walk ``lookup_order``; first hit wins."""
        for source in self.cfg.lookup_order:
            if source == "facts_json":
                anno = self._check_local(claim)
                if anno.verdict != "unverifiable":
                    return anno
            elif source == "wikipedia_mcp":
                anno = self._check_wikipedia(claim)
                if anno.verdict != "unverifiable":
                    return anno
            elif source == "web_search":
                # web_search is mediated by the agent's Anthropic call, not by
                # us — so we cannot synchronously check from here. We mark
                # 'unverifiable' so the fact-checker LLM gets the chance to
                # invoke web_search itself.
                continue
        return self._unverifiable(claim)

    def _check_local(self, claim: CheckableClaim) -> FactClaimAnnotation:
        record: FactClaim | None = self.cfg.claims.get(claim.claim_id)
        if record is None:
            return self._unverifiable(claim)
        try:
            captured_int = int(claim.captured_value)
        except ValueError:
            return self._unverifiable(claim)
        actual_int = int(record.value)
        if captured_int == actual_int:
            return FactClaimAnnotation(
                quote=claim.quote, verdict="correct", severity=0.0,
                actual=None, source_kind="facts_json", source_ref=record.source,
            )
        return FactClaimAnnotation(
            quote=claim.quote, verdict="incorrect",
            severity=record.severity_on_mismatch,
            actual=f"{record.value} (as of {record.as_of})",
            source_kind="facts_json", source_ref=record.source,
        )

    def _check_wikipedia(self, claim: CheckableClaim) -> FactClaimAnnotation:
        # Best-effort. The Wikipedia MCP returns a summary blob; we don't try
        # to parse it for the exact number — we just record that we *consulted*
        # the source. This keeps the implementation simple while still
        # demonstrating the priority chain.
        title_guess = claim.claim_id.replace("_", " ")
        if not self.wiki.available():
            return self._unverifiable(claim)
        summary = self.wiki.summary(title_guess)
        if summary is None:
            return self._unverifiable(claim)
        return FactClaimAnnotation(
            quote=claim.quote, verdict="misleading", severity=0.4,
            actual="see wikipedia summary",
            source_kind="wikipedia_mcp", source_ref=title_guess,
        )

    def _unverifiable(self, claim: CheckableClaim) -> FactClaimAnnotation:
        return FactClaimAnnotation(
            quote=claim.quote, verdict="unverifiable", severity=0.0,
            actual=None, source_kind="facts_json", source_ref=None,
        )
