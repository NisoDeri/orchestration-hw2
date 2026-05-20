"""Immutable project constants — enums for roles, kinds, and levels.

Per HW2 brief §8.6 ("no hardcoded parameters") only *categorical* constants
live here. Numeric tunables (rounds, timeouts, weights) live in ``config/``.
"""

from __future__ import annotations

from enum import Enum


class AgentRole(str, Enum):
    """Stable identifiers for each agent class.

    Used as the discriminator in JudgeEnvelope.from/to and as the lookup key
    in ``config/models.json``.
    """

    JUDGE = "judge"
    DEBATER_A = "debater-a"
    DEBATER_B = "debater-b"
    COMMENTATOR = "commentator"
    CROWD = "crowd"
    FACT_CHECKER = "fact-checker"


class RoundKind(str, Enum):
    """The four round phases of a debate.

    ``era_swap`` is structurally identical to ``rebuttal`` but tagged so the
    UI can announce it and the era-swap mechanism knows to swap personas in.
    """

    OPENING = "opening"
    REBUTTAL = "rebuttal"
    ERA_SWAP = "era_swap"
    CLOSING = "closing"


class EnvelopeKind(str, Enum):
    """The kinds of envelopes the Judge can relay or emit."""

    OPENING = "opening"
    REBUTTAL = "rebuttal"
    ERA_SWAP = "era_swap"
    CLOSING = "closing"
    RULING = "ruling"
    COMMENTARY = "commentary"
    CROWD = "crowd"
    FACT_CHECK = "fact_check"
    VERDICT = "verdict"


class LogLevel(str, Enum):
    """JSON log line levels per ``docs/PRD_logging.md`` §2."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Side(str, Enum):
    """Which side of the debate a debater argues."""

    PRO = "pro"
    CON = "con"
