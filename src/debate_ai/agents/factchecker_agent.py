"""Fact-Checker agent — viewer-only claim annotations.

The Fact-Checker annotates debater turns for the **human viewer**. It
NEVER feeds the Judge scoring pipeline (the Judge scores rhetoric, not
correctness). Uses ``FactsService`` for local + Wikipedia lookups; the
LLM call may additionally invoke ``web_search`` for claims the local
sources can't resolve.
"""

from __future__ import annotations

from debate_ai.agents.base_agent import AgentContext, BaseAgent
from debate_ai.models.message_models import (
    FactCheckReply,
    JudgeEnvelope,
)
from debate_ai.services.facts_service import FactsService
from debate_ai.shared.exceptions import SchemaError


class FactCheckerAgent(BaseAgent):
    """Annotates debater claims for the human viewer."""

    SYSTEM_PROMPT = (
        "You are the Fact-Checker in a Messi vs Ronaldo debate. "
        "Your annotations are for the human viewer only — the Judge ignores them. "
        "For each debater turn, extract checkable claims and verify them. "
        "Return ONLY a JSON FactCheckReply: {envelope_ref, claims: [{quote, "
        "verdict, severity, actual, source_kind, source_ref}]}. "
        "verdict is one of: correct, incorrect, misleading, unverifiable."
    )

    def __init__(
        self, ctx: AgentContext, facts_service: FactsService,
    ) -> None:
        super().__init__(ctx, system_prompt=self.SYSTEM_PROMPT)
        self.facts = facts_service

    def respond(self, envelope: JudgeEnvelope) -> FactCheckReply:
        """Annotate a debater turn with fact-check labels."""
        pre_annotations = self._pre_annotate(envelope)
        prompt = self._fc_prompt(envelope, pre_annotations)
        messages = self._build_messages() or [
            {"role": "user", "content": prompt},
        ]
        response = self._call_anthropic(messages=messages)
        payload = self._extract_payload(response)
        return self._validate(payload, envelope.envelope_id)

    def _pre_annotate(self, envelope: JudgeEnvelope) -> list[dict]:
        """Run local + Wikipedia checks before the LLM call."""
        text = _extract_argument_text(envelope)
        claims = self.facts.extract_checkable_claims(text)
        return [self.facts.verify(c).model_dump() for c in claims]

    def _fc_prompt(
        self, envelope: JudgeEnvelope, pre: list[dict],
    ) -> str:
        return (
            f"Fact-check this debater turn. Sender: {envelope.sender}, "
            f"round {envelope.round}.\n"
            f"Content: {envelope.payload!r}\n"
            f"Pre-annotations from local sources: {pre!r}\n"
            f"Merge your own findings with the pre-annotations. "
            f"Return ONLY JSON: {{envelope_ref, claims: [...]}}."
        )

    def _validate(self, payload: dict, envelope_id: str) -> FactCheckReply:
        payload.setdefault("envelope_ref", envelope_id)
        try:
            return FactCheckReply.model_validate(payload)
        except Exception as e:  # noqa: BLE001
            raise SchemaError(f"fact-checker: invalid FactCheckReply: {e}") from e


def _extract_argument_text(envelope: JudgeEnvelope) -> str:
    """Pull argument text from a DebaterReply-shaped payload."""
    return str(envelope.payload.get("argument", ""))
