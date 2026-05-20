# PRD — Color Crew (Commentator + Crowd)

**Version**: 1.00 · Two flavor agents. Neither scores. Both make the UI feel alive.

## 1. Commentator

A single sports-style commentator who drops one short line **between rounds**.

### When it fires

Right after `kind: "round_changed"` is emitted, and right after the verdict (one closing line).

### Contract

```json
{
  "commentary": "Ronaldo just landed a haymaker on the 2008 Champions League run...",
  "tone": "neutral" | "favouring_a" | "favouring_b",
  "round_ref": 3
}
```

`tone` is a soft signal for UI styling (italic vs bold), not for scoring.

### Skill

`color-commentary` — instructs: "One sentence. Evocative, not analytical. Never declare a winner. Reference the just-finished round specifically."

### Length cap

Hard-cap `max_tokens=80`. Violations clipped, not retried.

## 2. Crowd

A composite "audience" agent that drops a quick reaction **after every debater turn**.

### When it fires

Right after `kind: "agent_message"` with `from in {"debater-a", "debater-b"}`.

### Contract

```json
{
  "envelope_ref": "uuid",
  "emojis": ["🔥", "🔥", "🔥"],
  "one_liner": "they're going for it",
  "lean": -1.0..1.0
}
```

- `emojis`: 1–5 of them, the UI renders them inline.
- `one_liner`: ≤ 8 words. Casual register.
- `lean`: which side the crowd is leaning toward this turn (-1 = strongly A, +1 = strongly B).

### Skill

`audience-sentiment` — instructs: "React, don't analyze. Emojis first. One short sentence."

### Bias drift

To avoid the crowd parroting the judge's running score, the Crowd agent does **not** receive the scoreboard in its context (per `PRD_memory.md` visibility rules). It only sees the latest debater envelope.

## 3. They never score

Hard rule. The orchestrator's `score_turn` ignores Commentator and Crowd envelopes entirely. A unit test asserts that running aggregate is byte-identical whether or not these two agents are enabled.

## 4. Toggling on/off

Both are individually toggleable in `config/setup.json`:

```json
{
  "agents_enabled": {
    "commentator": true,
    "crowd": true,
    "fact_checker": true
  }
}
```

Disabling them is the brief-minimum mode — 3-agent debate. Default ships them all on.

## 5. Tests

- `test_commentator_one_line.py` — output ≤ 1 sentence.
- `test_commentator_no_winner_claim.py` — output never contains "wins" / "loses" / verdict language.
- `test_crowd_emojis_count.py` — `1 ≤ len(emojis) ≤ 5`.
- `test_color_crew_never_scores.py` — `ScoreAggregate` identical with crew on vs off.
- `test_crowd_sees_only_latest_envelope.py` — context window has exactly 1 debater envelope.
