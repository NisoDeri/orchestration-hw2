"""Commentator agent — colour commentary between rounds.

Part of the Color Crew bundle. The Commentator watches the debate and
produces a short, entertaining line after each round — never during.
Output feeds the UI and HTML replay, NOT the Judge scoring.
"""

from __future__ import annotations

from debate_ai.agents.base_agent import AgentContext, BaseAgent
from debate_ai.models.message_models import CommentaryReply, JudgeEnvelope
from debate_ai.shared.exceptions import SchemaError

COMMENTATOR_SYSTEM_PROMPT = (
    "You are the Commentator in a live Messi vs Ronaldo debate. "
    "After each round the Judge relays the latest exchange to you. "
    "Write a short, witty colour-commentary line (5-400 chars). "
    "Pick a tone: neutral, favouring_a (Messi), or favouring_b (Ronaldo). "
    "Respond ONLY with a JSON CommentaryReply: {commentary, tone, round_ref}."
)


class CommentatorAgent(BaseAgent):
    """Produces colour commentary after each round."""

    def __init__(self, ctx: AgentContext) -> None:
        super().__init__(ctx, system_prompt=COMMENTATOR_SYSTEM_PROMPT)

    def respond(self, envelope: JudgeEnvelope) -> CommentaryReply:
        """Generate a commentary line for the just-finished round."""
        prompt = self._commentary_prompt(envelope)
        messages = self._build_messages() or [
            {"role": "user", "content": prompt},
        ]
        response = self._call_anthropic(messages=messages)
        payload = self._extract_payload(response)
        return self._validate(payload, envelope.round)

    def _commentary_prompt(self, envelope: JudgeEnvelope) -> str:
        return (
            f"Round {envelope.round} just ended ({envelope.kind.value}). "
            f"Latest exchange: {envelope.payload!r}. "
            f"Write a punchy 1-line commentary. Respond ONLY with JSON: "
            f"{{commentary, tone, round_ref}}."
        )

    def _validate(self, payload: dict, round_ref: int) -> CommentaryReply:
        payload.setdefault("round_ref", round_ref)
        try:
            return CommentaryReply.model_validate(payload)
        except Exception as e:  # noqa: BLE001
            raise SchemaError(f"commentator: invalid CommentaryReply: {e}") from e
