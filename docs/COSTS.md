# COSTS — operating-cost analysis for debate-ai

**Version:** 1.00 · **Authoritative source:** `config/rate_limits.json` (cost caps live here, code never hardcodes).

The excellence-guidelines rubric (§11 "עלויות ותמחור") expects any real-world AI application to document and reason about what it costs to operate and how those costs behave as usage scales. This doc is that analysis.

## 1. Cost model — per debate

A full debate at the spec's `pings_per_side = 10` (the default in `config/setup.json`) makes roughly:

| Component | Calls per debate | Cost driver |
| --- | ---: | --- |
| Judge utterances (intro + per-round scoring + verdict) | ~12 | Claude Sonnet input + output tokens |
| Debater turns (Messi + Ronaldo, 10 each) | 20 | Claude Sonnet input + output, +1 web_search tool call per turn |
| Commentator color | 10 | Claude Haiku (cheaper persona, configured in `config/models.json`) |
| Crowd reactions | 10 | Claude Haiku |
| Fact-Checker annotations | 20 | Claude Sonnet — one per debater turn |
| Anthropic `web_search` invocations | ~20 | `$0.01` flat per use (set in `rate_limits.json`) |

### 1.1 Token-volume estimate (per debate)

Numbers are honest order-of-magnitude estimates based on the live demo transcript in `README.md` §9 and the system-prompt sizes in `config/personas/`:

| Bucket | Input tokens | Output tokens |
| --- | ---: | ---: |
| Judge | ~6 000 | ~3 000 |
| Each debater (×2) | ~12 000 | ~6 000 |
| Commentator + Crowd | ~3 000 | ~1 500 |
| Fact-Checker | ~6 000 | ~3 000 |
| **Total per debate** | **~39 000** | **~19 500** |

### 1.2 Dollar cost (Claude pricing as of 2026-05)

| Model | $ / M input | $ / M output | Used by |
| --- | ---: | ---: | --- |
| Sonnet 4.6 | 3.00 | 15.00 | Judge, Debaters, Fact-Checker |
| Haiku 4.5 | 0.80 | 4.00 | Commentator, Crowd |

Per-debate dollar estimate at default settings:

```
Sonnet input:   33 000 tokens · $3   /M = $0.099
Sonnet output:  16 500 tokens · $15  /M = $0.247
Haiku  input:    6 000 tokens · $0.8 /M = $0.005
Haiku  output:   3 000 tokens · $4   /M = $0.012
Web search:     20 calls     · $0.01    = $0.200
                                          -------
                                          ≈ $0.56 / debate
```

Range across observed runs: **$0.40 – $1.20** depending on how verbose the personas get; the hard cap in `rate_limits.json` is **$10 / debate**, well above the typical envelope. The cap exists for runaway-loop protection, not budget squeezing.

### 1.3 Cost cap enforcement

The gatekeeper (`src/debate_ai/services/gatekeeper.py`) tracks cumulative spend per debate. If `cost_caps.max_cost_usd_per_debate` is breached, the active call is allowed to finish (so we don't leave a half-formed message in the log), then the orchestrator aborts with a clean `CostCapExceeded` exception. Tests in `tests/unit/test_gatekeeper.py` cover the cap path.

## 2. Cost-reduction levers

If a future operator wants to run debates at lower cost, the following knobs are exposed in config without code changes:

| Lever | File | Effect |
| --- | --- | --- |
| Reduce `pings_per_side` from 10 → 5 | `config/setup.json` | ~50 % cost reduction; the assignment brief explicitly allows it with a budget note (see README §10). |
| Switch Sonnet → Haiku for one persona | `config/models.json` | ~70 % reduction for that persona's contribution. |
| Disable Fact-Checker | `config/setup.json:agents.fact_checker.enabled` | ~20 % reduction; loses the live-claim-annotation feature. |
| Disable color crew (Commentator + Crowd) | `config/setup.json:agents.{commentator,crowd}.enabled` | ~5 % reduction; loses atmosphere. |
| Self-hosted web search (Tavily / Exa) | `config/rate_limits.json:web_search_provider` | Provider-dependent; Tavily ~$0.001/call instead of Anthropic's $0.01. |

The orchestrator reads all of these at boot — none require recompilation, code edits, or rebuilds.

## 3. Scaling notes

The current implementation runs **one debate per process**. If we wanted to scale to, say, 1 000 debates a day:

- **Anthropic rate limits** become the bottleneck before dollars do. `rate_limits.json` caps us at 10 req/s with concurrency 4; the gatekeeper FIFO queues overflow rather than dropping. At ~64 Anthropic calls per debate and 4-way concurrency, a debate completes in ~30 s wall-clock; the queue holds the rest.
- **Cost at 1 000 debates/day** ≈ $560/day (≈ $200 K/year). At that volume we would (a) batch Fact-Checker calls via Claude's batches API for ~50 % discount, (b) move Commentator + Crowd to local-hosted small models, and (c) move web-search to a cheaper provider. The architecture is set up for this — the agents are subclasses of `BaseAgent`, model assignment is JSON, the gatekeeper abstracts the API.
- **Storage** grows by ~50 KB of JSONL log per debate. At 1 000/day that's 50 MB/day, ~18 GB/year — log rotation (configured at 20×500 lines in `config/logging.json`) keeps disk usage bounded if we trim aged debates.

## 4. Comparison vs the equivalent human task

For honesty: a human-judged debate of similar scope (two researchers, one judge, a moderator, an annotator) would cost roughly **$200–500 of labor for ~30 minutes** of output. The AI version produces equivalent transcript volume at $0.56 in ~3 minutes. The 99.7 % cost reduction is the actual value proposition; that's the number we'd put on a slide.

## 5. What's NOT included in this cost analysis

- **Developer time** (sunk cost of building the engine — out of scope for ops cost).
- **Anthropic API enterprise rates** that the user has access to (likely lower than list prices; we use list prices here for portability).
- **Egress / compute** when running on a paid VM (negligible at this throughput; ~$0.01 / debate at AWS t3.small).

If the assumptions in §1.2 (token counts, model mix) shift materially, regenerate this doc — don't patch numbers inline.
