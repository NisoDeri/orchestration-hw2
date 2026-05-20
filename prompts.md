# Prompt Engineering Log — debate-ai (HW2)

This log captures the significant prompts used to drive AI-assisted development, along with what we tried, what failed, and what we learned. Required by HW2 brief §8.7 and parent CLAUDE.md §8.

Format per entry:
```
## YYYY-MM-DD — short title
**Context.** Why we needed a prompt here.
**Prompt.** The literal text given to the AI.
**Outcome.** What came back — success, partial, fail.
**Lesson.** What we'd do differently / what to keep.
```

---

## 2026-05-20 — Initial scoping conversation

**Context.** First pass at locking HW2 scope: which creative bundles to include, how to differentiate from the obvious Messi-vs-Ronaldo wall-of-text other students will ship.

**Prompt.** "I want to add a UI for this similar to whatsapp or telegram when we see the agents argue and the judge - also add more creative ideas to this project as messi vs ronaldo will be commonly chose and we want to be special."

**Outcome.** Picked: Color Crew (commentator + crowd), Fact-Checker, Era-swap rounds (no rhetorical cards), Visual polish (live confidence meter + HTML replay export), generic-engine framing, FastAPI + SSE + HTML UI.

**Lesson.** "Make it generic" is a stronger differentiator than any single feature — converts a one-shot script into a platform.

---

## 2026-05-20 — Tool / MCP / Skill research

**Context.** The Hebrew brief mandates web search and "different Skill per agent". Needed to know what Anthropic actually exposes vs. what we'd have to plumb.

**Prompt.** Dispatched research agent (general-purpose) with concrete sub-questions about web_search built-in, Agent Skills API surface, prompt caching, force-search via `tool_choice`, fallback MCPs.

**Outcome.** Confirmed: `web_search_20260209` is the right built-in tool ($10/1k). Anthropic Agent Skills is a real Oct-2025 API feature — the literal interpretation of "Skill שונה לכל סוכן". Prompt caching cuts judge tokens 41–80 %. Wikipedia MCP free + no-auth makes a great Fact-Checker source.

**Lesson.** Always check whether the platform already exposes what we're about to build. Saved 100+ TODO tasks vs. plumbing our own search.

---

## 2026-05-20 — Agent Skill bundles (6 SKILL.md files)

**Context.** Each agent needs a separate Anthropic Agent Skill. The judge's skill defines the scoring rubric; debater skills encode rhetorical posture; colour crew and fact-checker get domain-specific guidelines.

**Prompt.** "Write each SKILL.md so the agent cannot drift outside its lane — judge scores rhetoric only, fact-checker annotates for viewers only (never feeds judge), crowd is emoji + one-liner."

**Outcome.** Six skill bundles under `src/debate_ai/skills/`. Each caps allowed tools, output schema, and behavioral guardrails. Tested by integration — agents stay in-lane.

**Lesson.** Skill prompts must explicitly state what the agent must NOT do, not just what it should do. Omissions get filled by the LLM's default helpfulness.

---

## 2026-05-20 — Gatekeeper.call() signature bug

**Context.** `_call_anthropic` put `model` in an api_kwargs dict AND passed it as a keyword to `gatekeeper.call()`, causing a `TypeError: got multiple values for keyword argument 'model'`.

**Prompt.** Self-debugging cycle — the error was caught in test, traced to the double-model path.

**Outcome.** Fixed with `api_kwargs.pop("model")` before spreading. Test mock also updated: `_gk_call` strips `model` and `source` before forwarding, matching real Gatekeeper behavior.

**Lesson.** When a proxy strips kwargs, every mock of that proxy must strip the same kwargs. Otherwise the test passes but the integration breaks.

---

## 2026-05-20 — ScoringService constructor mismatch

**Context.** `ScoringService.__init__` takes `(agreement_keywords: list[str], drift_window_turns: int)`, but `DebateService` was passing `self.setup.judge` (a `JudgeConfig` object).

**Prompt.** Caught via test_debate_manager.py when wiring mock ScoringService.

**Outcome.** Fixed `debate_service.py` to pass `self.setup.judge.agreement_keywords` and `self.setup.judge.drift_window_turns` separately. Also fixed `apply_lie_catch_bonus` which needed an explicit `opponent_replies=[]` third arg.

**Lesson.** Constructor signatures are contracts — always grep callers when you change one.

---

## 2026-05-20 — Coverage push from 83% to 89%

**Context.** 85% coverage is a hard gate. After implementing all source, coverage was 83.56%.

**Prompt.** "Add tests targeting debate_manager.py uncovered paths (verdict flow, event emission) and server.py (index, status, emitter wiring, broadcast)."

**Outcome.** test_debate_manager.py and test_server.py brought coverage to 88.97%. Uncovered paths are now limited to CLI (interactive menu — untestable in unit test) and some error branches.

**Lesson.** Test the orchestration loop with mocked agents — it exercises many branches cheaply. CLI/menu code is legitimately hard to unit-test; accept that gap.
