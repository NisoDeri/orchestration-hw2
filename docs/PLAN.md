# PLAN — debate-ai

**Version**: 1.00 · Supersedes nothing (first version). Architecture, ADRs, contracts, test strategy.

## 1. C4-style overview

### Level 1 — Context

One human operator (the user / lecturer) interacts with **debate-ai** via either the terminal menu or a browser tab. The system calls the **Anthropic API** for every agent turn. No other external systems.

### Level 2 — Containers

```
┌──────────────────────────── debate-ai process ────────────────────────────┐
│                                                                            │
│  ┌──────────────┐    ┌────────────┐    ┌──────────────────────────────┐  │
│  │  CLI Menu    │    │ HTML chat  │    │  UI event emitter            │  │
│  │  (Typer)     │    │ (FastAPI + │◄───│  (in-process pub/sub)        │  │
│  └──────┬───────┘    │   SSE)     │    └─────────────┬────────────────┘  │
│         │            └─────┬──────┘                  │                    │
│         └──────────────┐   │                         │                    │
│                        ▼   ▼                         │                    │
│                  ┌──────────────────┐                │                    │
│                  │       SDK        │────────────────┘                    │
│                  │  (only public    │                                     │
│                  │   entry point)   │                                     │
│                  └────────┬─────────┘                                     │
│                           │                                                │
│         ┌─────────────────┴──────────────────┐                            │
│         ▼                                    ▼                            │
│  ┌──────────────┐                  ┌────────────────────┐                 │
│  │ Orchestration│                  │   Services         │                 │
│  │ (manager,    │                  │  (scoring, facts,  │                 │
│  │  routing,    │                  │   debate ops)      │                 │
│  │  era-swap,   │                  └─────────┬──────────┘                 │
│  │  watchdog)   │                            │                            │
│  └──────┬───────┘                            ▼                            │
│         │                          ┌────────────────────┐                 │
│         ▼                          │  Memory + Models   │                 │
│  ┌──────────────┐                  └─────────┬──────────┘                 │
│  │   Agents     │                            │                            │
│  │ (Judge, Deb. │                            │                            │
│  │  A/B, Color  │                            │                            │
│  │  Crew, FC)   │                            │                            │
│  └──────┬───────┘                            │                            │
│         │                                    │                            │
│         ▼            ┌─────────────┐         │                            │
│  ┌──────────────┐    │ Gatekeeper  │◄────────┘                            │
│  │ Tools wrap.  │───▶│ (rate-limit │                                      │
│  │ (web_search, │    │  + retry +  │   ┌────────────┐                     │
│  │  web_fetch)  │    │  FIFO queue)│──▶│ Anthropic  │                     │
│  └──────────────┘    └─────────────┘   │   API      │                     │
│                                        └────────────┘                     │
│                                                                            │
│   shared/: config.py · logger.py (FIFO rotation) · version.py             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Level 3 — Components (Python modules)

See `docs/architecture.md` for the class diagram (Mermaid). Authoritative module layout is in CLAUDE.md "Layout (final)".

## 2. Architectural Decision Records (ADRs)

### ADR-001 — Generic engine, not a hardcoded debate

**Decision.** Personas and motion live in `config/`. The default demo is Messi vs Ronaldo; ship at least Python vs JavaScript as a second config to prove the genericity.

**Trade-off.** Adds a `personas/` config indirection and one extra Pydantic model (`Persona`). Pays back in DRY-ness, in differentiation against other submissions, and in trivially answering "what if I want a different topic?"

**Status.** Accepted.

### ADR-002 — Topology is child → father → child

**Decision.** The Judge is both router and scorer. Debaters' Anthropic calls receive transcripts the Judge has explicitly relayed; no direct debater-to-debater message exists in the system.

**Trade-off.** One extra hop per turn (latency + tokens). Pays back: matches the brief literally, simplifies turn-taking (judge is the single sequencer), and makes scoring contemporaneous with relaying.

**Status.** Accepted (mandated by brief §8.3.7).

### ADR-003 — Judge scores rhetoric, not facts

**Decision.** Rubric is `Logic | Evidence-as-rhetoric | Persuasiveness | Counter-arg quality`. Catching an opponent's lie scores **positive** for the catcher; the lie itself does **not** deduct from the liar. Fact-Checker output is rendered in the UI but never read by the judge.

**Trade-off.** Goes against intuition ("liars should lose points"). Pays back: matches the brief literally, makes lies *strategically risky for both sides* (good rhetoric → reward; sloppy lie → opponent rewards themselves by catching it).

**Status.** Accepted (mandated by brief §8.3.6 + §9).

### ADR-004 — Anthropic built-in `web_search`, not an MCP

**Decision.** Use Anthropic's server-side `web_search` (`web_search_20260209`) for the mandatory citation step. MCPs (Tavily, Exa, omnisearch) are documented as fallback in `PRD_tools.md` only.

**Trade-off.** Requires org admin to enable web_search in Claude Console. Pays back: no MCP server to run, native `web_search_tool_result` blocks include citations, simpler test mock.

**Status.** Accepted, pending user confirmation that web_search is enabled in their org.

### ADR-005 — Anthropic Agent Skills for "different Skill per agent"

**Decision.** Each of the six agent classes binds to a different Anthropic Agent Skill via `container.skills` on the Messages API. Skill bundles ship in-repo under `src/debate_ai/skills/<skill-id>/`.

**Trade-off.** Skills are a recent (Oct 2025) API surface — beta header required (`betas=["skills-2025-10-02"]`). Pays back: matches the brief's literal "Skill שונה לכל סוכן" wording, mechanically prevents auto-agreement (different system+instruction bundles produce different argumentative styles).

**Status.** Accepted.

### ADR-006 — FastAPI + SSE, not Streamlit or websockets

**Decision.** Backend is a FastAPI app exposing `GET /` (static index.html) and `GET /stream` (Server-Sent Events). Frontend is one HTML + one CSS + one JS file, no framework, no build step.

**Trade-off.** Slightly more code than Streamlit. Pays back: real HTML the user controls (per their explicit ask), one-way SSE is the right primitive for "server pushes events", no websocket handshake overhead, trivially screenshotable.

**Status.** Accepted.

### ADR-007 — Terminal menu is canonical, HTML UI is bonus

**Decision.** Grading happens via the Typer-driven menu or direct SDK call. The HTML UI exists for differentiation and screenshots, not as the test surface.

**Trade-off.** Two interfaces to maintain. Pays back: matches the brief's "תפעול מהטרמינל ... הבדיקה תהיה מבוססת תפעול באמצעות התפריט" verbatim, while keeping the differentiation we want.

**Status.** Accepted.

### ADR-008 — Prompt caching for the Judge

**Decision.** The Judge's system prompt + scoring rubric + accumulated transcript prefix are cached via `cache_control` on each Messages call; only the latest turn varies. Cache TTL ~5 min, well within debate length.

**Trade-off.** Need to be careful that cache key is stable — any whitespace drift busts the cache. Pays back: documented 41–80 % judge-token reduction. At ≥10 pings × 2 debaters, the judge is the most expensive agent, so cache hits matter most here.

**Status.** Accepted.

### ADR-009 — Watchdog as a per-agent supervisor thread, not a separate process

**Decision.** Each agent worker runs in a `concurrent.futures.ThreadPoolExecutor` future; the watchdog polls the future + a per-call timeout. On timeout, the future is cancelled and the agent re-instantiated.

**Trade-off.** Threads can't be forcibly killed in Python. Pays back: simpler than `multiprocessing` for an I/O-bound workload (the Anthropic call is the slow step); restart is "drop the agent object, build a new one" which is cheap.

**Status.** Accepted.

### ADR-010 — No tie via schema-level assertion

**Decision.** `Verdict.score_a` and `Verdict.score_b` are validated via a Pydantic validator that rejects equality. If the judge LLM produces a tie, we retry the verdict prompt with explicit "differentiate by ≥1 point" instruction; on second tie, the orchestrator awards the win to whichever side has the higher running aggregate from per-turn scoring.

**Trade-off.** Adds one retry budget per debate. Pays back: makes "no tie" a hard invariant, not a hope.

**Status.** Accepted.

## 3. SDK contract (the only public surface)

```python
# src/debate_ai/sdk/sdk.py
class DebateAI:
    def __init__(self, config_dir: Path = Path("config")) -> None: ...
    def list_personas(self) -> list[PersonaSummary]: ...
    def list_motions(self) -> list[MotionSummary]: ...
    def run_debate(self,
                   motion: str | None = None,
                   persona_a: str | None = None,
                   persona_b: str | None = None,
                   pings_per_side: int | None = None,
                   on_event: Callable[[UIEvent], None] | None = None,
                   ) -> DebateResult: ...
    def replay(self, debate_id: str) -> DebateResult: ...
    def export_replay(self, debate_id: str, path: Path) -> None: ...
