"""FastAPI server with SSE for the live debate chat UI."""
from __future__ import annotations

import asyncio
import json
import threading
import webbrowser
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from debate_ai.models.message_models import UIEvent
from debate_ai.orchestration.event_emitter import EventEmitter

app = FastAPI(title="debate-ai", docs_url=None, redoc_url=None)
_STATIC_DIR = Path(__file__).parent / "static"
_emitter: EventEmitter | None = None
_events: list[dict[str, Any]] = []
_lock = threading.Lock()


@app.get("/", response_class=HTMLResponse)
async def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/api/events")
async def events() -> EventSourceResponse:
    async def _stream():
        idx = 0
        while True:
            with _lock:
                batch = _events[idx:]
                idx += len(batch)
            for data in batch:
                yield {"data": json.dumps(data, default=str)}
            if not batch:
                await asyncio.sleep(0.05)
    return EventSourceResponse(_stream())


@app.get("/api/status")
async def status() -> dict:
    return {"status": "running", "emitter": _emitter is not None}


@app.post("/api/demo/start")
async def start_demo() -> dict:
    _cfg = Path(__file__).parents[3] / "config"
    _reset_events()
    emitter = EventEmitter("demo-ui")
    set_emitter(emitter)
    threading.Thread(target=_run_demo_bg, args=(_cfg, emitter), daemon=True).start()
    return {"started": True}


@app.post("/api/debate/start")
async def start_live() -> dict:
    """Start a live debate using the Anthropic API."""
    _reset_events()
    emitter = EventEmitter("live-ui")
    set_emitter(emitter)
    threading.Thread(target=_run_live_bg, args=(emitter,), daemon=True).start()
    return {"started": True}


def _run_demo_bg(cfg_dir: Path, emitter: EventEmitter) -> None:
    from debate_ai.services.demo_service import run_demo_with_emitter
    run_demo_with_emitter(cfg_dir, emitter)


def _run_live_bg(emitter: EventEmitter) -> None:
    from debate_ai.sdk.sdk import run_debate
    try:
        run_debate(emitter=emitter)
    except Exception as exc:  # noqa: BLE001
        emitter.emit("debate_ended", {"error": str(exc)})


def _reset_events() -> None:
    with _lock:
        _events.clear()


def broadcast(event: UIEvent) -> None:
    with _lock:
        _events.append(event.model_dump())


def set_emitter(emitter: EventEmitter) -> None:
    global _emitter  # noqa: PLW0603
    _emitter = emitter
    emitter.subscribe(broadcast)


def launch(host: str = "127.0.0.1", port: int = 8000) -> None:
    url = f"http://{host}:{port}"
    threading.Timer(1.5, webbrowser.open, args=[url]).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")
