"""Crowd agent — audience emoji + one-liner reaction.

Part of the Color Crew bundle. The Crowd reacts to individual debater
turns with an emoji set and a short one-liner. Output feeds the UI;
never the Judge scoring pipeline.
"""

from __future__ import annotations

from debate_ai.agents.base_agent import AgentContext, BaseAgent
from debate_ai.models.message_models import CrowdReply, JudgeEnvelope
from debate_ai.shared.exceptions import SchemaError

CROWD_SYSTEM_PROMPT = (
    "You are the Crowd in a live Messi vs Ronaldo debate. "
    "React to each debater turn with 1-5 emojis and a one-liner (max 80 chars). "
    "lean is a float from -1.0 (strongly Messi) to +1.0 (strongly Ronaldo). "
    "Respond ONLY with a JSON CrowdReply: {envelope_ref, emojis, one_liner, lean}."
)


class CrowdAgent(BaseAgent):
    """Produces emoji + one-liner crowd reactions."""

    def __init__(self, ctx: AgentContext) -> None:
        super().__init__(ctx, system_prompt=CROWD_SYSTEM_PROMPT)

    def respond(self, envelope: JudgeEnvelope) -> CrowdReply:
        """React to a single debater turn."""
        prompt = self._crowd_prompt(envelope)
        messages = self._build_messages() or [
            {"role": "user", "content": prompt},
        ]
        response = self._call_anthropic(messages=messages)
        payload = self._extract_payload(response)
        return self._validate(payload, envelope.envelope_id)

    def _crowd_prompt(self, envelope: JudgeEnvelope) -> str:
        return (
            f"Debater turn (round {envelope.round}, {envelope.kind.value}). "
            f"Sender: {envelope.sender}. Content: {envelope.payload!r}. "
            f"React with emojis + a one-liner. "
            f"Respond ONLY with JSON: {{envelope_ref, emojis, one_liner, lean}}."
        )

    def _validate(self, payload: dict, envelope_id: str) -> CrowdReply:
        payload.setdefault("envelope_ref", envelope_id)
        try:
            return CrowdReply.model_validate(payload)
        except Exception as e:  # noqa: BLE001
            raise SchemaError(f"crowd: invalid CrowdReply: {e}") from e
