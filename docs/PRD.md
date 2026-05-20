# PRD — debate-ai

**Version**: 1.00 · **Owner**: Nissim Deri + Yarden Tziar · **Course**: Orchestration (Dr. Yoram Segal) · **HW**: 02

## 1. Goal

Build a Python-driven, multi-agent debate engine where two LLM-backed debaters argue a configurable motion under a third LLM-backed judge. Every constraint in Dr. Segal's HW2 brief (Lecture 05, §8) is honored verbatim. The engine is **generic**: the motion and personas are config-driven, so the same code runs *Messi vs Ronaldo*, *Python vs JavaScript*, or any user-supplied debate.

## 2. Why this shape

Most HW2 submissions will be one-shot scripts on a hard-coded topic. The platform framing — same engine, swap-out personas + motion — is the differentiator. It also makes the code provably DRY: if Messi-vs-Ronaldo and Python-vs-JS share 95 % of execution, the abstractions are right.

## 3. KPIs

| KPI | Target | How measured |
| --- | --- | --- |
| Lecturer brief compliance | 100 % of §8.3 + §8.6 + §8.7 items addressed | Cross-checked in `docs/COMPLIANCE.md` (auto-generated table) |
| Test coverage | ≥ 85 % | `uv run pytest --cov` with `fail_under = 85` |
| Ruff violations | 0 | `uv run ruff check` clean |
| Files over 150 LoC | 0 | CI script greps every `*.py` |
| Debates that end in a tie | 0 | Judge contract forbids ties; assertion in `scoring_service` |
| Debater turns without a `web_search` invocation | 0 | Gatekeeper rejects replies missing `citations` |
| Agent processes that hang past timeout | 0 in CI | Watchdog kill-and-restart; integration test simulates hang |
| Self-assessment grade target | **88** | Per parent CLAUDE.md §11 — "don't claim 100" |

## 4. Functional requirements

**FR-1 — Three primary + three supporting agents.** Judge, Debater-A, Debater-B (primary). Commentator, Crowd, Fact-Checker (supporting, do not score).

**FR-2 — Routing topology.** Every utterance goes child → father → child. Debaters never receive each other's text directly; the judge relays.

**FR-3 — Mandatory web search.** Both debaters' Anthropic calls force `tool_choice: {"type": "any"}` so they cannot reply without invoking `web_search`. The reply schema requires `citations: [url, …]` (≥ 1).

**FR-4 — One distinct Skill per agent.** Six Anthropic Agent Skill bundles ship under `src/debate_ai/skills/` — one per agent class. Skills differ enough that the debaters cannot collapse into mutual agreement.

**FR-5 — Configurable pings.** Default 10 per side; `setup.json` may reduce to 5 (with README note) without code change.

**FR-6 — Era-swap round.** Exactly one round per debate forces both debaters to argue as a specific era version of themselves (e.g. *2009 Messi vs 2013 Ronaldo*). Eras live in each persona's config under `eras`. Scores feed the *same* aggregate as normal rounds — no separate verdict.

**FR-7 — Whole-debate verdict, no tie.** The judge emits exactly one `Verdict` at the end with a differential score and reasoning. The schema asserts `score_a != score_b`.

**FR-8 — Persuasion-only scoring.** Judge rubric is `Logic | Evidence-as-rhetoric | Persuasiveness | Counter-arg quality`. *Factual correctness is explicitly out of scope* for the judge. Catching an opponent's lie counts toward Persuasiveness; the lie itself does not deduct anything.

**FR-9 — Fact-Checker is viewer-only.** Annotates dubious claims for the human watching the UI. Judge ignores it.

**FR-10 — Two interfaces, one event stream.**
- *Canonical (graded):* terminal menu (Typer), keyboard-operated, one menu item per SDK call.
- *Bonus:* HTML chat UI served by FastAPI, live-updated via Server-Sent Events.
Both subscribe to the same `UIEvent` emitter.

**FR-11 — Replay export.** Every debate writes a JSON event log + a self-contained styled HTML replay to `replays/`.

**FR-12 — Watchdog + keep-alive.** Every Anthropic call has a timeout. A monitor thread/process detects hangs and restarts the agent worker, up to a config-defined retry cap.

