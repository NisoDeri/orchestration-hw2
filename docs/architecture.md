# Architecture — class diagram and module relationships

**Version**: 1.00 · Mandatory per HW2 brief §8.6 (OOP class diagram requirement).

## 1. Inheritance graph (Mermaid)

```mermaid
classDiagram
    class BaseAgent {
        +str agent_id
        +str skill_id
        +dict[str, Any] tools
        +AgentConfig config
        +ConversationMemory memory
        +respond(envelope: JudgeEnvelope) AgentReply
        +on_event(event: UIEvent) void
        #_call_anthropic(messages, **kw) Response
        #_validate_reply(payload: dict) AgentReply
    }
    class DebaterAgent {
        +Persona persona
        +str side
        +Era|None current_era
        +respond(envelope) DebaterReply
        +switch_era(era: Era) void
    }
    class JudgeAgent {
        +ScoringRubric rubric
        +ScoreAggregate running
        +relay(from_agent, to_agent, payload) JudgeEnvelope
        +score_turn(reply: DebaterReply) TurnScore
        +verdict() Verdict
    }
    class CommentatorAgent {
        +respond(envelope) CommentaryReply
    }
    class CrowdAgent {
        +respond(envelope) CrowdReply
    }
    class FactCheckerAgent {
        +FactsService facts
        +respond(envelope) FactCheckReply
    }

    BaseAgent <|-- DebaterAgent
    BaseAgent <|-- JudgeAgent
    BaseAgent <|-- CommentatorAgent
    BaseAgent <|-- CrowdAgent
    BaseAgent <|-- FactCheckerAgent
```

## 2. Orchestration relationships

```mermaid
classDiagram
    class DebateManager {
        +DebateConfig config
        +DebateState state
        +RoundManager round_mgr
        +Routing routing
        +Watchdog watchdog
        +EventEmitter events
        +start() DebateResult
        +cancel() void
    }
    class RoundManager {
        +int index
        +RoundKind kind
        +run(state, agents) RoundResult
    }
    class Routing {
        +JudgeAgent judge
        +relay(from_agent, payload) JudgeEnvelope
    }
    class Watchdog {
        +float timeout_s
        +int max_restarts
        +supervise(future, agent) Any
        +restart(agent) Agent
    }
    class EraSwap {
        +int round_index
        +pick(persona) Era
    }
    class EventEmitter {
        +list~Subscriber~ subs
        +emit(event: UIEvent) void
        +subscribe(cb) Unsubscribe
    }

    DebateManager o-- RoundManager
    DebateManager o-- Routing
    DebateManager o-- Watchdog
    DebateManager o-- EventEmitter
    DebateManager ..> EraSwap
    RoundManager ..> Routing
    Routing o-- JudgeAgent
```

## 3. Cross-cutting (shared)

```mermaid
classDiagram
    class ConfigLoader {
        +load(name: str) BaseModel
        +validate_versions() void
    }
    class FifoLogger {
        +Path dir
        +int max_files
        +int lines_per_file
        +log(level, **fields) void
        +tail(n) list~str~
    }
    class Gatekeeper {
        +RateLimits limits
        +PriorityQueue queue
        +call(req) Response
        +cost_so_far_usd() float
    }
    class Version {
        +str CODE_VERSION
        +str config_version_required(name) str
    }

    ConfigLoader ..> Version : validates
    Gatekeeper ..> RateLimits
    Gatekeeper ..> FifoLogger : logs every call
```

## 4. Module dependency rules

- **CLI** depends only on **SDK**.
- **UI** (FastAPI server) depends only on **SDK** + **EventEmitter**.
- **SDK** depends on **Orchestration** + **Services** + **Memory** + **Models**.
- **Orchestration** depends on **Agents** + **Models** + **Memory** + **shared/**.
- **Agents** depend on **Tools** + **Memory** + **Models** + **shared/Gatekeeper**.
- **Tools** depend on **Anthropic SDK** + **shared/Gatekeeper**.
- **shared/** depends on nothing project-local except `models/` for typed config schemas.

**Forbidden edges** (will fail CI grep):
- `agents → orchestration` (would create a cycle).
- `cli → agents` (CLI must go through SDK).
- `ui → agents` (same).
- Anything → `cli` (CLI is a sink).

## 5. Where each spec mandate lives

| Brief item | Code location |
| --- | --- |
| Child → father → child (§8.3.7) | `orchestration/routing.py` + `agents/judge_agent.py::relay` |
| JSON message format (§8.3.8) | `models/message_models.py` |
| ≥10 pings (§8.3.3) | `orchestration/debate_manager.py` loop + `config/setup.json` |
| Mutual reference (§8.3.4) | `agents/debater_agent.py` system prompt + judge re-anchor check |
| Mandatory web search (§8.3.5) | `tools/web_search_tool.py` + `tool_choice` enforcement |
| No tie (§8.3.6 + §9) | `models/message_models.py::Verdict` validator + `services/scoring_service.py` retry |
| Different `Skill` per agent (§8.3.2) | `skills/<id>/` + `config/models.json` skill_id mapping |
| OOP + class diagram (§8.6) | this file |
| Watchdog + timeouts (§8.6) | `orchestration/watchdog.py` |
| FIFO log rotation (§8.6) | `shared/logger.py` + `config/logging.json` |
| Gatekeeper (§8.6) | `shared/gatekeeper.py` + `config/rate_limits.json` |
| SDK below all interfaces (§8.6) | `sdk/sdk.py` is the single public class |
| Terminal menu canonical (§8.6) | `cli/menu.py` |
