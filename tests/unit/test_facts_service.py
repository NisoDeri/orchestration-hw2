"""Tests for ``services.facts_service``."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate_ai.models.config_models import FactsConfig
from debate_ai.services.facts_service import FactsService


def _cfg(lookup_order: list[str] | None = None) -> FactsConfig:
    return FactsConfig.model_validate({
        "version": "1.00",
        "lookup_order": lookup_order or ["facts_json", "wikipedia_mcp", "web_search"],
        "claims": {
            "ballon_dor_count_messi": {
                "value": 8, "as_of": "2024",
                "source": "https://francefootball.fr",
                "severity_on_mismatch": 0.6,
            },
            "champions_league_titles_ronaldo": {
                "value": 5, "as_of": "2024",
                "source": "https://uefa.com",
                "severity_on_mismatch": 0.5,
            },
        },
        "patterns": [
            {"regex": r"Messi\s+has\s+(\d+)\s+Ballon d'Ors?", "claim_id": "ballon_dor_count_messi"},
            {"regex": r"Ronaldo\s+won\s+(\d+)\s+Champions League titles?",
             "claim_id": "champions_league_titles_ronaldo"},
        ],
    })


def test_extract_finds_claims() -> None:
    svc = FactsService(_cfg(), wikipedia=MagicMock(available=lambda: False))
    claims = svc.extract_checkable_claims("Messi has 8 Ballon d'Ors")
    assert len(claims) == 1
    assert claims[0].captured_value == "8"


def test_extract_no_match_returns_empty() -> None:
    svc = FactsService(_cfg(), wikipedia=MagicMock(available=lambda: False))
    assert svc.extract_checkable_claims("Football is fun") == []


def test_verify_correct_claim_local() -> None:
    svc = FactsService(_cfg(), wikipedia=MagicMock(available=lambda: False))
    claims = svc.extract_checkable_claims("Messi has 8 Ballon d'Ors")
    anno = svc.verify(claims[0])
    assert anno.verdict == "correct"
    assert anno.severity == 0.0
    assert anno.source_kind == "facts_json"


def test_verify_incorrect_claim_local() -> None:
    svc = FactsService(_cfg(), wikipedia=MagicMock(available=lambda: False))
    claims = svc.extract_checkable_claims("Messi has 7 Ballon d'Ors")
    anno = svc.verify(claims[0])
    assert anno.verdict == "incorrect"
    assert anno.severity == 0.6
    assert anno.actual is not None
    assert "8" in anno.actual


def test_verify_unverifiable_when_no_pattern_matches() -> None:
    # Construct a claim by hand for a claim_id we don't know.
    from debate_ai.services.facts_service import CheckableClaim
    svc = FactsService(_cfg(), wikipedia=MagicMock(available=lambda: False))
    anno = svc.verify(CheckableClaim(quote="x", claim_id="unknown_claim", captured_value="42"))
    assert anno.verdict == "unverifiable"


def test_verify_falls_through_to_wikipedia_when_local_misses() -> None:
    cfg = _cfg(lookup_order=["facts_json", "wikipedia_mcp"])
    wiki = MagicMock()
    wiki.available.return_value = True
    wiki.summary.return_value = {"extract": "found"}
    svc = FactsService(cfg, wikipedia=wiki)
    from debate_ai.services.facts_service import CheckableClaim
    anno = svc.verify(CheckableClaim(quote="x", claim_id="unknown_claim", captured_value="42"))
    assert anno.source_kind == "wikipedia_mcp"
    assert anno.verdict == "misleading"


def test_verify_unverifiable_when_wikipedia_unavailable() -> None:
    cfg = _cfg(lookup_order=["wikipedia_mcp"])
    wiki = MagicMock()
    wiki.available.return_value = False
    svc = FactsService(cfg, wikipedia=wiki)
    from debate_ai.services.facts_service import CheckableClaim
    anno = svc.verify(CheckableClaim(quote="x", claim_id="unknown", captured_value="0"))
    assert anno.verdict == "unverifiable"
