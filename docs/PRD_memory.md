# PRD — Memory

**Version**: 1.00 · How the transcript is stored, viewed, and fed to each agent.

## 1. Two layers

| Layer | What | Owned by |
| --- | --- | --- |
| **Transcript** | Append-only log of every `JudgeEnvelope` ever emitted in a debate. | `memory/conversation_memory.py::ConversationMemory` |
| **Context view** | What a specific agent sees in its next Anthropic call. Derived from the transcript via `context_builder`. | `memory/context_builder.py::ContextBuilder` |

Agents never read the transcript directly. They always go through the context builder, which encodes the per-agent visibility rules.

## 2. Per-agent visibility rules

| Agent | Sees from transcript |
| --- | --- |
| **Judge** | Everything except its own internal scoring notes. |
| **Debater-A** | Only envelopes with `to == "debater-a"` OR `to == "all" AND from == "judge"`. Crucially: sees `from=debater-b`'s replies *only after* the judge relayed them. |
| **Debater-B** | Mirror of A. |
| **Commentator** | All debater + judge envelopes from the most recent round, plus the running scoreboard. |
| **Crowd** | The most recent debater envelope only. |
| **Fact-Checker** | The most recent debater envelope only (so it can annotate just that claim). |

Visibility is enforced by the builder, not by trust. A test asserts no agent's context ever contains an envelope it shouldn't see.

## 3. ConversationMemory schema

```python
class TranscriptEntry(BaseModel):
    envelope: JudgeEnvelope
    seq: int                  # global ordering within debate
    in_round: int

class ConversationMemory(BaseModel):
    debate_id: str
    motion: str
    entries: list[TranscriptEntry] = []
    scoreboard: ScoreAggregate = ScoreAggregate()

    def append(self, envelope: JudgeEnvelope) -> None: ...
    def view_for(self, agent_id: str) -> list[TranscriptEntry]: ...   # delegates to ContextBuilder
    def latest_for(self, agent_id: str) -> TranscriptEntry | None: ...
```

`append` is the only mutator. `seq` and `in_round` are stamped here.

## 4. ContextBuilder

```python
class ContextBuilder:
    def build(self, agent_id: str, mem: ConversationMemory) -> list[Message]:
        """Translate transcript entries into Anthropic `messages` array.
        Static prefix (cached): role + rubric + previous turns.
        Dynamic suffix: latest envelope.
        """
```

Output structure (debater example):

```
system: [persona.system_prompt + skill prompt]  # cached
messages: [
    {"role": "user", "content": "<- judge relayed the motion: ... ->"},
    {"role": "assistant", "content": "<your previous reply, paraphrased>"},
    {"role": "user", "content": "<- judge relayed opponent's last point: ... ->"},
    ...
    {"role": "user", "content": "<- judge: your turn, round N, kind=rebuttal ->"},  # latest
]
```

The N-1 previous messages are deterministically generated from the transcript so the cache prefix is stable across turns.

## 5. Eviction

A single debate at 10 pings × 2 debaters has ~25 envelopes — well within Claude's context window. **No eviction is implemented in v1.00**, but the abstraction is in place: `ContextBuilder.build` could trim early turns if `tokens > budget`. Documented as a v1.1 hook; not built.

## 6. Persistence

In-memory during a debate. On debate end, `replay_export.py` serializes the full `ConversationMemory` to:

1. `replays/<debate_id>.json` — raw transcript + scoreboard.
2. `replays/<debate_id>.html` — styled, self-contained replay viewer (no server, just open in browser).

No database. Replays are flat files.

## 7. Tests

- `test_memory_append.py` — `seq` monotonic, `in_round` correct.
- `test_visibility_debater.py` — debater-a never sees envelopes addressed to debater-b directly.
- `test_visibility_judge.py` — judge sees everything.
- `test_context_builder_cache_stability.py` — same transcript → byte-identical static prefix across turns (proves prompt cache will hit).
- `test_replay_roundtrip.py` — write replay, read it back, asserts equality.
