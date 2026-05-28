"""Child -> father -> child routing enforcer.

Every utterance in the debate passes through the Judge (father). Debaters
never communicate directly. This module validates routing rules and
determines the next recipient for each message.
"""

from __future__ import annotations

from debate_ai.constants import AgentRole, EnvelopeKind
from debate_ai.shared.exceptions import RouteError

_JUDGE = AgentRole.JUDGE.value
_DA = AgentRole.DEBATER_A.value
_DB = AgentRole.DEBATER_B.value
_SUPPORT = frozenset(
    {
        AgentRole.COMMENTATOR.value,
        AgentRole.CROWD.value,
        AgentRole.FACT_CHECKER.value,
    }
)


def validate_route(sender: str, recipient: str) -> None:
    """Raise ``RouteError`` if sender -> recipient violates topology."""
    if sender in (_DA, _DB) and recipient != _JUDGE:
        raise RouteError(f"debater {sender} tried to address {recipient} directly")
    if sender in _SUPPORT and recipient != _JUDGE:
        raise RouteError(f"support agent {sender} tried to address {recipient}")


def opponent_of(debater: str) -> str:
    """Return the opposing debater role string."""
    if debater == _DA:
        return _DB
    if debater == _DB:
        return _DA
    raise RouteError(f"{debater} is not a debater role")


def next_recipient(
    sender: str,
    kind: EnvelopeKind,
    round_index: int,
    pings_per_side: int,
) -> str:
    """Determine who the Judge should relay the message to next."""
    if sender == _DA:
        return _DB
    if sender == _DB:
        return _DA
    if sender == _JUDGE:
        if kind in (EnvelopeKind.OPENING, EnvelopeKind.ERA_SWAP):
            return _DA
        return _DA
    raise RouteError(f"unexpected sender for routing: {sender}")


def is_round_complete(
    a_pings_this_round: int,
    b_pings_this_round: int,
) -> bool:
    """True when both debaters have spoken at least once this round."""
    return a_pings_this_round >= 1 and b_pings_this_round >= 1
