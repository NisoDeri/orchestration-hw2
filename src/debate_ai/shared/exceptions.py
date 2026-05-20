"""Project exception hierarchy.

Every error raised by code in this package inherits from ``DebateAIError`` so
callers can ``except DebateAIError`` if they want a broad catch — but normally
they should catch the specific subtype. Test suites grep for use of the base
class in production code and warn.
"""

from __future__ import annotations


class DebateAIError(Exception):
    """Base class for every error this project raises."""


class ConfigError(DebateAIError):
    """Raised by ``shared.config`` when a config file is missing / malformed."""


class ConfigVersionError(ConfigError):
    """A loaded config's ``version`` does not match what the code expects."""


class SchemaError(DebateAIError):
    """An agent reply does not conform to its Pydantic schema."""


class CitationError(SchemaError):
    """A debater reply is missing the mandatory ``citations`` array."""


class RouteError(DebateAIError):
    """An attempt to deliver an envelope to the wrong recipient.

    Raised by ``orchestration.routing`` when the brief's child -> father -> child
    topology is violated.
    """


class CostCapExceededError(DebateAIError):
    """The gatekeeper's per-debate cost cap was reached."""


class AgentUnrecoverableError(DebateAIError):
    """An agent failed past ``max_restarts_per_agent``.

    The debate manager catches this and forces a verdict from the running
    aggregate so the debate ends cleanly.
    """


class VerdictTieError(DebateAIError):
    """The Judge LLM emitted a tie verdict that survived all retries.

    The orchestrator catches this and falls back to the running-aggregate
    winner — the brief forbids ties.
    """


class WatchdogTimeoutError(DebateAIError):
    """An agent call exceeded the per-call timeout."""
