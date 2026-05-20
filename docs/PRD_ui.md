# PRD — UI

**Version**: 1.00 · Two interfaces, one event stream. The terminal menu is what gets graded; the HTML chat UI is the differentiator.

## 1. The event bus

Everything the UI shows is a `UIEvent` emitted by the orchestrator. One emitter, two subscribers (menu's "watch live" loop + FastAPI's SSE endpoint).

```python
class UIEvent(BaseModel):
    debate_id: str
    seq: int
    ts: datetime
    kind: Literal[
        "debate_started", "round_changed",
        "agent_started_typing", "agent_message",
        "score_update", "drift_warning",
        "fact_check", "commentary", "crowd_reaction",
        "verdict", "debate_ended", "error"
    ]
    payload: dict  # discriminated by kind
```

The emitter is in-process, lock-protected, and replayable: `EventEmitter.replay(from_seq=0)` returns everything since debate start (used when a browser tab connects mid-debate).

## 2. Terminal menu (canonical, graded)

`src/debate_ai/cli/menu.py` — Typer + Rich. Loop:

```
debate-ai
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Run debate (default motion + personas)
[2] Choose motion ...
[3] Choose personas (A: messi | B: ronaldo)
[4] Run + watch live in this terminal
[5] Show last verdict
[6] Browse replays
[7] Tail logs
[8] Show config / version
[0] Quit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pick:
```

- Every item is one SDK call. No business logic in the menu.
- Item [4] subscribes to the same `UIEvent` stream the HTML UI would; renders chat bubbles inline with Rich panels.
- Keyboard-only. No mouse. Grading-friendly.

## 3. HTML chat UI (bonus, differentiator)

### Backend

`src/debate_ai/ui/server.py` — FastAPI:

| Route | Returns |
| --- | --- |
| `GET /` | `static/index.html` |
| `GET /static/*` | static assets |
| `GET /stream?debate_id=<id>` | Server-Sent Events — `text/event-stream`, one `data: <json>\n\n` per `UIEvent` |
| `POST /start` | starts a new debate (body: motion, persona-a, persona-b, pings); returns `{ debate_id }` |
| `GET /verdict/{debate_id}` | the final `Verdict` once emitted |
| `GET /replay/{debate_id}` | self-contained styled HTML file (download) |

SSE rationale: one-way, server → client, no handshake. The browser uses `EventSource` (native). When the page connects, the server calls `emitter.replay(from_seq=last_event_id)` so the client never misses an event.

### Frontend

Three files, no framework, no build step:

- `static/index.html` — semantic HTML: header (motion, round badge, status), main grid (chat column + scoreboard sidebar), footer (controls).
- `static/styles.css` — Telegram/WhatsApp-style bubbles, agent-colored (each persona has a `color_hex`), responsive grid (chat 70 % / sidebar 30 % on desktop, stacked on narrow).
- `static/app.js` — `EventSource('/stream?debate_id=…')`; one event-kind handler per `UIEvent.kind`; appends bubbles, updates scoreboard, animates typing indicator.

### Chat-bubble layout

```
┌─────────────────────────────────── debate-ai ─ ⚪ Round 3/5 ───────────────────────┐
│                                                                                    │
│   Judge · 20:14                                                                    │
│   ┌────────────────────────────────────┐                                           │
│   │ Welcome. Tonight's motion is...    │                                           │
│   └────────────────────────────────────┘                                           │
│                                                                                    │
│                                                       Debater-A (Messi) · 20:14    │
│                                                  ┌───────────────────────────┐    │
│                                                  │ 8 Ballon d'Ors, 4 CL...    │   │
│                                                  │ ── citation: bbc.com/...   │   │
│                                                  └───────────────────────────┘    │
│                                                                                    │
│   ⚠ Fact-Checker: "Ronaldo has 5 Ballon d'Ors" → recorded 5 ✓                     │
│                                                                                    │
│   Debater-B (Ronaldo) · 20:15                                                      │
│   ┌────────────────────────────────────┐                                           │
│   │ Yet I scored 140 in the CL...      │                                           │
│   └────────────────────────────────────┘                                           │
│                                                                                    │
│   🎙 Commentator: "Ronaldo just landed a haymaker on the CL run..."                 │
│   👥 Crowd: 🔥🔥🔥 — they're going for it                                            │
│                                                                                    │
├──────────────────────────────────── sidebar ─────────────────────────────────────┤
│   Scoreboard         Confidence            Round 3 of 5                            │
│   Messi    78        ▓▓▓▓▓▓▓░░ 67 %        ▣ Era-swap next (1973-style)            │
│   Ronaldo  72        ▓▓▓▓▓▓░░░ 58 %                                                 │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### Replay export

When the debate ends, the server writes `replays/<debate_id>.html`. The file:

1. Inlines `styles.css` and `app.js` (no external deps).
2. Embeds the full `UIEvent` stream as a `<script>const events = [...]</script>` constant.
3. On load, `app.js` runs the events through the same renderer used live — at 5× speed by default, with playback controls (pause, scrub, slow-mo).

Result: a single `.html` file is the replay. No server needed to view; perfect for README screenshots and Moodle handoff.

## 4. Browser launch

`uv run debate-ai start` → uvicorn on `localhost:8000` → `webbrowser.open("http://localhost:8000")`. `--no-browser` flag for CI / SSH.

## 5. Tests

- `test_event_emitter.py` — replay(from_seq=N) returns everything since N.
- `test_sse_endpoint.py` — FastAPI TestClient subscribes, receives N events, disconnects cleanly.
- `test_menu_loop.py` — menu key sequences drive SDK methods; no business logic in handlers.
- `test_replay_html_selfcontained.py` — generated replay opens in headless Chromium without network.
