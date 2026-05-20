"""FastAPI server with SSE for the live debate chat UI.

Serves a single-page HTML chat interface. Debate events are streamed
to connected clients via Server-Sent Events. ``launch()`` boots
uvicorn and opens the browser.
"""

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
from sse_starlette.sse import EventSourceResponse

from debate_ai.models.message_models import UIEvent
from debate_ai.orchestration.event_emitter import EventEmitter

app = FastAPI(title="debate-ai", docs_url=None, redoc_url=None)
_STATIC_DIR = Path(__file__).parent / "static"
_event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_emitter: EventEmitter | None = None


@app.get("/", response_class=HTMLResponse)
async def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/api/events")
async def events() -> EventSourceResponse:
    async def _stream():
        while True:
            data = await _event_queue.get()
            yield {"data": json.dumps(data, default=str)}
    return EventSourceResponse(_stream())


@app.get("/api/status")
async def status() -> dict:
    return {"status": "running", "emitter": _emitter is not None}


def broadcast(event: UIEvent) -> None:
    """Push a UIEvent into the SSE queue (thread-safe)."""
    import contextlib
    with contextlib.suppress(asyncio.QueueFull):
        _event_queue.put_nowait(event.model_dump())


def set_emitter(emitter: EventEmitter) -> None:
    """Wire the debate's EventEmitter to the SSE broadcast."""
    global _emitter  # noqa: PLW0603
    _emitter = emitter
    emitter.subscribe(broadcast)


def launch(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Boot uvicorn and open the browser."""
    url = f"http://{host}:{port}"
    threading.Timer(1.5, webbrowser.open, args=[url]).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")
