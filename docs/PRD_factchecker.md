# PRD — Fact-Checker

**Version**: 1.00 · Viewer-only claim annotator. The judge ignores it; the human watching the UI uses it.

## 1. Why viewer-only

Per HW2 brief §8.3.6 + §9, the judge scores **persuasion, not factual correctness**, and **lies are explicitly allowed**. So the Fact-Checker:

- Does **not** feed the judge.
- Does **not** affect any score.
- Is purely an audience aid for the human watching the chat UI.
- Gives the user (and lecturer) something interesting to read alongside the debate.

This is the locked rule per memory `feedback-judge-verdict-rule`.

## 2. Trigger

After every debater envelope is relayed by the judge, the orchestrator dispatches the same envelope's `argument` text to the Fact-Checker. The FC produces a `FactCheckReply` which becomes a `UIEvent(kind="fact_check", ...)`.

## 3. JSON contract

```json
{
  "envelope_ref": "uuid-of-debater-envelope",
  "claims": [
    {
      "quote": "Messi has 7 Ballon d'Ors",
      "verdict": "incorrect" | "correct" | "misleading" | "unverifiable",
      "severity": 0.0 - 1.0,
      "actual": "Messi has 8 Ballon d'Ors as of 2024.",
      "source_kind": "facts_json" | "wikipedia_mcp" | "web_search",
      "source_ref": "facts.json#ballon_dor_counts" | "https://..."
    }
  ]
}
```

Multiple claims per turn are allowed. If no claim is checkable, `claims: []`.

## 4. Data sources (in priority order)

1. **`config/facts.json`** — handcrafted knowledge base for the default personas (Messi, Ronaldo, …). Cheap, deterministic. Examples: `ballon_dor_counts`, `world_cups`, `champions_league_titles`. Tests rely on this.
2. **Wikipedia MCP** (`uvx wikipedia-mcp`) — free, no auth, structured. Looked up when the claim falls outside facts.json.
3. **Anthropic `web_search`** — last resort. Costly. Only used when 1 and 2 miss.

This priority is in `config/facts.json::lookup_order` so it can be reordered or pruned without a code change.

## 5. UI rendering

A `kind: "fact_check"` event renders below the debater bubble as a chip:

```
⚠ Fact-Checker — Messi has 8 Ballon d'Ors (debater said 7). Source: facts.json
```

Color-coded by `severity`:
- `0.0 – 0.3` → grey chip (`misleading`, low stakes)
- `0.3 – 0.7` → yellow chip
- `0.7 – 1.0` → red chip (clear contradiction)

Correct claims do not render a chip (no clutter for accurate statements).

## 6. The agent itself

```python
class FactCheckerAgent(BaseAgent, JsonReplyMixin, SkillBoundMixin):
    skill_id = "claim-verification"
    facts: FactsService

    def respond(self, envelope: JudgeEnvelope) -> FactCheckReply:
        claims = self.facts.extract_checkable_claims(envelope.payload["argument"])
        results = [self.facts.verify(c) for c in claims]
        return FactCheckReply(envelope_ref=envelope.envelope_id, claims=results)
```

`FactsService.verify` walks `lookup_order`. The first source that returns a non-`unverifiable` result wins; otherwise the claim is marked `unverifiable`.

## 7. Tests

- `test_factchecker_priority.py` — facts.json hit short-circuits before Wikipedia / web_search.
- `test_factchecker_misleading.py` — partially-true claims classified `misleading`, severity ∈ [0.3, 0.7).
- `test_factchecker_does_not_score.py` — judge's `score_turn` output is byte-identical whether or not a fact-check event was emitted.
- `test_factchecker_ui_render.py` — `kind: "fact_check"` event maps to a chip with the right severity color.
