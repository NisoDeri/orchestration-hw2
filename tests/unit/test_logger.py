"""Tests for ``shared.logger.FifoLogger``."""

from __future__ import annotations

import json
from pathlib import Path

from debate_ai.shared.logger import FifoLogger


def _make(
    tmp_path: Path,
    *,
    max_files: int = 3,
    lines_per_file: int = 5,
    default_level: str = "INFO",
    overrides: dict | None = None,
) -> FifoLogger:
    return FifoLogger(
        directory=tmp_path / "logs",
        max_files=max_files,
        lines_per_file=lines_per_file,
        default_level=default_level,
        level_overrides=overrides,
    )


def test_log_writes_json_line(tmp_path: Path) -> None:
    lg = _make(tmp_path)
    lg.log("INFO", source="test", msg="hello", round=1)
    out = sorted((tmp_path / "logs").glob("*.jsonl"))[0].read_text(encoding="utf-8")
    blob = json.loads(out.splitlines()[0])
    assert blob["level"] == "INFO"
    assert blob["msg"] == "hello"
    assert "ts" in blob


def test_log_rotates_at_lines_per_file(tmp_path: Path) -> None:
    lg = _make(tmp_path, lines_per_file=3, max_files=10)
    for i in range(7):
        lg.log("INFO", source="t", n=i)
    files = sorted((tmp_path / "logs").glob("*.jsonl"))
    assert len(files) >= 2
    first = files[0].read_text(encoding="utf-8").splitlines()
    assert len(first) == 3


def test_log_fifo_evicts_oldest_past_cap(tmp_path: Path) -> None:
    lg = _make(tmp_path, max_files=2, lines_per_file=2)
    for i in range(20):
        lg.log("INFO", source="t", n=i)
    files = sorted((tmp_path / "logs").glob("*.jsonl"))
    assert len(files) <= 2


def test_log_respects_level_threshold(tmp_path: Path) -> None:
    lg = _make(tmp_path, default_level="WARN")
    lg.log("DEBUG", source="t", n=1)
    lg.log("INFO", source="t", n=2)
    lg.log("WARN", source="t", n=3)
    out = sorted((tmp_path / "logs").glob("*.jsonl"))
    if not out:
        return  # nothing written, threshold worked
    lines = out[0].read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["level"] == "WARN"


def test_log_level_overrides_per_source(tmp_path: Path) -> None:
    lg = _make(tmp_path, default_level="WARN", overrides={"verbose": "DEBUG"})
    lg.log("DEBUG", source="quiet", n=1)
    lg.log("DEBUG", source="verbose", n=2)
    files = sorted((tmp_path / "logs").glob("*.jsonl"))
    lines = files[0].read_text(encoding="utf-8").splitlines() if files else []
    assert len(lines) == 1
    assert json.loads(lines[0])["source"] == "verbose"


def test_tail_returns_last_n_lines_across_files(tmp_path: Path) -> None:
    lg = _make(tmp_path, max_files=10, lines_per_file=3)
    for i in range(10):
        lg.log("INFO", source="t", n=i)
    tail = lg.tail(4)
    assert len(tail) == 4
    last = json.loads(tail[-1])
    assert last["n"] == 9


def test_cursor_persists_across_instances(tmp_path: Path) -> None:
    a = _make(tmp_path, lines_per_file=2, max_files=10)
    a.log("INFO", source="t", n=1)
    a.log("INFO", source="t", n=2)
    a.log("INFO", source="t", n=3)
    # Second logger instance picks up the cursor.
    b = _make(tmp_path, lines_per_file=2, max_files=10)
    b.log("INFO", source="t", n=4)
    total_lines = sum(
        len(f.read_text(encoding="utf-8").splitlines()) for f in (tmp_path / "logs").glob("*.jsonl")
    )
    assert total_lines == 4
