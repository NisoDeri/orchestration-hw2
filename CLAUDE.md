# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Inheritance — read the parent first

This is **HW2 of an Orchestration course** (Dr. Yoram Segal, year 3, semester B). The parent `orchestraction/CLAUDE.md` (loaded automatically) carries every course-wide rule: documentation-before-code workflow, `uv`-only tooling, 150-LoC file cap, SDK-as-only-entry-point, 85 % coverage gate, zero-ruff-violation gate, conventional-commit cadence, Moodle submission protocol. This file only records what is **specific to HW2**.

When parent rules conflict with the HW2 assignment spec, the **spec wins**.

## Authoritative HW2 spec

The lecturer's actual brief (Hebrew, given in Lecture 05 and the matching summary in Moodle) — paraphrased below in English. The text "hw2 prompt.txt" at the root is a *style template the user composed*, NOT the lecturer brief. Where the two disagree, the lecturer brief wins.

### What the brief actually says

1. **Architecture**: three agents — a Judge (father), a Pro agent, a Con agent.
2. **Topic is FREE.** Barcelona vs Real Madrid, atheism vs theism, freshwater vs saltwater fish, which diet is better — anything. Topic choice is part of "showing taste."
3. **Mandatory conditions:**
   - Respectful turn-taking (limit by time or word count).
   - **Real contradiction**: each agent has a different `Skill` from its opponent — agents tend to "want to please" each other; this *must* be engineered out.
   - **≥ 10 pings per side** (one "ping" = argument + counter-argument). 5 allowed with explicit budget note in README.
   - **Mutual reference**: each agent must address the opponent's actual arguments, not talk in parallel.
   - **Web-search tool is MANDATORY.** Every debater must cite from the internet.
   - **Judge MUST decide. No tie.** Differential scores (e.g. 80/70) are fine; a tie is a fail.
   - **Topology: child → father → child.** Debaters never address each other directly; every utterance routes through the judge.
   - **Communication format: JSON.** Structured templates — monitorable, testable, token-efficient.
4. **What NOT to do:**
   - No tie.
   - No fake debate — the LLM must actually run; you can't fabricate the dialogue from Python.
   - No vulgar / partisan language. Politically correct, respectful.
   - **Cannot submit a Claude-CLI-only solution.** Must be a Python program that drives the agents.
