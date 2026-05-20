# PRD — Judge

**Version**: 1.00 · The Judge is the system's most important agent. It is router + scorer + verdict-issuer.

## 1. Two responsibilities, one class

`JudgeAgent` does two things that elsewhere would be split — and the brief explicitly mandates this coupling:

1. **Routing.** Every debater turn is sent *to the judge*. The judge wraps it in a `JudgeEnvelope` and relays it to the opponent. Debaters never see each other directly.
2. **Scoring + verdict.** As the judge relays, it scores each turn against the rubric and updates a running aggregate. After the closing turn, it emits exactly one `Verdict` — no ties.

These cannot be split into two classes because the scoring of turn N depends on the judge having *just* read the relayed text; splitting would require re-reading.

## 2. The Judge does NOT know the topic

Per brief §9 ("Does the judge need to know the topic? No"). The judge's system prompt describes only:

- The structure of a debate (opening, rebuttals, era-swap, closing).
- The rubric: `Logic | Evidence-as-rhetoric | Persuasiveness | Counter-arg quality`.
- The contract that it scores **rhetoric, not facts**.
- The relay protocol.
- The no-tie rule.

The motion text appears only in the envelope payload, *as relayed material*. The judge treats it as a sealed envelope topic, scoring how each side argues without taking a position. This is the lecturer's stated reason: a judge ignorant of the topic is harder to bias.

## 3. Routing protocol

```
debater-a.respond() ─▶ judge.relay(from="debater-a", to="debater-b", payload=DebaterReply)
                       │
                       ├─ judge.score_turn(payload) ─▶ running_aggregate
                       │
                       └─ JudgeEnvelope(round, kind, from, to, payload) ─▶ debater-b
```

`JudgeEnvelope` is the unit of every relayed message. Schema:
```json
{
  "envelope_id": "uuid",
  "round": 3,
  "kind": "opening" | "rebuttal" | "era_swap" | "closing" | "ruling",
  "from": "debater-a",
  "to": "debater-b" | "all",
  "payload": { "<DebaterReply | CommentaryReply | CrowdReply | FactCheckReply | Verdict>": "..." },
  "ts": "2026-05-20T..."
}
```

Routing rules:
- `from=debater-a → to=debater-b` and vice versa.
- `from=judge → to=all` for openings, era-swap announcement, closing, verdict.
- `from=commentator | crowd | fact-checker → to=all` (broadcast for UI; debaters ignore them).

## 4. Scoring rubric (rhetoric, not facts)

Per turn, the judge scores the **rhetorical quality** of a debater's reply on four dimensions, each 0–10:

| Dimension | Rewards | Does NOT reward |
| --- | --- | --- |
| **Logic** | Coherent argumentation, clean inference chain | Whether premises are factually true |
| **Evidence-as-rhetoric** | How convincingly evidence is wielded — invoked specifically, anchored to claim | Whether the cited stat is real |
| **Persuasiveness** | Vivid language, memorable framing, emotional resonance, **catching the opponent's lies** | Politeness, neutrality |
| **Counter-arg quality** | Directly addresses opponent's most recent attack, names it, dismantles it | Length of rebuttal |

**Per-turn score**: `TurnScore(logic, evidence, persuasion, counter)` — four 0–10 floats.

**Running aggregate**: sum across all turns for that debater. Era-swap turns count identically (no special weight).

**Lie-catching bonus**: if a debater's reply contains `attack_points` that demonstrably reference a (potentially false) claim the opponent made and `references_opponent` quotes it, the **Persuasion** score for that turn gets a +1 floor. Implemented as a deterministic check in `scoring_service`, NOT delegated to the judge LLM — keeps lie-catching credit consistent.

## 5. Verdict contract

```json
{
  "winner": "debater-a" | "debater-b",
  "score_a": 78,
  "score_b": 72,
  "reasoning": "Debater-A scored higher on Persuasion and Counter-arg quality...",
  "rubric_breakdown": {
    "debater-a": {"logic": 19, "evidence": 17, "persuasion": 23, "counter": 19},
    "debater-b": {"logic": 18, "evidence": 19, "persuasion": 18, "counter": 17}
  }
}
```

Pydantic validator: **`score_a != score_b`** — equality raises. The orchestrator catches that:

1. First tie → retry verdict prompt with explicit "differentiate by ≥ 1 point" instruction.
2. Second tie → fall back to running-aggregate winner from per-turn scores (deterministic, no LLM call).

This guarantees the brief's no-tie rule even if the judge LLM is stubborn.

## 6. Prompt caching strategy

The judge's transcript grows with every turn. To cut tokens:

```python
system=[
    {"type": "text",
     "text": judge_system_prompt + rubric_text,
     "cache_control": {"type": "ephemeral"}},        # static, cached
    {"type": "text",
     "text": format_transcript(state.history[:-1]),
     "cache_control": {"type": "ephemeral"}},        # grows, but prefix cacheable across turns
]
messages=[{"role": "user", "content": format_envelope(state.history[-1])}]
```

The static prompt + rubric is cached on the first turn; the transcript prefix grows monotonically so each new turn extends rather than invalidates the cache. Expected 41–80 % token reduction on the judge — documented in Anthropic's caching guide.

## 7. Drift detector

Brief §9 says one-off mid-debate agreement is OK but sustained agreement is "drift" and the judge must intervene. Concrete rule:

- If both debaters' `references_opponent` quotes contain agreement keywords (`"yes,"`, `"true,"`, `"correct,"`, `"agreed"`, etc.) for **two consecutive turns**, the judge emits a `kind: "ruling"` envelope with `payload: { "directive": "re-anchor", "message": "Debaters: return to your assigned positions." }` before the next round.

Implemented in `services/scoring_service.py::detect_drift`, not in the LLM call — deterministic, testable.

## 8. Tests

- `test_judge_routing.py` — every relayed envelope goes to the *other* debater.
- `test_judge_no_tie.py` — judge emits a tie → orchestrator retries, second tie → falls back to aggregate.
- `test_judge_topic_ignorance.py` — judge system prompt does not contain the motion text.
- `test_judge_scoring_lies_allowed.py` — feed the judge a debater who lied, opponent who caught it: catcher gets +1 Persuasion floor; liar's score is *not* deducted.
- `test_judge_drift_detector.py` — two consecutive agreement turns trigger a re-anchor ruling.
- `test_judge_prompt_cache.py` — second turn's request has `cache_control` on the static prefix.
