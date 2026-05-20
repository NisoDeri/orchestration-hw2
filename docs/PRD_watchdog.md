# PRD — Watchdog + timeouts

**Version**: 1.00 · Mandatory per HW2 brief §8.6 ("Timeouts on every request. Watchdog with keep-alive — if a process falls, kill and restart").

## 1. Failure modes covered

1. **Network hang** — Anthropic call never returns within `timeout_s`.
2. **Schema break** — agent returns malformed JSON or missing required field.
3. **Citation missing** — debater reply has empty `citations`.
4. **Drift** — two consecutive turns of cross-debater agreement (separate detector, see `PRD_judge.md` §7).
5. **Cost cap exceeded** — gatekeeper trips (see `PRD_tools.md` §5).
6. **Exception in tool call** — web_search 500, web_fetch refused, MCP timeout.

Each mode has a deterministic, config-driven recovery.

## 2. Architecture

```
DebateManager
   └─ for each agent turn:
        └─ Watchdog.supervise(
              fn      = agent.respond,
              args    = (envelope,),
              timeout = config.timeout_s,
              on_hang = restart_agent,
           )
```

`Watchdog.supervise`:
- Submits `fn(*args)` to a `ThreadPoolExecutor(max_workers=1)` future.
- Polls `future.result(timeout=timeout_s)`.
- On `TimeoutError` or `Exception` → calls `on_hang(agent)`, which re-instantiates the agent and returns the new instance. Retries up to `max_restarts` times.
- On `max_restarts` exceeded → raises `AgentUnrecoverable`, which the `DebateManager` catches → forces a `Verdict` from current aggregate → ends debate with `UIEvent(kind="error", payload={"reason": "agent_unrecoverable", "agent_id": ...})`.

Threads are used (not multiprocessing) because the work is I/O-bound on the Anthropic call. Cancellation of a Python thread is best-effort; recovery is "drop the agent object, build a new one" (cheap — agents are stateless except for their `ConversationMemory` view, which is rebuildable from the central transcript).

## 3. Per-mode recovery

| Failure | Detector | Recovery |
| --- | --- | --- |
| Network hang | `Watchdog` timeout | Restart agent; retry the same envelope. |
| Schema break | Pydantic `ValidationError` raised in `_validate_reply` | Retry once with an appended system instruction `"Respond in valid JSON only. Schema: {...}"`. Second failure → restart agent. |
| Missing citations | `CitedReplyMixin._validate_citations` | Retry once with `"Your reply must include >=1 URL in citations."`. Second failure → restart. |
| Cost cap | `Gatekeeper.cost_so_far_usd() >= max_cost_usd_per_debate` | Stop accepting new calls. Force judge verdict from current aggregate. |
| Tool 5xx | exception bubbling up from `tools/web_search_tool` | Gatekeeper retries per `rate_limits.json::retry_policy`. Exhaustion → restart agent. |

`max_restarts` defaults to 3 per agent per debate (config-tunable). Restart count is shared across failure modes — a flaky agent can be restarted at most 3 times total, not 3-per-mode.

## 4. Keep-alive (the brief's wording)

Between turns, the watchdog pings each idle agent with a no-op (no Anthropic call — just `agent.alive() → True`). This is per-agent state-machine bookkeeping; it does not generate API spend. The "keep-alive" semantics from the brief are honored by the supervisor merely existing and tracking liveness — Anthropic itself is the LLM service; we don't keep TCP connections open.

## 5. Config

```json
// config/setup.json (excerpt)
{
  "watchdog": {
    "timeout_s_per_call": 60,
    "max_restarts_per_agent": 3,
    "keepalive_interval_s": 5,
    "on_unrecoverable": "force_verdict_from_aggregate"
  }
}
```

All fields validated on startup.

## 6. Tests

- `test_watchdog_timeout_restarts.py` — simulate a hang via a stub agent that `time.sleep(timeout + 1)`; assert watchdog restarts and returns valid reply on retry.
- `test_watchdog_max_restarts_exhausted.py` — agent always hangs; after `max_restarts`, `AgentUnrecoverable` raised.
- `test_watchdog_schema_break_retry.py` — first call returns bad JSON, second returns good JSON; assert single retry with stricter prompt suffix.
- `test_watchdog_missing_citation_retry.py` — same pattern, citation arm.
- `test_watchdog_unrecoverable_forces_verdict.py` — `AgentUnrecoverable` → `DebateManager` emits a `Verdict` from running aggregate, debate ends cleanly.
- `test_keepalive_no_api_calls.py` — assert keep-alive ticks do NOT increment gatekeeper call counter.
