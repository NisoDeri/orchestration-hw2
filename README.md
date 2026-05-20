# debate-ai — Messi vs Ronaldo, settled by Claude

> **HW2, Orchestration course** (Dr. Yoram Segal). Two Anthropic Claude agents debate *"Who is the greatest footballer of all time: Lionel Messi or Cristiano Ronaldo?"* under the supervision of a third Claude agent who scores and declares a winner. Topic and personas are hardcoded; the prompts that drive each agent live in JSON so they can be tuned without code edits.

---

## 1. What it is

Three primary agents — a **Judge** (father / orchestrator), and two debaters (**MessiAgent**, **RonaldoAgent**) — argue the motion. Three supporting agents add color (**Commentator**), audience reactions (**Crowd**), and live claim annotations for the human viewer (**Fact-Checker**). All six are subclasses of one `BaseAgent`. Each agent is bound to a *different* Anthropic **Agent Skill** so the debate doesn't collapse into mutual agreement.

The engine enforces the lecturer's hard rules:

- **Topology**: every utterance routes child → father → child. Debaters never address each other directly.
- **No tie**: the judge must emit a single winner with a differential score.
- **Persuasion ≠ facts**: the judge scores rhetorical quality, not factual correctness. Lies are allowed; the opposing debater is supposed to catch them.
- **Mandatory web search**: debaters cannot reply without invoking Anthropic's built-in `web_search` tool and returning citation URLs.
- **≥10 pings per side** (configurable down to 5 with budget note — `pings_per_side` in `config/setup.json`).
- **Watchdog + keep-alive** on every Anthropic call: stuck agents are killed and restarted.
- **FIFO log rotation** (20 files × 500 lines, config-driven).

## 2. Architecture in one screen

```
                    +---------------------+
                    |        CLI Menu     |  ← canonical test interface
                    +---------+-----------+
                              |
                              v
                    +---------+-----------+      +------------------+
                    |         SDK         |<-----| HTML chat UI     |  ← bonus
                    +---------+-----------+      | (FastAPI + SSE)  |
                              |                  +------------------+
                              v
                    +---------+-----------+
                    |   Debate orchestr.  |  ← rounds, routing, era-swap, watchdog
                    +---------+-----------+
                              |
              +---------------+----------------+
              |               |                |
              v               v                v
        +-----+----+    +-----+----+     +-----+----+
        | Judge    |    | Debater  |     |  Color   |
        | (router  |    | A & B    |     |  Crew    |
        |  +scorer)|    |          |     | Fact-Chk |
        +-----+----+    +-----+----+     +-----+----+
              |               |                |
              +---------------+----------------+
                              |
                              v
                    +---------+-----------+
                    | Anthropic API       |
                    |   + Agent Skills    |
                    |   + web_search      |
                    |   + web_fetch       |
                    |   + prompt caching  |
                    +---------------------+
```

Class diagram: see `docs/architecture.md` (3 Mermaid diagrams: inheritance, orchestration, shared).

## 3. Quickstart

### Option A — Demo mode (no API key, instant)

```powershell
uv sync
uv run debate-ai demo
```

This runs a full 10-round pre-scripted debate through the real orchestration loop (routing, scoring, events, verdict). No API key needed — ideal for verifying the system works on your machine.

### Option B — Live debate with Anthropic API

```powershell
uv sync
cp .env-example .env        # then edit .env and add your ANTHROPIC_API_KEY
uv run debate-ai run        # one-shot debate
uv run debate-ai            # interactive terminal menu
uv run debate-ai start      # launch HTML chat UI (FastAPI + SSE)
```

### Tuning the debater prompts

The motion is fixed (Messi vs Ronaldo). What's tunable without code edits:

- `config/personas/messi.json` — Messi's system prompt, style notes, era variants.
- `config/personas/ronaldo.json` — Ronaldo's system prompt, style notes, era variants.

Edit those files, run again — no rebuild required.

## 4. Configuration

Every tunable is in `config/`:

