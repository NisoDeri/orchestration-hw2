# PRD — Era-swap round

**Version**: 1.00 · One designated round per debate forces both debaters into a specific era of their persona.

## 1. The mechanic

One round per debate is marked `kind: "era_swap"`. For that round and that round only, both debaters argue as a specific era version of themselves: e.g. *2009 Messi vs 2013 Ronaldo*, or *2007-Python (no async/await) vs 2015-JavaScript (pre-ES6 still common)*.

It is **a flavor variation**, not a verdict track. Scores from era-swap turns feed the same aggregate as every other round (per memory `feedback-judge-verdict-rule`).

## 2. Why include it

- Differentiation: no other submission will have this.
- Creates a narrative arc — the era-swap is the "trick round" the judge announces beforehand.
- Stresses the engine's generic-ness: any persona can declare eras; the orchestrator picks one.

## 3. Where eras live

In each persona JSON:

```json
{
  "name": "Messi",
  "eras": [
    { "label": "2009",       "system_addendum": "You are 2009 Messi: ascendant, Pep's Barcelona, untouchable in tight space..." },
    { "label": "2014-WC",    "system_addendum": "You are 2014 Messi: golden ball but final lost..." },
    { "label": "2022-postWC","system_addendum": "You are 2022 Messi: validated, World Cup winner, complete..." }
  ]
}
```

A persona with no `eras` cannot participate in an era-swap round. The orchestrator falls back to a normal round in that case (warning logged).

## 4. Round index

`config/setup.json::era_swap_round_index` (default: 4, i.e. the 4th of 5 rounds). `null` disables the mechanic entirely. The judge announces the swap one round in advance.

## 5. Picking the era

`orchestration/era_swap.py::EraSwap.pick(persona)`:

- Default strategy: `"random"` — uniform random from `persona.eras`.
- Other strategies allowed via `config/setup.json::era_swap_strategy`:
  - `"first"` — always the earliest era listed.
  - `"latest"` — always the most recent.
  - `"contrasting"` — picks the era with the largest temporal distance from the opponent's chosen era (e.g. *2009 Messi vs 2018 Ronaldo*).

## 6. Mechanics during the round

```
DebateManager → RoundManager(kind=era_swap):
  1. Pick eras: era_a = EraSwap.pick(persona_a), era_b = EraSwap.pick(persona_b)
  2. Judge announces: "This round both debaters argue as their <era_a.label> and <era_b.label> versions."
  3. Set debater_a.current_era = era_a, debater_b.current_era = era_b.
  4. Run the pings as normal — debaters' system prompts now include the era addendum.
  5. Reset current_era = None at round end.
```

`current_era` only affects the system prompt; the JSON contract, scoring, and routing are unchanged.

## 7. Tests

- `test_era_swap_index.py` — only round `era_swap_round_index` is marked era_swap; others are normal.
- `test_era_swap_strategy_contrasting.py` — picks furthest-apart eras given a set of labels with years.
- `test_era_swap_falls_back.py` — persona without `eras` array → falls back to normal round, warning logged.
- `test_era_swap_scoring_same_aggregate.py` — TurnScores from era_swap round are added to the same `ScoreAggregate`, no separate counter.
- `test_era_swap_system_prompt_addendum.py` — during era_swap, the debater's effective system prompt contains the era's `system_addendum`.
