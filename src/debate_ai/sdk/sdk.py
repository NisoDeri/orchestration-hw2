"""SDK — single public entry point for all debate-ai business logic.

Per CLAUDE.md §4: "every function containing business logic must be
reachable through sdk/". CLI, UI, and REST handlers are thin wrappers
that call this module.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import anthropic

from debate_ai.models.debate_models import DebateResult
from debate_ai.orchestration.event_emitter import EventEmitter
from debate_ai.services.debate_service import DebateService
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.config import ConfigLoader
from debate_ai.shared.gatekeeper import Gatekeeper
from debate_ai.shared.logger import FifoLogger
from debate_ai.tools.wikipedia_mcp import WikipediaMCP

_CONFIG_DIR = Path(__file__).parents[3] / "config"


def run_debate(
    config_dir: Path | None = None,
    anthropic_client: Any | None = None,
    emitter: EventEmitter | None = None,
) -> DebateResult:
    """Run a complete debate and return the result."""
    cfg_dir = config_dir or _CONFIG_DIR
    loader = ConfigLoader(cfg_dir)
    loader.validate_all()
    setup = loader.load("setup")
    models = loader.load("models")
    debate_json = loader.load("debate")
    rate_limits = loader.load("rate_limits")
    logging_cfg = loader.load("logging")
    facts_cfg = loader.load("facts")
    persona_a = loader.load_persona(debate_json.persona_a)
    persona_b = loader.load_persona(debate_json.persona_b)
    logger = FifoLogger(
        log_dir=Path(logging_cfg.dir),
        max_files=logging_cfg.max_files,
        lines_per_file=logging_cfg.lines_per_file,
    )
    gatekeeper = Gatekeeper(rate_limits, logger)
    wiki = WikipediaMCP()
    facts_service = FactsService(facts_cfg, wikipedia=wiki)
    client = anthropic_client or _make_client()
    svc = DebateService(
        setup=setup, models_cfg=models,
        persona_a=persona_a, persona_b=persona_b,
        motion=debate_json.motion,
        gatekeeper=gatekeeper, logger=logger,
        facts_service=facts_service, anthropic_client=client,
    )
    return svc.run_debate(emitter=emitter)


def list_personas(config_dir: Path | None = None) -> list[str]:
    """List available persona names."""
    loader = ConfigLoader(config_dir or _CONFIG_DIR)
    return loader.list_personas()


def get_config(config_dir: Path | None = None) -> dict[str, Any]:
    """Return a summary of the current config."""
    loader = ConfigLoader(config_dir or _CONFIG_DIR)
    setup = loader.load("setup")
    debate = loader.load("debate")
    return {
        "motion": debate.motion,
        "pings_per_side": setup.pings_per_side,
        "era_swap_round": setup.era_swap_round_index,
        "personas": [debate.persona_a, debate.persona_b],
    }


def run_demo(config_dir: Path | None = None) -> DebateResult:
    """Run a demo debate with pre-scripted agents (no API key needed)."""
    from debate_ai.services.demo_service import run_demo as _run
    return _run(config_dir or _CONFIG_DIR)


def _make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    return anthropic.Anthropic(api_key=api_key)
