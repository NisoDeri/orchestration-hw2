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

## Future entries

Append below as we write each skill bundle, each agent system prompt, each iteration on the judge rubric, and each fix to a misbehaving agent.

(blank — to be filled phase-by-phase)
