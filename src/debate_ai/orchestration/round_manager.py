"""Round lifecycle — knows which round we're in and when to advance.

The RoundManager tracks rounds, determines round kinds (opening, rebuttal,
era_swap, closing), and tells the orchestrator when to stop. It is purely
computational — no I/O, no API calls.
"""

from __future__ import annotations

from debate_ai.constants import RoundKind
from debate_ai.models.config_models import SetupConfig


class RoundManager:
    """Track round index and map it to a RoundKind."""

    def __init__(self, setup: SetupConfig) -> None:
        self.pings_per_side = setup.pings_per_side
        self.era_swap_round = setup.era_swap_round_index
        self.total_rounds = setup.pings_per_side
        self._current = 0

    @property
    def current_round(self) -> int:
        return self._current

    def kind_for(self, round_index: int) -> RoundKind:
        """Map a round index to its kind."""
        if round_index == 0:
            return RoundKind.OPENING
        if round_index == self.total_rounds - 1:
            return RoundKind.CLOSING
        if self.era_swap_round is not None and round_index == self.era_swap_round:
            return RoundKind.ERA_SWAP
        return RoundKind.REBUTTAL

    def current_kind(self) -> RoundKind:
        return self.kind_for(self._current)

    def advance(self) -> int:
        """Move to next round; return the new index."""
        self._current += 1
        return self._current

    def is_last_round(self) -> bool:
        return self._current >= self.total_rounds - 1

    def is_debate_over(self) -> bool:
        return self._current >= self.total_rounds

    def is_era_swap_round(self) -> bool:
        if self.era_swap_round is None:
            return False
        return self._current == self.era_swap_round