**FR-13 — Gatekeeper.** Centralizes outbound Anthropic calls behind a rate-limited FIFO queue, with retry-on-transient and backpressure. Config in `rate_limits.json`.

**FR-14 — Structured logging with FIFO rotation.** Config-driven file count and lines-per-file (e.g. 20 × 500). Every log line carries `debate_id`, `round`, `agent`, `kind`.

## 5. Non-functional requirements

**NFR-1 — `uv` only.** No `pip`, no `venv`, no `requirements.txt`. `pyproject.toml` + `uv.lock` is the truth.

**NFR-2 — 150-LoC file cap.** Per parent rule. Test files included. No compressing to fit — split.

**NFR-3 — Zero hardcoded tunables.** Rounds, pings, timeouts, model IDs, temperatures, scoring weights, log rotation, persona paths — all in `config/*.json`, version-validated on startup.

**NFR-4 — TDD.** Tests written before or alongside code. ≥85 % global coverage. External APIs mocked.

**NFR-5 — Ruff clean.** Active groups `E, F, W, I, N, UP, B, C4, SIM`. Line length 100.

**NFR-6 — OOP + class diagram.** `BaseAgent` inheritance graph rendered in Mermaid in `docs/architecture.md` (mandatory per brief §8.6).

**NFR-7 — Secrets hygiene.** `.env-example` only is committed; `.env` is gitignored. Tests never hit the live API.

**NFR-8 — Cost guard.** Default debate runs at ~$0.50–2.00 of Anthropic spend (10 pings × 2 debaters × ~5 tool-calls + judge reasoning). Hard cap configured in `rate_limits.json` (`max_cost_usd_per_debate`); gatekeeper aborts cleanly if breached.

**NFR-9 — Working language.** Code, identifiers, docstrings, JSON keys, log messages — English. README and `docs/*.md` may be Hebrew or English (asked once per file).

## 6. Constraints

- Anthropic API only (Claude Opus 4.7 default — required for Agent Skills + `web_search`).
- Python ≥ 3.10 (current `uv` default).
- Org admin must enable `web_search` in Claude Console — flagged in §10 as a question for the user.
- No GUI dependency for grading: the menu + SDK must run headless.

## 7. Milestones

| # | Deliverable | Acceptance signal |
| --- | --- | --- |
| M1 | All docs approved | User says "ship it" |
| M2 | Scaffolding green | `uv sync` + `ruff check` + empty test suite all pass |
| M3 | Tools layer + Gatekeeper + Logger | Mocked search + log rotation tested |
| M4 | Agents wired | Single mock-debate round completes end-to-end |
| M5 | Orchestration + watchdog | 10-ping debate completes without intervention |
| M6 | Menu + UI + replay export | Browser shows live debate; menu drives the same debate |
| M7 | Tests + polish + tag v1.0.0 | `ruff check` clean, `pytest --cov` ≥ 85 %, README screenshots in place |

## 8. Acceptance criteria

1. `uv run debate-ai run` produces a complete, transcripted, non-tie debate end-to-end.
2. Replacing `config/debate.json` to a different persona pair (e.g. Python vs JS) and re-running produces a coherent debate on the new motion with zero code changes.
3. `docs/COMPLIANCE.md` shows every brief §8 item as ✅.
4. Kill `-9` of a debater process mid-debate is recovered by the watchdog within the configured timeout.
5. `uv run debate-ai start` opens a browser tab to a live chat UI rendering the same debate the menu would.
6. A `replays/<timestamp>.html` is self-contained (open in any browser, no server required).

## 9. Out of scope (HW2)

- Persistence beyond per-debate replay artifacts (no DB).
- User auth (single-user local app).
- Multi-debate tournaments (could be a follow-up assignment).
- Real-time multilingual dubbing.

## 10. Open questions for the user

Surfaced at the end of the docs phase, before any code lands. See chat.

## 11. Self-assessment grade

**88.** Justification: all brief items addressed, generic-engine framing as a real differentiator, but we're conservative about claiming perfection (per parent CLAUDE.md §11 — high self-grades trigger ruthless review).
