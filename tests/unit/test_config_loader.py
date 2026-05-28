"""Tests for ``shared.config.ConfigLoader``.

Uses the *real* shipped configs under ``config/`` to verify they round-trip.
A separate set of tests uses ``tmp_config_dir`` to assert error paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from debate_ai.shared.config import ConfigLoader
from debate_ai.shared.exceptions import ConfigError, ConfigVersionError
from tests.conftest import write_json

REPO_CONFIG_DIR = Path(__file__).parents[2] / "config"


def test_loader_loads_real_setup() -> None:
    loader = ConfigLoader(REPO_CONFIG_DIR)
    setup = loader.load("setup")
    assert setup.pings_per_side == 10  # type: ignore[attr-defined]


def test_loader_validates_every_real_config() -> None:
    ConfigLoader(REPO_CONFIG_DIR).validate_all()


def test_loader_lists_personas() -> None:
    personas = ConfigLoader(REPO_CONFIG_DIR).list_personas()
    assert {"messi", "ronaldo"}.issubset(set(personas))


def test_loader_loads_persona() -> None:
    p = ConfigLoader(REPO_CONFIG_DIR).load_persona("messi")
    assert p.name == "Messi"
    assert p.has_eras()


def test_loader_raises_for_missing_config_dir(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        ConfigLoader(tmp_path / "does-not-exist")


def test_loader_raises_for_missing_versions(tmp_config_dir: Path) -> None:
    # versions.json absent
    with pytest.raises(ConfigError):
        ConfigLoader(tmp_config_dir).versions()


def test_loader_raises_for_unknown_config_name(tmp_config_dir: Path) -> None:
    write_json(
        tmp_config_dir / "versions.json",
        {
            "version": "1.00",
            "code": "1.00",
            "configs": {"setup": "1.00"},
        },
    )
    loader = ConfigLoader(tmp_config_dir)
    with pytest.raises(ConfigError):
        loader.load("nonexistent")


def test_loader_raises_on_version_mismatch(tmp_config_dir: Path) -> None:
    write_json(
        tmp_config_dir / "versions.json",
        {
            "version": "1.00",
            "code": "1.00",
            "configs": {"setup": "2.00"},
        },
    )
    write_json(tmp_config_dir / "setup.json", _MIN_SETUP)
    with pytest.raises(ConfigVersionError):
        ConfigLoader(tmp_config_dir).load("setup")


def test_loader_raises_on_malformed_json(tmp_config_dir: Path) -> None:
    write_json(
        tmp_config_dir / "versions.json",
        {
            "version": "1.00",
            "code": "1.00",
            "configs": {"setup": "1.00"},
        },
    )
    (tmp_config_dir / "setup.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        ConfigLoader(tmp_config_dir).load("setup")


def test_loader_raises_on_missing_persona_file(tmp_config_dir: Path) -> None:
    write_json(
        tmp_config_dir / "versions.json",
        {
            "version": "1.00",
            "code": "1.00",
            "configs": {"personas": "1.00"},
        },
    )
    with pytest.raises(ConfigError):
        ConfigLoader(tmp_config_dir).load_persona("ghost")


_MIN_SETUP = {
    "version": "1.00",
    "pings_per_side": 10,
    "era_swap_round_index": 4,
    "era_swap_strategy": "contrasting",
    "agents_enabled": {
        "judge": True,
        "debater_a": True,
        "debater_b": True,
        "commentator": True,
        "crowd": True,
        "fact_checker": True,
    },
    "watchdog": {
        "timeout_s_per_call": 60.0,
        "max_restarts_per_agent": 3,
        "keepalive_interval_s": 5.0,
        "on_unrecoverable": "force_verdict_from_aggregate",
    },
    "judge": {"verdict_no_tie_retries": 1, "drift_window_turns": 2, "agreement_keywords": ["yes,"]},
    "ui": {"host": "127.0.0.1", "port": 8000, "open_browser_on_start": True},
    "replay": {"dir": "replays", "playback_speed_default": 5.0},
}
