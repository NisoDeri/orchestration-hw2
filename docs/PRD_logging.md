# PRD — Logging (FIFO file rotation)

**Version**: 1.00 · Mandatory per HW2 brief §8.6 ("Structured logs — ready package, FIFO defined in the configuration file — e.g. 20 files, each up to 500 lines").

## 1. Goals

- Structured, line-delimited JSON log records.
- Bounded disk footprint: max `N` files × `L` lines each, oldest dropped (FIFO).
- One log line per significant event (Anthropic call started/finished, envelope relayed, score updated, error, etc.).
- Cheaply tailable from the CLI menu.

## 2. Schema (one JSON object per line)

```json
{
  "ts": "2026-05-20T20:14:03.142Z",
  "level": "INFO" | "WARN" | "ERROR" | "DEBUG",
  "debate_id": "uuid",
  "round": 3,
  "agent": "judge" | "debater-a" | ...,
  "kind": "anthropic_call_started" | "anthropic_call_finished" | "envelope_relayed"
        | "score_update" | "watchdog_restart" | "cost_cap_hit" | "drift_detected"
        | "verdict_emitted" | "fact_check" | ...,
  "msg": "human-readable text",
  "fields": { "...": "..." }
}
```

`debate_id` may be absent for pre-debate logs (startup, config validation).

## 3. FIFO rotation

`shared/logger.py::FifoLogger`:

- Writes into `logs/<NN>.jsonl` where `NN` is a monotonically incremented zero-padded counter.
- When the current file's line count hits `lines_per_file`, rolls to the next file.
- When total file count exceeds `max_files`, oldest is unlinked.
- Counter persisted to `logs/.cursor` so restart picks up where it left off (no overwrite).

```json
// config/logging.json (excerpt)
{
  "version": "1.00",
  "dir": "logs",
  "max_files": 20,
  "lines_per_file": 500,
  "default_level": "INFO",
  "level_overrides": { "tools.web_search_tool": "DEBUG" }
}
```

## 4. Integration

- All Anthropic calls are routed through `Gatekeeper`, which logs `anthropic_call_started` (with the prompt cache_control hash) and `anthropic_call_finished` (with token usage + cost estimate).
- Every relayed `JudgeEnvelope` is logged once (`envelope_relayed`).
- Watchdog restarts → `watchdog_restart` with `agent`, `restart_count`, `reason`.
- Drift detector → `drift_detected`, includes the matching agreement quotes.
- Score updates → `score_update`, with running aggregate.

Agents do **not** log directly; they emit events into the orchestrator, which logs. Single sink, single format.

## 5. Tailing from the menu

Menu item `[7] Tail logs` calls `FifoLogger.tail(n=100)`:

- Returns the last 100 lines across files (boundary-aware).
- Rich-rendered into a colored panel.
- Live mode: `[7] Tail logs (live)` polls the current file via `inotify` (Linux) / file mtime (Windows) and streams new lines.

## 6. Tests

- `test_logger_rotation.py` — write `lines_per_file + 5` lines, assert rollover to next file index.
- `test_logger_fifo_eviction.py` — write past `max_files * lines_per_file`, assert oldest file is unlinked.
- `test_logger_schema.py` — every emitted line parses as JSON and has required keys.
- `test_logger_cursor_persistence.py` — kill the logger mid-run, recreate it, assert next line goes to the right file.
- `test_logger_no_logs_from_agents.py` — grep the agent modules for `logger.` calls — there should be zero.