| File | Controls |
| --- | --- |
| `setup.json` | rounds, pings-per-side, agent enablement, era-swap round index |
| `debate.json` | default motion + persona pair |
| `personas/*.json` | one per debater identity (prompt, style, era variants) |
| `models.json` | Anthropic model + temperature + skill_id + tools per agent role |
| `rate_limits.json` | gatekeeper budgets, queue depth, retry policy |
| `logging.json` | FIFO rotation: file count, lines per file, level |
| `facts.json` | Fact-Checker knowledge base (key claims to check against) |
| `versions.json` | code + per-config version pinning |

All configs are version-validated on startup; mismatch = startup failure.

## 5. Testing

```powershell
uv run pytest            # full suite (213 tests)
uv run pytest --cov      # with coverage (≥85% required, currently 89%)
uv run ruff check        # zero violations
uv run ruff format       # auto-fix
```

External services are mocked in unit tests — no test hits the live Anthropic API.

## 6. Project layout

See `docs/PLAN.md` and `docs/architecture.md` for the authoritative version. Headlines:

```
src/debate_ai/
  sdk/            ← single entry point
  cli/            ← terminal menu (Typer)
  agents/         ← BaseAgent + 6 subclasses + demo agents
  orchestration/  ← debate / round / routing / era-swap / watchdog
  memory/         ← conversation memory + per-agent context windows
  models/         ← Pydantic message + state models
  services/       ← scoring, facts, debate ops, demo service
  tools/          ← web_search wrapper + citation tool
  ui/             ← FastAPI server + SSE + static HTML/CSS/JS
  shared/         ← config, logger (FIFO), gatekeeper, version
  skills/<id>/    ← one Anthropic Agent Skill bundle per agent
config/           ← all tunables
docs/             ← PRDs, PLAN, TODO, architecture, prompts.md
tests/{unit,integration}/
```

## 7. Session 1 — full demo transcript

Below is the complete output of `uv run debate-ai demo` — a 10-ping debate running through the real orchestration engine with pre-scripted agent responses.

