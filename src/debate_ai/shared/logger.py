"""Structured JSON logger with FIFO file rotation.

Per HW2 brief §8.6: "structured logs, FIFO defined in config — e.g. 20 files
x 500 lines". Each log line is one JSON object on its own line. Files are
named ``NN.jsonl`` (zero-padded). When the active file's line count hits
``lines_per_file``, we roll to the next file; when total files exceed
``max_files``, the oldest is unlinked.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from debate_ai.constants import LogLevel

_LEVEL_RANK: dict[str, int] = {
    LogLevel.DEBUG.value: 10,
    LogLevel.INFO.value: 20,
    LogLevel.WARN.value: 30,
    LogLevel.ERROR.value: 40,
}


class FifoLogger:
    """Append JSON lines into a bounded ring of files.

    Concurrency-safe via a single instance-level ``RLock``. Callers do not
    need to coordinate.
    """

    def __init__(
        self,
        directory: Path | str,
        max_files: int,
        lines_per_file: int,
        default_level: str = "INFO",
        level_overrides: dict[str, str] | None = None,
    ) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.max_files = max_files
        self.lines_per_file = lines_per_file
        self.default_level = default_level
        self.level_overrides = dict(level_overrides or {})
        self._lock = threading.RLock()
        self._cursor_path = self.dir / ".cursor"
        self._idx, self._count = self._load_cursor()

    def log(self, level: str, source: str = "", **fields: Any) -> None:
        """Write one JSON line at the given level if it passes the threshold."""
        if not self._passes(level, source):
            return
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": level,
            "source": source,
            **fields,
        }
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self._lock:
            self._write_line(line)

    def tail(self, n: int) -> list[str]:
        """Return the last ``n`` lines across all rotation files, oldest first."""
        files = sorted(self.dir.glob("*.jsonl"))
        lines: list[str] = []
        for f in files:
            lines.extend(f.read_text(encoding="utf-8").splitlines())
        return lines[-n:] if n < len(lines) else lines

    def _passes(self, level: str, source: str) -> bool:
        threshold = self.level_overrides.get(source, self.default_level)
        try:
            return _LEVEL_RANK[level] >= _LEVEL_RANK[threshold]
        except KeyError:
            return True

    def _write_line(self, line: str) -> None:
        self._rotate_if_needed()
        path = self.dir / f"{self._idx:04d}.jsonl"
        with path.open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")
        self._count += 1
        self._save_cursor()

    def _rotate_if_needed(self) -> None:
        if self._count >= self.lines_per_file:
            self._idx += 1
            self._count = 0
            self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        files = sorted(self.dir.glob("*.jsonl"))
        while len(files) >= self.max_files:
            files[0].unlink(missing_ok=True)
            files = files[1:]

    def _load_cursor(self) -> tuple[int, int]:
        if not self._cursor_path.is_file():
            return (0, 0)
        try:
            blob = json.loads(self._cursor_path.read_text(encoding="utf-8"))
            return int(blob["idx"]), int(blob["count"])
        except (json.JSONDecodeError, KeyError, ValueError):
            return (0, 0)

    def _save_cursor(self) -> None:
        self._cursor_path.write_text(
            json.dumps({"idx": self._idx, "count": self._count}),
            encoding="utf-8",
        )