```

CLI menu, FastAPI server, and tests all consume this surface. Anything else is private.

## 4. JSON message contracts

See `models/message_models.py`. Defined in detail in `PRD_agents.md` and `PRD_judge.md`.

## 5. Test strategy

- **Unit tests**: every public class/function, mocked Anthropic. Coverage target ≥85 %.
- **Integration tests** (still mocked): full 10-ping debate, era-swap round behavior, watchdog kill-and-restart, no-tie retry, FIFO log rotation, replay round-trip.
- **End-to-end tests** (recorded — `vcrpy` against a single recorded session): one canned Messi vs Ronaldo debate, asserted character-for-character. Run only locally / manually, not in CI.
- **Property tests** (`hypothesis`): JudgeEnvelope routing always preserves agent identity; scoring aggregator is monotonic in per-turn scores; FIFO rotation never loses lines.

## 6. Risk register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Org has not enabled `web_search` | Med | High | ADR-004 fallback to Tavily MCP; surfaced as Open Question #1 |
| Anthropic Agent Skills beta unstable | Low | Med | Pin beta header; document graceful degradation to per-agent system prompts only |
| Debaters still auto-agree despite different skills | Med | Med | Skill prompts explicitly enforce contradiction; Judge has a "drift detector" that forces re-anchor |
| Watchdog races with normal completion | Low | Med | Single supervisor, futures cancellation is idempotent |
| Cost overrun in a single debate | Low | Med | Hard cap in `rate_limits.json` (`max_cost_usd_per_debate`); gatekeeper aborts |
| User loses or rotates Anthropic key mid-debate | Low | Low | Gatekeeper raises a clean `AuthError`; menu shows actionable hint |
