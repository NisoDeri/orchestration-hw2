# PRD — Agents

**Version**: 1.00 · Covers `BaseAgent` + `DebaterAgent`. Judge has its own PRD (`PRD_judge.md`).

## 1. Goal

A single `BaseAgent` ABC that every agent class extends. The base owns: Anthropic client, gatekeeper integration, Agent-Skill binding, memory view, JSON-reply validation, and event-emit hooks. Subclasses customize only persona, schema, and turn behavior.

## 2. `BaseAgent` contract

```python
class BaseAgent(ABC):
    agent_id: str               # "judge" | "debater-a" | ...
    role: AgentRole             # enum
    skill_id: str               # Anthropic Agent Skill bundle id
    config: AgentConfig         # model, temperature, betas, tools, tool_choice
    memory: ConversationMemory  # per-agent view onto the global transcript
    gatekeeper: Gatekeeper

    @abstractmethod
    def respond(self, envelope: JudgeEnvelope) -> AgentReply: ...

    def _call_anthropic(self, system: str, messages: list[Message]) -> Response:
        """Single chokepoint: every Anthropic call goes through gatekeeper."""

    def _validate_reply(self, raw: dict) -> AgentReply:
        """Pydantic validation. Raises on schema break -> watchdog catches."""
```

**Mixins** (one concern each, per parent rule):
- `JsonReplyMixin` — enforces `tool_use` → final JSON message extraction.
- `CitedReplyMixin` — asserts `citations: [url, …]` non-empty (debaters only).
- `MemoryAwareMixin` — formats `memory.get(self.agent_id)` into the user-message prefix.
- `SkillBoundMixin` — sets `container={"skills": [{"type": "anthropic", "skill_id": self.skill_id, ...}]}`.

## 3. `DebaterAgent`

```python
class DebaterAgent(BaseAgent, JsonReplyMixin, CitedReplyMixin, MemoryAwareMixin, SkillBoundMixin):
    persona: Persona            # loaded from config/personas/<name>.json
    side: Literal["pro", "con"]
    current_era: Era | None     # None for normal rounds, set during era-swap

    def respond(self, envelope: JudgeEnvelope) -> DebaterReply: ...
    def switch_era(self, era: Era | None) -> None: ...
```

**Persona schema** (`config/personas/messi.json`):
```json
{
  "version": "1.00",
  "name": "Messi",
  "system_prompt": "You are arguing that Lionel Messi is the greatest...",
  "style_notes": ["Calm. Cite stats. Reference World Cup 2022.", "..."],
  "eras": [
    { "label": "2009", "system_addendum": "You are the 2009 version..." },
    { "label": "2022", "system_addendum": "You are the post-World-Cup version..." }
  ],
  "color_hex": "#7B1E3B"
}
```

**DebaterReply JSON contract**:
```json
{
  "argument": "string, <= 250 words, addresses opponent's last point",
  "confidence": 0.78,
  "attack_points": ["point 1", "point 2"],
  "defense_points": ["..."],
  "citations": ["https://...", "https://..."],
  "references_opponent": "quote or paraphrase of opponent's claim being addressed"
}
```

`references_opponent` is non-optional (enforces brief §8.3.4 "mutual reference"). Empty string = schema rejection = watchdog retry.

## 4. `CommentatorAgent` / `CrowdAgent` / `FactCheckerAgent`

Thin subclasses — see `PRD_color_crew.md` and `PRD_factchecker.md` for schemas. They share the same `BaseAgent.respond(envelope) → AgentReply` shape; they just emit different payload subtypes.

## 5. Anthropic call shape (per agent)

```python
client.beta.messages.create(
    model=cfg.model,                              # "claude-opus-4-7"
    betas=["skills-2025-10-02", "code-execution-2025-08-25"],
    container={"skills": [{"type": "anthropic", "skill_id": cfg.skill_id, "version": "latest"}]},
    system=[
        {"type": "text", "text": persona.system_prompt, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": rubric_or_role_text, "cache_control": {"type": "ephemeral"}},
    ],
    tools=cfg.tools,                              # [{"type": "web_search_20260209", ...}]
    tool_choice=cfg.tool_choice,                  # debaters: {"type": "any"}
    temperature=cfg.temperature,
    max_tokens=cfg.max_tokens,
    messages=memory_aware_messages,               # latest envelope last
)
```

Every field above is config-driven; nothing hardcoded.

## 6. "Different Skill per agent" mapping (locked)

| Agent | Skill ID | What the skill instructs |
| --- | --- | --- |
| `debater-a` | `rhetorical-aggression` | "Press the attack. Find weak premises. Cite always. Reference opponent's last point verbatim." |
| `debater-b` | `evidence-marshalling` | "Build from sources upward. Anticipate the next attack. Cite always. Reference opponent verbatim." |
| `judge` | `scoring-rubric` | "Score on rhetoric not facts. Aggregate. Refuse ties. Output a Verdict JSON." |
| `commentator` | `color-commentary` | "One sentence, evocative, no scoring claim." |
| `crowd` | `audience-sentiment` | "Emoji + 5-word reaction line." |
| `fact-checker` | `claim-verification` | "Look up the claim. Annotate severity. Do not score." |

Skill bundles live in `src/debate_ai/skills/<id>/SKILL.md` + helpers; modeled on `github.com/anthropics/skills`.

## 7. Failure handling

- **Pydantic validation fails** on reply → watchdog retries with stricter "respond in JSON only" prompt suffix once; second failure → agent restart.
- **`citations` empty** for a debater → schema reject (treated identically to above).
- **Anthropic non-200** → gatekeeper retries per `rate_limits.json`; on exhaustion, watchdog restarts the agent.
- **Hang past `timeout_s`** → watchdog cancels the future and re-instantiates the agent.

## 8. Tests

- `test_base_agent.py` — gatekeeper is always called; schema validation; mixin composition.
- `test_debater_agent.py` — persona loading; era switch; citations enforcement; reference-opponent enforcement.
- `test_skill_binding.py` — each agent's `container.skills` payload matches its config.
- `test_drift_resistance.py` — fed an "I agree completely" opponent reply, the debater still produces a contradicting argument (proving the skill prompt works).
