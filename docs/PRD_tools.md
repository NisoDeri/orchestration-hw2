# PRD — Tools / MCPs / Skills

**Version**: 1.00 · The full external-affordance stack. Conclusions from the 2026-05-20 research pass; details in memory `project-hw2-tools-stack`.

## 1. Anthropic server-side tools (no plumbing — just enable)

### `web_search` (MANDATORY by spec)

- Identifier: `web_search_20260209` (older `web_search_20250305` still works but lacks dynamic filters).
- Models supported: Claude Opus 4.7, Sonnet 4.6.
- Org admin must enable in Claude Console.
- **Pricing: $10 / 1 000 searches** + normal token costs.
- Parameters used: `max_uses=3` per debater turn, `user_location={"country": "IL"}` for local context, optionally `allowed_domains` / `blocked_domains` from `config/rate_limits.json`.
- Returns `web_search_tool_result` blocks containing `url`, `title`, `snippet` — these become the debater's `citations` array.

**Why this, not an MCP**: zero plumbing, native citations, simpler test mock (`anthropic` client returns `web_search_tool_result` block; we just pre-fill it).

### `web_fetch`

- Companion to `web_search`. Server-side URL → text.
- Used by the **Judge** to *probe* a debater's cited URL when scoring "Evidence-as-rhetoric" (the judge isn't verifying truth; it's verifying that the URL exists and contains *something* the debater is gesturing at — which is what raises rhetorical quality).

## 2. Anthropic Agent Skills (resolves "different Skill per agent")

- Real, formal API feature, released Oct 2025 as an open standard.
- Bundles of instructions + scripts on the filesystem, loaded on-demand via `container.skills` on the Messages API.
- API beta header: `betas=["skills-2025-10-02", "code-execution-2025-08-25"]`.

### Our six skills (locked)

Each lives at `src/debate_ai/skills/<skill-id>/`. Each follows the upstream format:

```
src/debate_ai/skills/rhetorical-aggression/
  SKILL.md             # the instruction set Claude sees
  scripts/             # optional helper scripts the skill may invoke
  resources/           # optional static assets
```

| Skill ID | Owned by | One-line essence |
| --- | --- | --- |
| `rhetorical-aggression` | Debater-A | "Attack premises. Cite always. Name opponent's previous claim before rebutting." |
| `evidence-marshalling` | Debater-B | "Build from sources upward. Anticipate counter-attack. Cite always. Quote opponent." |
| `scoring-rubric` | Judge | "Score rhetoric not facts. Aggregate per turn. Refuse ties." |
| `color-commentary` | Commentator | "One evocative sentence between rounds. Never declare winner." |
| `audience-sentiment` | Crowd | "Emojis first. One short reaction line. Lean ∈ [-1, 1]." |
| `claim-verification` | Fact-Checker | "Check claim against facts.json → Wikipedia MCP → web_search. Annotate severity. Do not score." |

Skill bundles are modelled on `github.com/anthropics/skills` (Apache 2.0). We may invoke `code_execution_20250825` from within skills if a skill chooses to.

## 3. MCP — only one ships by default

### Wikipedia MCP (ships)

- Install: `uvx wikipedia-mcp`
- Repo: `github.com/Rudra-ravi/wikipedia-mcp`
- Auth: none. Free.
- Used by: `claim-verification` skill (Fact-Checker), as the second-priority claim source after `facts.json`.
- Why it ships: free, structured, deterministic enough for tests. Lets the Fact-Checker punch above its weight without burning paid searches.

### Fallback providers (documented, not shipped)

If the org disables `web_search`, swap in **one** of these by toggling `config/rate_limits.json::web_search_provider` from `"anthropic_builtin"` to one of:

| Provider | Install | Free quota | Why fallback |
| --- | --- | --- | --- |
| `tavily` | `uvx tavily-mcp` | 1 000 credits/month free | Cleanest LLM-shaped search API; closest semantic match to Anthropic's built-in |
| `exa` | `npx -y exa-mcp-server` | pay-as-you-go | Best for *novel angles* — semantic search finds non-obvious counter-evidence |
| `omnisearch` | `uvx mcp-omnisearch` | per-provider | A/B test multiple providers without rewiring |

`tools/web_search_tool.py` exposes a single `search(query) -> list[Citation]` surface; the implementation under that surface is dispatched by config. The agents never know which provider was used.

## 4. Prompt caching (for Judge cost)

`cache_control={"type": "ephemeral"}` on:

1. Judge system prompt + rubric (static across the debate).
2. Transcript prefix (grows monotonically — each turn extends the cached prefix).

Latest turn (`messages[-1]`) is NOT cached so it always re-runs.

Expected savings: 41–80 % on judge tokens after the first turn. Documented in Anthropic's prompt-caching guide. Cache TTL ~5 min, well within a single debate.

## 5. Cost guard

`config/rate_limits.json::max_cost_usd_per_debate` (default `2.00`). The Gatekeeper tracks running cost from Anthropic response headers + a static $0.01-per-search counter for `web_search`. When the cap is breached:

1. Stop accepting new agent calls.
2. Emit `UIEvent(kind="error", payload={"reason": "cost_cap"})`.
3. Force the Judge to emit a verdict from the running aggregate.

## 6. Tests

- `test_web_search_tool_dispatch.py` — switching `web_search_provider` config swaps the implementation; agents are unchanged.
- `test_force_search_tool_choice.py` — debater requests always include `tool_choice: {"type": "any"}`.
- `test_judge_cache_control.py` — second judge call's system prompt is byte-identical to first call's prefix (so the cache hits).
- `test_skill_bundle_present.py` — each of the six skill IDs has a `SKILL.md` on disk before the agent boots.
- `test_cost_cap_triggers_verdict.py` — gatekeeper at-or-over cap → Judge emits verdict from aggregate.