5. **Scoring criterion: persuasive ability, NOT factual correctness.** Like the TV show *To Tell the Truth* — the judge scores rhetoric, not facts. **Lies during the debate are explicitly allowed**; the opposing debater is supposed to catch them, and catching them counts as persuasion.
6. **Build-up phases (Dr. Segal's recommendation):**
   1. Manual phase — two Claude CLIs (or GPT + Gemini), give each a role, run a manual debate, learn the dynamics.
   2. Intermediate — a ClaudeCLI command that runs the father, who runs the children.
   3. Final — Python main that runs all three processes. **This is what we ship.**
7. **Engineering must-haves (explicit in the brief):**
   - Timeouts on every request.
   - **Watchdog + keep-alive** — if an agent process dies, kill and restart it.
   - **OOP** with class diagram of the inheritance graph — attached to the submission.
   - **TDD** + unit tests.
   - Linter + Ruff.
   - **Zero hardcoded parameters** — everything in config files.
   - Cyber: no API keys in Git. Only `.env-example` is committed; `.env` is ignored.
   - **Gatekeeper** — economic/consumption throttling layer (FIFO queue, rate limits).
   - **SDK layer** — independent modules under the interface (Terminal/CLI/UI/API) so an AI agent can debug itself by calling the SDK directly.
   - **Structured logging with FIFO file rotation** — config-driven (e.g. 20 files × 500 lines).
   - **Terminal menu operation is the canonical test interface** — keyboard-driven menu in the terminal. GUI is allowed and screenshots welcomed, but **grading is via menu or direct SDK call**.
8. **Submission requirements:**
   - `README.md` with screenshots, the actual prompts used, and the full transcript of session 1.
   - Conversations in **English or Hebrew** (not Arabic — the lecturer needs to read them).
   - `uv` virtual env, `pyproject.toml` reproducible on the examiner's machine.
   - `.env-example` only, no `.env`.
   - Pair submission, each member uploads the PDF link separately on Moodle, repo shared with `rmisegal@gmail.com` (or public — public is recommended).
   - Inaccessible repos at deadline = disqualified, no resubmission.
9. **Edge-cases clarified in class:**
   - Tie? Definitely no. Even 51/49 is OK; tie is not.
   - Does the judge need to know the topic? *No* — the judge only knows the rules and judges rhetoric. Better that he doesn't know the topic (less bias).
   - Mid-debate agreement? Allowed *at a single point*. Sustained agreement is "drift" and the father must intervene to re-anchor roles.
   - Lies? Allowed. Catching them is part of the game.

## What HW2 builds

A debate system on the hardcoded motion *"Who is the greatest footballer of all time: Lionel Messi or Cristiano Ronaldo?"* — the user picked this topic and explicitly rejected generic-engine framing on 2026-05-20 ("we chose messi vs ronaldo and we want it hardcoded"). MessiAgent and RonaldoAgent are concrete classes (no persona-swap at runtime). Their prompts + era variants still live in `config/personas/messi.json` and `ronaldo.json` so they can be tuned without code edits.

**Six agent classes**, all subclassing one `BaseAgent`:

| Agent | Role | Affects scoring? |
| --- | --- | --- |
| **JudgeAgent** (father) | Routes every message, enforces structure, scores running aggregate, declares the winner. Does *not* know the topic in advance — only the rules. | — (it IS the scorer) |
| **MessiAgent** (debater-a) | Argues Messi is the greatest. Inherits from shared `DebaterAgent` base for DRY (citations, mutual-reference enforcement, JSON schema). | Yes |
| **RonaldoAgent** (debater-b) | Argues Ronaldo is the greatest. Same shared base. | Yes |
| **CommentatorAgent** | Color-commentary one-liner between rounds. | No — flavor only |
| **CrowdAgent** | Audience sentiment + emoji reaction after each debater turn. | No — flavor only |
| **FactCheckerAgent** | Annotates dubious claims for the human audience. **The judge ignores it** (judge scores rhetoric, not facts — per the brief). | **No** |

### Debate flow (per the spec)

1. Judge announces the motion and rules. Does **not** reveal which side it agrees with.
2. **Opening statements** — Debater-A, then Debater-B. Each speaks *to the judge*; the judge relays.
3. **N rebuttal pings** (default N = 10 per side, configurable down to 5 with README note). Each ping = one debater turn + one opponent counter-turn, both routed through the judge.
4. **One designated round is the era-swap round** — both debaters must argue as a specific era version of themselves (2009 Messi vs 2013 Ronaldo, per persona's `eras` array). Scores into the same aggregate, not a separate verdict.
5. **Final summaries** — each debater closes.
6. **Judge verdict** — single decision, differential score (e.g. *Messi 78 / Ronaldo 72*), with reasoning. **No tie permitted.**

### JSON message contracts

**Debater reply:**
```json
{ "argument": "...", "confidence": 0.0-1.0, "attack_points": ["..."], "defense_points": ["..."], "citations": ["https://..."] }
```

**Judge envelope (every message in the debate is wrapped in one):**
```json
{ "from": "Debater-A" | "Debater-B" | "Judge" | "Commentator" | "Crowd" | "Fact-Checker",
  "to":   "Debater-A" | "Debater-B" | "All",
  "round": 1, "kind": "opening" | "rebuttal" | "era_swap" | "closing" | "ruling",
  "payload": { ... } }
```

Judge scoring categories: **Logic, Evidence-as-rhetoric, Persuasiveness, Counter-argument quality**. "Evidence-as-rhetoric" means we score *how convincingly* a debater wielded evidence, NOT whether the evidence is true. This is the key rephrasing required by the brief.

## Locked design rules (do not relitigate without the user)

1. **Topology is child → father → child.** Debaters never message each other directly. The judge is a router AND scorer.
2. **Judge verdict is whole-debate aggregate, single decision, no tie.** Era-swap rounds feed the same aggregate.
3. **Judge scores persuasion, NOT facts.** Lies are allowed. The opposing debater is supposed to catch them; catching them = persuasion points.
4. **Each agent has a different `Skill` set** (in the Anthropic-API or Claude-Code sense — TBD by research agent). Debater-A and Debater-B must differ in skill/tool affordances so they don't auto-agree.
5. **Web search is MANDATORY** for both debaters. Citations array is required in their JSON reply.
6. **Fact-Checker never scores.** It is a viewer-side annotation only. Judge does not consult it.
7. **No rhetorical cards system.** Explicitly cut during scoping.
8. **Personas (prompts + eras) live in config; the agent classes are concrete.** MessiAgent and RonaldoAgent are explicit subclasses that load their respective JSON. There is no `--persona-a` / `--persona-b` CLI flag and no runtime persona swap.
9. **Terminal menu is the canonical test interface.** HTML UI is bonus, not the grading surface.
10. **No ties.** Even 51/49 is acceptable; equal scores must be broken by the judge.

## UI — two interfaces, one event stream

The brief grades the **terminal menu**. The HTML chat UI is for differentiation.

- **Canonical (graded): terminal menu** under `src/debate_ai/cli/`. Typer-driven, keyboard-operated, exposes: *Start debate*, *Show last verdict*, *Open replay*, *Tail logs*, *Show config / version*. Every menu item is a thin wrapper around the SDK — operators can also call the SDK directly. (No "choose persona/motion" items — topic is hardcoded.)
- **Bonus (differentiator): HTML chat UI.** FastAPI under `src/debate_ai/ui/` exposes `GET /` (single-page HTML/CSS/JS chat) and `GET /stream` (Server-Sent Events pushing `agent_typing`, `agent_message`, `score_update`, `round_changed`, `verdict`). Telegram-style bubbles, live scoreboard side panel, confidence meter, round badge. No JS framework, no build step.
- **One event stream feeds both.** The orchestrator emits `UIEvent`s through a single emitter; the CLI menu's "Watch live" subscribes via in-process queue, the HTML page via SSE. Same source of truth.
- **Replay export.** Each debate persists its full event log as JSON *and* renders to a styled HTML file. README screenshots come from these replays.

## Layout (final)

```
src/debate_ai/
  sdk/sdk.py                        # single entry point for all business logic
  cli/
    main.py                         # Typer app
    menu.py                         # keyboard-driven menu loop (canonical test UI)
  agents/
    base_agent.py                   # ABC + mixins for memory / JSON / tools
    debater_agent.py                # shared DebaterAgent base — citations / mutual ref
    messi_agent.py                  # MessiAgent — loads personas/messi.json
    ronaldo_agent.py                # RonaldoAgent — loads personas/ronaldo.json
    judge_agent.py                  # router + scorer
    commentator_agent.py
    crowd_agent.py
    factchecker_agent.py
  orchestration/
    debate_manager.py               # full debate lifecycle
    round_manager.py                # one round of speak-turns
    routing.py                      # child -> father -> child enforcement
    era_swap.py                     # picks era variants for the era-swap round
    watchdog.py                     # keep-alive + restart of stuck agents
  memory/
    conversation_memory.py
    context_builder.py
  models/
    message_models.py               # AgentReply, JudgeEnvelope, Verdict, UIEvent
    debate_models.py                # DebateConfig, DebateState, Round, Persona
  services/
    debate_service.py
    scoring_service.py              # rhetoric-not-fact aggregator
    facts_service.py                # facts JSON for Fact-Checker (viewer-only)
  tools/
    web_search_tool.py              # wraps the chosen web-search affordance
    citation_tool.py                # URL fetch + extract for citations
  ui/
    server.py                       # FastAPI + SSE
    events.py                       # UIEvent emitter (shared CLI + HTML)
    static/{index.html,styles.css,app.js}
    replay_export.py
  shared/
    config.py                       # JSON config loader, version-checked
    gatekeeper.py                   # rate-limit + FIFO queue + retry
    logger.py                       # FIFO file rotation, config-driven
    version.py                      # starts at "1.00"
  utils/{formatting.py,validators.py}
  constants.py
config/
  setup.json                        # rounds, timeouts, agent enablement
  debate.json                       # motion + persona pair selection
  personas/
    messi.json, ronaldo.json, python.json, javascript.json   # at least 4 to show genericity
  models.json                       # Anthropic model IDs + temperatures per role
  logging.json                      # FIFO rotation: 20 files x 500 lines
  rate_limits.json                  # gatekeeper budgets
  facts.json                        # Fact-Checker knowledge base
  versions.json                     # code/config pinning
docs/
  PRD.md, PLAN.md, TODO.md
  PRD_agents.md                     # base + debater + judge personas, JSON contracts
  PRD_judge.md                      # rhetoric scoring + no-tie + child-father-child
  PRD_memory.md
  PRD_ui.md                         # menu + HTML/SSE
  PRD_factchecker.md                # viewer-only annotator
  PRD_color_crew.md                 # commentator + crowd
  PRD_era_swap.md
  PRD_tools.md                      # web search + citations + chosen MCPs/skills
  PRD_watchdog.md                   # timeouts + keep-alive + restart
  PRD_logging.md                    # FIFO rotation
  architecture.md                   # class diagram (Mermaid)
  prompts.md                        # Prompt Engineering Log
```

## Implementation phases (post-doc-approval)

1. **Docs** — all PRDs + ≥500-task TODO + README skeleton. Pause for user approval.
2. **Scaffolding** — `pyproject.toml`, `uv.lock`, `.env-example`, `.gitignore`, empty tree, ruff + coverage, version `1.00`.
3. **Models + memory** — Pydantic message contracts, transcript store.
4. **Logger + Gatekeeper** — FIFO rotation, rate-limit queue. Get these in early; everything depends on them.
5. **Tools layer** — web-search wrapper + citation tool. Mockable for tests.
6. **Agents** — base, debater, judge, commentator, crowd, fact-checker.
7. **Orchestration** — routing (child→father→child), round manager, debate manager, era-swap, watchdog.
8. **SDK** — wire everything into `sdk/sdk.py`.
9. **CLI menu** — canonical interface, every menu item calls SDK.
10. **UI server** — FastAPI + SSE + HTML page.
11. **Tests** — unit + integration with mocked Anthropic, ≥85 % coverage.
12. **Polish** — ruff clean, README screenshots + session-1 transcript, version tag `v1.0.0`.

Commit per atomic task. No mega-commits.

## Configuration knobs the brief forbids hardcoding

Rounds per debate, pings-per-side, timeouts per request, watchdog poll interval and restart count, gatekeeper rate limits and queue depth, log rotation (file count and lines-per-file), model IDs, temperatures, scoring weights, persona file paths, debate motion text. All in `config/*.json`, version-pinned, validated on startup.

## Tools / MCPs / Skills (confirmed stack)

Resolved by research pass 2026-05-20. Details in `PRD_tools.md`.

- **Web search (mandatory)**: Anthropic built-in `web_search` server tool (`web_search_20260209`). Org admin enables in Claude Console. $10 / 1k searches. Returns `web_search_tool_result` blocks with native URL citations.
- **URL fetch**: Anthropic built-in `web_fetch` server tool. Judge uses it to re-pull a debater's cited URL when probing claims.
- **Force-cite-every-turn**: pass `tool_choice: {"type": "any"}` (or `{"name": "web_search"}`) to debater requests so they cannot reply without invoking search.
- **"Different `Skill` per agent" = Anthropic Agent Skills.** The literal interpretation of the brief. Filesystem skill bundles loaded via `container.skills` on Messages API. Each agent gets a different skill ID:
  - Debater-A → `rhetorical-aggression`
  - Debater-B → `evidence-marshalling`
  - Judge → `scoring-rubric`
  - Commentator → `color-commentary`
  - Crowd → `audience-sentiment`
  - Fact-Checker → `claim-verification`
  Skill bundles live under `src/debate_ai/skills/<skill-id>/SKILL.md` + helpers. Modeled on `github.com/anthropics/skills`.
- **Prompt caching for the Judge**: judge's transcript grows turn-by-turn. Cache the system prompt + rubric + transcript prefix with `cache_control`; latest turn goes last. Documented 41–80 % judge-token reduction.
- **Wikipedia MCP** (`uvx wikipedia-mcp`, free, no auth): Fact-Checker's claim-verification skill calls this. Avoids a second paid search provider.
- **Fallback search providers** (Tavily / Exa / Brave / mcp-omnisearch): documented in `PRD_tools.md` as a switchover plan if the org disables built-in `web_search`. Not shipped by default.

API beta headers required: `betas=["skills-2025-10-02", "code-execution-2025-08-25"]`. Model: `claude-opus-4-7` (skills require Opus 4.7 / Sonnet 4.6).

## Secrets

`ANTHROPIC_API_KEY` read via `os.environ.get(...)` only. `.env-example` ships a placeholder. `.env` is gitignored. Tests mock the Anthropic client end-to-end.

## Working language

Code identifiers, docstrings, JSON keys, log messages: **English**. README and `docs/*.md`: English or Hebrew per user — *ask once per file before committing*.
