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
- **≥10 pings per side** (or 5 with budget note — `pings_per_side` lives in `config/setup.json`).
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

Class diagram: see `docs/architecture.md`.

## 3. Quickstart

```powershell
# 1. install
uv sync

# 2. set your key (PowerShell)
cp .env-example .env        # then edit .env and add ANTHROPIC_API_KEY

# 3. canonical: terminal menu
uv run debate-ai

# 4. one-shot: run the default debate
uv run debate-ai run

# 5. bonus: launch the HTML chat UI
uv run debate-ai start
# → opens http://localhost:8000 in your browser, debate streams live
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
uv run pytest            # full suite
uv run pytest --cov      # with coverage (≥85% required)
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
  agents/         ← BaseAgent + 6 subclasses
  orchestration/  ← debate / round / routing / era-swap / watchdog
  memory/         ← conversation memory + per-agent context windows
  models/         ← Pydantic message + state models
  services/       ← scoring, facts, debate ops
  tools/          ← web_search wrapper + citation tool
  ui/             ← FastAPI server + SSE + static HTML/CSS/JS
  shared/         ← config, logger (FIFO), gatekeeper, version
  skills/<id>/    ← one Anthropic Agent Skill bundle per agent
config/           ← all tunables
docs/             ← PRDs, PLAN, TODO, architecture, prompts.md
tests/{unit,integration}/
```

## 7. Live demo & screenshots

To see the live UI, run `uv run debate-ai start` — it opens a browser with the SSE-driven chat UI. Terminal output (the graded interface) is shown by `uv run debate-ai run`.

## 8. Group

| Field | Value |
| --- | --- |
| Member 1 | Nissim Deri — ID 211569744 — nissimderi123@gmail.com |
| Member 2 | Yarden Tziar — ID 208017749 |
| Group code | *(see PDF cover)* |
| Course | Orchestration, Dr. Yoram Segal |

## 9. License

MIT. See `LICENSE`.