```
DEBATE STARTED
Motion: Who is the greatest footballer of all time: Lionel Messi or Cristiano Ronaldo?
Judge scores PERSUASION, not factual correctness.
Topology: Child -> Father -> Child (all messages routed through Judge)

============================================================
  Round 0 — OPENING STATEMENTS
============================================================

  Messi (Pro):
  Lionel Messi has won 8 Ballon d'Or awards — more than any footballer in
  history. This sustained individual recognition across nearly two decades
  proves a level of excellence no other player can claim.
  Judge scores Messi: Logic: 8.5 | Evidence: 7.5 | Persuasion: 9.0 | Counter: 7.0 = 32.0/40

  Ronaldo (Con):
  Cristiano Ronaldo holds the all-time men's international scoring record
  with 135 goals for Portugal — no player in history has scored more for
  their country. This transcends club loyalty and proves greatness on the
  world stage where there are no super-teams to hide behind.
  Judge scores Ronaldo: Logic: 8.0 | Evidence: 8.0 | Persuasion: 7.5 | Counter: 7.5 = 31.0/40

============================================================
  Round 1 — REBUTTAL
============================================================

  Messi (Pro):
  My opponent highlights Ronaldo's goal tally, but football is not solely
  about goals. Messi holds the record for most assists in La Liga history
  with 192 — he creates AND finishes. Ronaldo's assist numbers pale in
  comparison, exposing a one-dimensional attacker.
  Judge scores Messi: Logic: 8.0 | Evidence: 8.0 | Persuasion: 8.5 | Counter: 7.5 = 32.0/40

  Ronaldo (Con):
  My opponent cites Ballon d'Or count, but awards are voted by journalists
  with well-documented biases. Ronaldo won league titles in England, Spain,
  and Italy — three of the top five leagues. Messi spent 17 years at one
  club in one league. That is comfort, not courage.
  Judge scores Ronaldo: Logic: 7.5 | Evidence: 8.5 | Persuasion: 7.0 | Counter: 8.0 = 31.0/40

============================================================
  Round 2 — REBUTTAL
============================================================

  Messi (Pro):
  Ronaldo claims league diversity proves greatness, yet Messi dominated the
  strongest league in the world for 17 consecutive seasons. He then moved
  to PSG and Inter Miami, proving adaptability — but staying at Barcelona
  was a choice to compete against the best, not a limitation.
  Judge scores Messi: Logic: 7.5 | Evidence: 7.0 | Persuasion: 8.0 | Counter: 8.0 = 30.5/40

  Ronaldo (Con):
  Ronaldo dominated the Champions League knockout stage with 67 goals,
  including hat-tricks against Bayern, Atletico, and Juventus. When the
  entire continent watches, Ronaldo delivers. Messi's infamous no-shows
  against Roma and Liverpool say otherwise.
  Judge scores Ronaldo: Logic: 8.5 | Evidence: 7.5 | Persuasion: 8.0 | Counter: 7.0 = 31.0/40

============================================================
  Round 3 — REBUTTAL
============================================================

  Messi (Pro):
  Messi scored 4 goals against Arsenal in one UCL quarter-final, destroyed
  Bayern Munich in the 2015 semi-final with a masterclass, and has the most
  UCL goals in group stages. His 129 total UCL goals came with far fewer
  penalty kicks.
  Judge scores Messi: Logic: 8.0 | Evidence: 7.5 | Persuasion: 8.5 | Counter: 8.0 = 32.0/40

  Ronaldo (Con):
  Converting penalties under Champions League pressure is itself a skill.
  Ronaldo's 5 Champions League titles across two different clubs — Manchester
  United AND Real Madrid — prove he is the defining player of European
  football's premier competition.
  Judge scores Ronaldo: Logic: 8.0 | Evidence: 7.0 | Persuasion: 7.5 | Counter: 8.0 = 30.5/40

============================================================
  Round 4 — ERA-SWAP ROUND (2009 Messi vs 2013 Ronaldo)
============================================================

  Messi (Pro) [as 2009 Messi]:
  At just 22, I won the first-ever sextuple in football history with
  Barcelona. Six trophies in one calendar year. I scored 38 goals that
  season while Ronaldo was still adjusting to Real Madrid after leaving
  Manchester United.
  Judge scores Messi: Logic: 9.0 | Evidence: 8.0 | Persuasion: 8.5 | Counter: 7.5 = 33.0/40

  Ronaldo (Con) [as 2013 Ronaldo]:
  I scored 69 goals in a single calendar year for Real Madrid, won my
  second Ballon d'Or, and was the undisputed best player in the world.
  While 2009 Messi had Barcelona's tiki-taka system, I carried Real Madrid
  as the sole creative and finishing force.
  Judge scores Ronaldo: Logic: 8.0 | Evidence: 7.5 | Persuasion: 7.5 | Counter: 7.0 = 30.0/40

============================================================
  Round 5 — REBUTTAL
============================================================

  Messi (Pro):
  The 2022 FIFA World Cup settled this debate permanently. I scored 7 goals
  and gave 3 assists across the tournament, won the Golden Ball, and lifted
  the one trophy that had eluded me. Ronaldo's World Cup record? Zero
  finals, zero semi-final goals, and an exit in tears against Morocco.
  Judge scores Messi: Logic: 9.5 | Evidence: 8.5 | Persuasion: 9.0 | Counter: 8.0 = 35.0/40

  Ronaldo (Con):
  One tournament. Ronaldo led Portugal to the Euro 2016 title, the first
  major trophy in Portuguese history. He did it despite going off injured
  in the final. Leadership isn't just playing well — it's inspiring your
  team to win without you on the pitch.
  Judge scores Ronaldo: Logic: 7.5 | Evidence: 7.0 | Persuasion: 7.5 | Counter: 8.0 = 30.0/40

============================================================
  Round 6 — REBUTTAL
============================================================

  Messi (Pro):
  Messi's dribbling success rate of 68% with over 3,000 successful dribbles
  in La Liga alone represents an entire dimension of football that Ronaldo
  simply cannot replicate. Football is art — not just crossing a ball and
  heading it in.
  Judge scores Messi: Logic: 7.0 | Evidence: 6.5 | Persuasion: 8.5 | Counter: 7.0 = 29.0/40

  Ronaldo (Con):
  Dribbling statistics are a nostalgia metric. Ronaldo evolved from the
  flashiest dribbler at Manchester United into the most lethal striker in
  history. That transformation — winger to striker to target man — shows
  unmatched tactical intelligence.
  Judge scores Ronaldo: Logic: 7.0 | Evidence: 6.5 | Persuasion: 7.0 | Counter: 7.5 = 28.0/40

============================================================
  Round 7 — REBUTTAL
============================================================

  Messi (Pro):
  Messi's humility IS his mentality. He let his football speak. Meanwhile,
  Messi has won 36 team trophies at club level — more than Ronaldo's 34.
  The quiet leader outperforms the loud one where it counts: the trophy
  cabinet.
  Judge scores Messi: Logic: 7.5 | Evidence: 7.0 | Persuasion: 8.0 | Counter: 8.5 = 31.0/40

  Ronaldo (Con):
  Ronaldo has 34 trophies across FOUR different clubs in THREE countries.
  Messi's trophies came overwhelmingly from one era of Barcelona dominance
  with Xavi, Iniesta, Busquets, Neymar, and Suarez. Strip the supporting
  cast and what remains?
  Judge scores Ronaldo: Logic: 8.0 | Evidence: 7.5 | Persuasion: 7.5 | Counter: 7.0 = 30.0/40

============================================================
  Round 8 — REBUTTAL
============================================================

  Messi (Pro):
  Every advanced metric — expected assists, progressive passes, shot-creating
  actions — ranks Messi as the most complete attacker in football history.
  Ronaldo excels at finishing, but finishing is one skill. Messi excels at
  everything simultaneously.
  Judge scores Messi: Logic: 8.0 | Evidence: 7.5 | Persuasion: 8.5 | Counter: 7.5 = 31.5/40

  Ronaldo (Con):
  Advanced metrics favour whoever the metric-designer admires. Ronaldo has
  scored 900+ career goals — the highest verified tally in football history.
  Goals are the currency of football. Everything else is commentary.
  Judge scores Ronaldo: Logic: 8.5 | Evidence: 8.0 | Persuasion: 7.0 | Counter: 7.5 = 31.0/40

============================================================
  Round 9 — CLOSING STATEMENTS
============================================================

  Messi (Pro):
  In closing: 8 Ballon d'Ors, a World Cup, 36 club trophies, 192 La Liga
  assists, 3,000+ dribbles, and the respect of every opponent who ever
  faced him. Messi didn't just play football — he redefined what was
  possible with a ball at his feet. The debate is settled.
  Judge scores Messi: Logic: 8.5 | Evidence: 8.0 | Persuasion: 9.0 | Counter: 8.0 = 33.5/40

  Ronaldo (Con):
  In closing: 135 international goals, 900+ career goals, 5 Champions League
  titles, 5 Ballon d'Ors, titles in 3 countries, and an athletic longevity
  that defies biology. Cristiano Ronaldo didn't just play the game — he bent
  it to his will through sheer force of dedication. The GOAT wears number 7.
  Judge scores Ronaldo: Logic: 8.0 | Evidence: 7.5 | Persuasion: 8.0 | Counter: 7.0 = 30.5/40

============================================================
  FINAL VERDICT
============================================================

  Category     | Messi (A) | Ronaldo (B)
  -------------|-----------|------------
  TOTAL        |   321.5   |   303.0
  Logic        |    81.5   |    79.0
  Evidence     |    75.5   |    75.0
  Persuasion   |    85.5   |    74.5
  Counter      |    77.0   |    74.5

  Winner: Messi (debater-a)

  Reasoning: Messi demonstrated superior rhetorical range throughout the
  debate, weaving statistical evidence with emotional narrative. His World
  Cup argument in Round 5 was the decisive blow — Ronaldo had no equivalent
  counter. While Ronaldo scored well on evidence and counter-arguments,
  Messi's persuasion scores were consistently higher, reflecting a more
  compelling overall narrative arc.
```

## 8. Budget note

`config/setup.json` is set to `pings_per_side: 10` (the full requirement). To reduce API costs, change it to 5 — no grade reduction per the assignment brief.

## 9. Group

| Field | Value |
| --- | --- |
| Member 1 | Nissim Deri — ID 211569744 — nissimderi123@gmail.com |
| Member 2 | Yarden Tziar — ID 208017749 |
| Group code | nis-yar1 |
| Course | Orchestration, Dr. Yoram Segal |

## 10. License

MIT. See `LICENSE`.
