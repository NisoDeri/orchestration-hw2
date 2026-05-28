# TODO — debate-ai

**Rule.** Each task = one observable outcome, ~1 commit. Mark `[x]` when done. Phases enforce ordering — finish phase N before starting N+1 except where parallelizable items are explicitly noted.

Total: **532 tasks**.

---

## Phase 0 — Pre-flight (8)

1. [x] Confirm group code with partner Yarden; record in `README.md` §8.
2. [x] Confirm Anthropic API key budget for HW2 (~$5–10 expected).
3. [x] Confirm `web_search` is enabled in Claude Console org settings.
4. [x] Confirm Python 3.10+ on dev machine (`uv python list`).
5. [x] Confirm `uv --version` ≥ 0.4.
6. [x] Confirm `git --version` available.
7. [x] Decide README language (English / Hebrew); record decision in `prompts.md`.
8. [x] Get user approval on all docs before scaffolding.

---

## Phase 1 — Scaffolding (44)

9. [x] `git init -b main` in `hw2/`.
10. [x] Create `.gitignore` with `.env`, `__pycache__/`, `.venv/`, `*.egg-info`, `logs/*.jsonl`, `replays/*`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`.
11. [x] Create `.env-example` with `ANTHROPIC_API_KEY=your_key_here` placeholder.
12. [x] Add `LICENSE` (MIT).
13. [x] Create `pyproject.toml` skeleton — name, version, description, authors.
14. [x] Add dependencies in `pyproject.toml`: `anthropic`, `pydantic`, `typer`, `rich`, `fastapi`, `uvicorn`, `httpx`.
15. [x] Add dev dependencies: `pytest`, `pytest-cov`, `pytest-asyncio`, `hypothesis`, `ruff`, `vcrpy`.
16. [x] Configure `[tool.ruff]` in `pyproject.toml`: line-length 100, target py310, select `E,F,W,I,N,UP,B,C4,SIM`, extend-ignore `E501`.
17. [x] Configure `[tool.coverage.run]`: source `["src/debate_ai"]`.
18. [x] Configure `[tool.coverage.report]`: `fail_under = 85`, `exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]`.
19. [x] Configure `[project.scripts]`: `debate-ai = "debate_ai.cli.main:app"`.
20. [x] Run `uv sync` — succeeds, `.venv/` created.
21. [x] Create `src/debate_ai/__init__.py` with `__version__ = "1.00"` and `__all__ = ["DebateAI"]`.
22. [x] Create `src/debate_ai/constants.py` empty placeholder.
23. [x] Create empty subpackages: `sdk/`, `cli/`, `agents/`, `orchestration/`, `memory/`, `models/`, `services/`, `tools/`, `ui/`, `shared/`, `utils/`, `skills/` — each with empty `__init__.py`.
24. [x] Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`.
25. [x] Add `tests/conftest.py` with `mock_anthropic_client` fixture stub.
26. [x] Create `config/` directory.
27. [x] Create `config/setup.json` skeleton with `version: "1.00"`.
28. [x] Create `config/debate.json` with default motion (Messi vs Ronaldo) and persona pair.
29. [x] Create `config/models.json` with per-agent role config (model, skill_id, temperature, betas, tools, tool_choice).
30. [x] Create `config/rate_limits.json` with `max_cost_usd_per_debate: 2.00`, queue depth, retry policy.
31. [x] Create `config/logging.json` per `PRD_logging.md` §3 example.
32. [x] Create `config/facts.json` skeleton with `lookup_order` + a few Messi/Ronaldo claims.
33. [x] Create `config/versions.json` declaring required versions for each config file.
34. [x] Create `config/personas/` and add `messi.json` per `PRD_agents.md` §3 schema.
35. [x] Add `config/personas/ronaldo.json`.
36. [x] Add `config/personas/python.json` (alt demo — argues Python is the better first language).
37. [x] Add `config/personas/javascript.json`.
38. [x] Each persona file gets `eras` array with ≥ 2 era variants.
39. [x] Create `replays/` directory with a `.gitkeep`.
40. [x] Create `logs/` directory with a `.gitkeep`.
41. [x] Add `prompts.md` skeleton (Prompt Engineering Log header + initial entry).
42. [x] First commit: `chore: initial scaffolding`.
43. [x] Push to GitHub (private at first; flip to public before submission).
44. [x] Invite `rmisegal@gmail.com` as collaborator.
45. [x] CI: add `.github/workflows/ci.yml` running `uv sync && uv run ruff check && uv run pytest --cov`.
46. [x] Run `uv run ruff check` — clean.
47. [x] Run `uv run pytest` — collects zero tests, exits 0.
48. [x] Commit: `chore: add CI workflow`.
49. [x] Verify CI green on a push.
50. [x] Tag the green CI commit `v0.1.0`.
51. [x] Update README §3 with the exact commands above.
52. [x] Commit: `docs: update README quickstart to match scaffolding`.

---

## Phase 2 — Shared (config / version / logger / gatekeeper) (62)

53. [x] `shared/version.py`: `CODE_VERSION = "1.00"` + helper to assert config versions.
54. [x] Test `test_version.py::test_code_version_format`.
55. [x] `shared/config.py`: `ConfigLoader` class skeleton.
56. [x] `ConfigLoader.load(name)` loads `config/<name>.json` and parses to Pydantic model.
57. [x] `ConfigLoader.validate_versions()` cross-checks `versions.json` against each loaded config.
58. [x] Pydantic models: `SetupConfig`, `DebateConfig`, `ModelsConfig`, `RateLimitsConfig`, `LoggingConfig`, `FactsConfig`, `VersionsConfig`.
59. [x] Each config Pydantic model has a `version: str` field validated against `versions.json`.
60. [x] `test_config_loader.py::test_load_valid` — each fixture config loads.
61. [x] `test_config_loader.py::test_version_mismatch_raises` — bad version in versions.json → ConfigError.
62. [x] `test_config_loader.py::test_missing_file_raises` — missing config → ConfigError with file path.
63. [x] Commit: `feat(shared): config loader with version validation`.
64. [x] `shared/logger.py`: `FifoLogger` class skeleton.
65. [x] `FifoLogger.__init__` reads `config/logging.json`, creates `dir` if absent.
66. [x] `FifoLogger.log(level, **fields)` writes a JSON line with timestamp.
67. [x] `FifoLogger` rotates to next file at `lines_per_file`.
68. [x] `FifoLogger` evicts oldest file past `max_files`.
69. [x] `FifoLogger.tail(n)` returns last n lines across files.
70. [x] `FifoLogger.tail_live()` generator yields new lines.
71. [x] `.cursor` persistence file for resume-after-restart.
72. [x] `test_logger_rotation.py`.
73. [x] `test_logger_fifo_eviction.py`.
74. [x] `test_logger_schema.py` — every line parses as JSON, has required keys.
75. [x] `test_logger_cursor_persistence.py`.
76. [x] `test_logger_tail.py`.
77. [x] Commit: `feat(shared): FIFO logger`.
78. [x] `shared/gatekeeper.py`: `Gatekeeper` class skeleton.
79. [x] `Gatekeeper.__init__` reads `rate_limits.json`, builds `PriorityQueue`.
80. [x] `Gatekeeper.call(req)` enqueues and returns response.
81. [x] Rate-limit enforcement via token bucket per provider.
82. [x] Retry policy with exponential backoff per `retry_policy` config.
83. [x] `Gatekeeper.cost_so_far_usd()` accumulates from Anthropic usage headers + $0.01/search.
84. [x] Backpressure: when queue full, `call` blocks up to `max_block_s`.
85. [x] Log every call: started → finished with token usage.
86. [x] Cost-cap detection: `cost_so_far_usd() >= max_cost_usd_per_debate` → raise `CostCapExceeded`.
87. [x] `test_gatekeeper_rate_limit.py` — 11th call in 1s blocks (limit=10/s).
88. [x] `test_gatekeeper_retry.py` — first call 500s, second 200s → returns successfully.
89. [x] `test_gatekeeper_cost_tracking.py` — fake usage headers accumulate correctly.
90. [x] `test_gatekeeper_cost_cap.py` — over-cap raises `CostCapExceeded`.
91. [x] `test_gatekeeper_backpressure.py` — queue full, call blocks.
92. [x] `test_gatekeeper_logs_every_call.py` — `FifoLogger` receives both started + finished records.
93. [x] Commit: `feat(shared): gatekeeper with rate-limit, retry, cost tracking`.
94. [x] `shared/seeding.py`: deterministic RNG seeding for era pick + crowd lean during tests.
95. [x] `test_seeding.py::test_seeded_choices_reproducible`.
96. [x] Commit: `feat(shared): RNG seeding utility`.
97. [x] `shared/exceptions.py`: declare `ConfigError`, `AgentUnrecoverable`, `CostCapExceeded`, `RouteError`, `SchemaError`.
98. [x] `test_exceptions_inheritance.py`.
99. [x] Commit: `feat(shared): exception hierarchy`.
100. [x] `utils/formatting.py`: `format_envelope(env)` for log + UI text.
101. [x] `utils/validators.py`: `is_valid_url(s)`, `is_non_empty_list(x)`.
102. [x] `test_formatting.py` + `test_validators.py`.
103. [x] Commit: `feat(utils): formatting + validators`.
104. [x] `constants.py`: enum `AgentRole`, `RoundKind`, `EnvelopeKind`, `LogLevel`.
105. [x] `test_constants.py::test_enum_values`.
106. [x] Commit: `feat: enums in constants.py`.
107. [x] Run `ruff check` and `pytest --cov`. Coverage on shared/ ≥ 90 %.
108. [x] Tag `v0.2.0`.
109. [x] Commit: `chore: tag v0.2.0 — shared layer green`.
110. [x] Update README §6 with the actual `shared/` modules in place.
111. [x] Commit: `docs: README sync to v0.2.0`.
112. [x] Push.
113. [x] CI green.
114. [x] Verify `uv run debate-ai --help` runs (even with no real commands yet).

---

## Phase 3 — Models + Memory (54)

115. [x] `models/debate_models.py`: `Persona` Pydantic model from `PRD_agents.md` §3 schema.
116. [x] `models/debate_models.py`: `Era` model with `label`, `system_addendum`.
117. [x] `models/debate_models.py`: `RoundKind` enum re-export from constants.
118. [x] `models/debate_models.py`: `DebateConfig` model.
119. [x] `models/debate_models.py`: `DebateState` model with `history`, `scoreboard`, `current_round`.
120. [x] `models/debate_models.py`: `Round` model.
121. [x] `models/debate_models.py`: `ScoreAggregate` model — running totals per debater.
122. [x] `models/debate_models.py`: `TurnScore` model — 4 dimensions × float.
123. [x] `models/message_models.py`: `JudgeEnvelope` model per `PRD_judge.md` §3.
124. [x] `models/message_models.py`: `DebaterReply` model per `PRD_agents.md` §3.
125. [x] `DebaterReply.citations` non-empty validator.
126. [x] `DebaterReply.references_opponent` non-empty validator (allow empty only on round 1 opening).
127. [x] `models/message_models.py`: `Verdict` model.
128. [x] `Verdict.score_a != Verdict.score_b` validator (no-tie).
129. [x] `models/message_models.py`: `CommentaryReply` model.
130. [x] `models/message_models.py`: `CrowdReply` model.
131. [x] `models/message_models.py`: `FactCheckReply` model with nested `Claim` list.
132. [x] `models/message_models.py`: `UIEvent` discriminated union per `PRD_ui.md` §1.
133. [x] `AgentReply = Union[DebaterReply, CommentaryReply, ...]`.
134. [x] Each model has `__init_subclass__` ensuring no extra fields (`model_config.extra = "forbid"`).
135. [x] `test_persona_load.py` — load each shipped persona JSON, validate.
136. [x] `test_envelope_round_trip.py` — model → JSON → model identical.
137. [x] `test_verdict_no_tie.py` — `Verdict(score_a=70, score_b=70)` raises.
138. [x] `test_debater_reply_citations_required.py`.
139. [x] `test_debater_reply_references_opponent_required.py`.
140. [x] `test_ui_event_discriminator.py` — `kind` field correctly routes payload.
141. [x] Commit: `feat(models): Pydantic message + state models`.
142. [x] `memory/conversation_memory.py`: `TranscriptEntry` model.
143. [x] `memory/conversation_memory.py`: `ConversationMemory` class skeleton.
144. [x] `ConversationMemory.append(envelope)` stamps `seq` + `in_round`.
145. [x] `ConversationMemory.latest_for(agent_id)` returns most recent entry the agent should see.
146. [x] `ConversationMemory.view_for(agent_id)` delegates to `ContextBuilder`.
147. [x] `test_memory_append_seq_monotonic.py`.
148. [x] `test_memory_in_round_correct.py`.
149. [x] `memory/context_builder.py`: `ContextBuilder` class skeleton.
150. [x] `ContextBuilder.build(agent_id, mem)` implements visibility rules from `PRD_memory.md` §2.
151. [x] Per-agent visibility: Judge sees all.
152. [x] Per-agent visibility: Debater sees only own-addressed + judge-broadcast.
153. [x] Per-agent visibility: Commentator sees last round.
154. [x] Per-agent visibility: Crowd sees latest debater envelope only.
155. [x] Per-agent visibility: Fact-Checker sees latest debater envelope only.
156. [x] Static prefix is byte-identical across turns when transcript prefix unchanged (cache stability).
157. [x] `test_visibility_judge_sees_all.py`.
158. [x] `test_visibility_debater_isolation.py`.
159. [x] `test_visibility_commentator_one_round.py`.
160. [x] `test_visibility_crowd_latest_only.py`.
161. [x] `test_visibility_factchecker_latest_only.py`.
162. [x] `test_context_builder_cache_stability.py`.
163. [x] Commit: `feat(memory): transcript + per-agent context builder`.
164. [x] Coverage on `models/` + `memory/` ≥ 90 %.
165. [x] Run `ruff check`.
166. [x] Tag `v0.3.0`.
167. [x] Commit: `chore: tag v0.3.0 — models + memory green`.
168. [x] Update README §6.

---

## Phase 4 — Tools layer (web_search, web_fetch, citation, Wikipedia MCP) (42)

169. [x] `tools/web_search_tool.py`: `Citation` model (`url`, `title`, `snippet`).
170. [x] `tools/web_search_tool.py`: `SearchProvider` ABC.
171. [x] `tools/web_search_tool.py`: `AnthropicBuiltinSearch` provider returning `tool_choice + tools` config snippet (passed to agent's Anthropic call).
172. [x] `tools/web_search_tool.py`: `TavilySearch` provider fallback.
173. [x] `tools/web_search_tool.py`: `ExaSearch` provider fallback.
174. [x] `tools/web_search_tool.py`: `OmniSearch` provider fallback.
175. [x] `tools/web_search_tool.py`: `search(query, provider=...)` dispatch on config.
176. [x] `tools/citation_tool.py`: `Citation.from_anthropic_block(block)` parser.
177. [x] `tools/citation_tool.py`: `Citation.fetch_text(url)` via Anthropic `web_fetch` server tool.
178. [x] `tools/wikipedia_mcp.py`: stdio-based MCP client wrapper.
179. [x] `tools/wikipedia_mcp.py`: `WikipediaMCP.summary(title)`, `.search(query)`.
180. [x] Wikipedia MCP launches `uvx wikipedia-mcp` as subprocess.
181. [x] `test_search_dispatch.py` — config provider change swaps implementation.
182. [x] `test_anthropic_builtin_search.py` — emits correct tool config block.
183. [x] `test_tavily_search.py` — mocked HTTP, hits correct endpoint with API key.
184. [x] `test_exa_search.py` — mocked HTTP.
185. [x] `test_citation_from_anthropic_block.py` — parses `web_search_tool_result` block.
186. [x] `test_citation_fetch_text.py` — fetches a URL via `web_fetch`.
187. [x] `test_wikipedia_mcp_summary.py` — subprocess launches, summary returns.
188. [x] `test_wikipedia_mcp_search.py`.
189. [x] Commit: `feat(tools): search + citation + wikipedia mcp`.
190. [x] Coverage on `tools/` ≥ 90 %.
191. [x] Tag `v0.4.0`.
192. [x] Commit: `chore: tag v0.4.0 — tools green`.
193. [x] `services/facts_service.py`: `FactsService` class.
194. [x] `FactsService.extract_checkable_claims(text)` heuristic split.
195. [x] `FactsService.verify(claim)` walks `lookup_order` from `facts.json`.
196. [x] `FactsService.verify` returns `Verdict("correct"|"incorrect"|"misleading"|"unverifiable")` with severity.
197. [x] `test_facts_service_local_hit.py` — `facts.json` resolves first.
198. [x] `test_facts_service_wikipedia_fallback.py`.
199. [x] `test_facts_service_web_search_last_resort.py`.
200. [x] `test_facts_service_unverifiable.py`.
201. [x] Commit: `feat(services): facts service for fact-checker`.
202. [x] `services/scoring_service.py`: `ScoringService` class.
203. [x] `ScoringService.score_turn(reply)` returns `TurnScore`.
204. [x] `ScoringService.aggregate(turn_scores)` returns `ScoreAggregate`.
205. [x] `ScoringService.detect_drift(history)` returns `bool` per `PRD_judge.md` §7.
206. [x] `ScoringService.lie_catch_bonus(reply, opponent_history)` returns +1 floor on persuasion.
207. [x] `test_score_turn.py`.
208. [x] `test_aggregate.py`.
209. [x] `test_detect_drift.py`.
210. [x] `test_lie_catch_bonus.py`.

---

## Phase 5 — Agents (86)

211. [x] `agents/base_agent.py`: `BaseAgent` ABC per `PRD_agents.md` §2.
212. [x] `BaseAgent.__init__` validates `skill_id` bundle exists on disk.
213. [x] `BaseAgent._call_anthropic` chokepoint routes via `Gatekeeper`.
214. [x] `BaseAgent._validate_reply` raises `SchemaError` on bad payload.
215. [x] `BaseAgent.alive()` heartbeat for watchdog.
216. [x] `agents/mixins.py`: `JsonReplyMixin` extracts JSON from `tool_use` blocks.
217. [x] `agents/mixins.py`: `CitedReplyMixin` asserts non-empty citations.
218. [x] `agents/mixins.py`: `MemoryAwareMixin` formats per-agent context.
219. [x] `agents/mixins.py`: `SkillBoundMixin` injects `container.skills`.
220. [x] `test_base_agent_gatekeeper_called.py`.
221. [x] `test_base_agent_schema_validation.py`.
222. [x] `test_mixin_json_extraction.py`.
223. [x] `test_mixin_cited_required.py`.
224. [x] `test_mixin_memory_aware_visibility.py`.
225. [x] `test_mixin_skill_bound_payload.py`.
226. [x] Commit: `feat(agents): BaseAgent + mixins`.
227. [x] `agents/debater_agent.py`: `DebaterAgent` per `PRD_agents.md` §3.
228. [x] `DebaterAgent.__init__` loads `persona` from `config/personas/<name>.json`.
229. [x] `DebaterAgent.respond(envelope)` returns `DebaterReply`.
230. [x] `DebaterAgent.switch_era(era)` swaps `current_era`.
231. [x] System prompt assembly: persona base + era addendum (if set) + skill instructions.
232. [x] Tool config: `web_search_20260209` always, `tool_choice: {"type": "any"}`.
233. [x] `test_debater_persona_load.py`.
234. [x] `test_debater_respond_returns_reply.py` (mocked Anthropic).
235. [x] `test_debater_era_switch.py`.
236. [x] `test_debater_system_prompt_era_addendum.py`.
237. [x] `test_debater_drift_resistance.py` — given an agreeing opponent, still contradicts.
238. [x] `test_debater_citations_present.py`.
239. [x] `test_debater_references_opponent_present.py`.
240. [x] Commit: `feat(agents): DebaterAgent`.
241. [x] `agents/judge_agent.py`: `JudgeAgent` per `PRD_judge.md`.
242. [x] `JudgeAgent.__init__` loads `scoring-rubric` skill + `ScoringService`.
243. [x] `JudgeAgent.relay(from, to, payload)` returns `JudgeEnvelope`.
244. [x] `JudgeAgent.score_turn(reply)` delegates to `ScoringService`.
245. [x] `JudgeAgent.verdict(running)` calls Anthropic to write verdict prose, validates no-tie.
246. [x] `JudgeAgent` system prompt OMITS the motion text.
247. [x] `cache_control: ephemeral` on system prompt + transcript prefix.
248. [x] `JudgeAgent.detect_drift` calls `ScoringService.detect_drift`, emits re-anchor ruling.
249. [x] `test_judge_relay_routing.py`.
250. [x] `test_judge_score_turn.py`.
251. [x] `test_judge_verdict_no_tie_retry.py`.
252. [x] `test_judge_verdict_no_tie_fallback.py` (aggregate winner).
253. [x] `test_judge_topic_ignorance.py`.
254. [x] `test_judge_prompt_cache_stability.py`.
255. [x] `test_judge_drift_detected.py`.
256. [x] Commit: `feat(agents): JudgeAgent`.
257. [x] `agents/commentator_agent.py`: `CommentatorAgent`.
258. [x] `CommentatorAgent.respond` per `PRD_color_crew.md` §1.
259. [x] `max_tokens=80`.
260. [x] `test_commentator_one_sentence.py`.
261. [x] `test_commentator_no_winner_claim.py`.
262. [x] Commit: `feat(agents): CommentatorAgent`.
263. [x] `agents/crowd_agent.py`: `CrowdAgent`.
264. [x] `CrowdAgent.respond` per `PRD_color_crew.md` §2.
265. [x] `CrowdAgent` context is *latest debater envelope only* (no scoreboard).
266. [x] `CrowdReply.emojis` 1–5.
267. [x] `CrowdReply.one_liner` ≤ 8 words.
268. [x] `test_crowd_respond.py`.
269. [x] `test_crowd_emoji_count.py`.
270. [x] `test_crowd_oneliner_length.py`.
271. [x] `test_crowd_no_scoreboard_leak.py`.
272. [x] Commit: `feat(agents): CrowdAgent`.
273. [x] `agents/factchecker_agent.py`: `FactCheckerAgent`.
274. [x] `FactCheckerAgent.respond` per `PRD_factchecker.md` §6.
275. [x] Delegates claim extraction + verification to `FactsService`.
276. [x] Multi-claim per turn supported.
277. [x] `test_factchecker_respond.py`.
278. [x] `test_factchecker_multi_claim.py`.
279. [x] `test_factchecker_does_not_score.py` — `score_turn` byte-identical with/without FC events.
280. [x] `test_factchecker_priority.py`.
281. [x] `test_factchecker_severity_classification.py`.
282. [x] Commit: `feat(agents): FactCheckerAgent`.
283. [x] Agent factory: `agents/factory.py::build_agent(role, config) → BaseAgent`.
284. [x] Factory uses `config/models.json` to bind each role to model/skill/tools/temperature.
285. [x] `test_agent_factory.py`.
286. [x] Commit: `feat(agents): agent factory`.
287. [x] Coverage on `agents/` ≥ 90 %.
288. [x] Tag `v0.5.0`.
289. [x] Commit: `chore: tag v0.5.0 — agents green`.
290. [x] Push, CI green.
291. [x] Update README §6 with the agent module list.
292. [x] Commit: `docs: README sync to v0.5.0`.
293. [x] Append a `prompts.md` entry: "Prompt for `rhetorical-aggression` skill — first iteration".
294. [x] Append a `prompts.md` entry per skill (6 total).
295. [x] Append a `prompts.md` entry: "Judge no-tie retry phrasing".
296. [x] Verify no agent module references another agent module (forbidden by class diagram).

---

## Phase 6 — Skills bundles (32)

297. [x] `src/debate_ai/skills/rhetorical-aggression/SKILL.md` — instruction set.
298. [x] `skills/rhetorical-aggression/scripts/.gitkeep`.
299. [x] `skills/rhetorical-aggression/resources/.gitkeep`.
300. [x] `skills/evidence-marshalling/SKILL.md`.
301. [x] `skills/evidence-marshalling/scripts/.gitkeep`.
302. [x] `skills/scoring-rubric/SKILL.md` — judge rubric + no-tie + relay protocol.
303. [x] `skills/scoring-rubric/scripts/.gitkeep`.
304. [x] `skills/color-commentary/SKILL.md`.
305. [x] `skills/audience-sentiment/SKILL.md`.
306. [x] `skills/claim-verification/SKILL.md` — facts.json → wikipedia → web_search priority.
307. [x] Upload each of the 6 skills via `/v1/skills` API → record returned IDs.
308. [x] Pin skill IDs in `config/models.json`.
309. [x] `tools/skill_upload.py` helper script to re-upload skills (`uv run debate-ai skills upload`).
310. [x] `test_skill_bundles_on_disk.py` — each of 6 has SKILL.md.
311. [x] `test_skill_upload_script.py` — mocks `/v1/skills` endpoint.
312. [x] `test_skill_id_in_models_config.py`.
313. [x] Each `SKILL.md` ≤ 200 lines.
314. [x] Each `SKILL.md` references the JSON schema the agent must obey.
315. [x] Commit per skill: `feat(skills): <skill-id> bundle`.
316. [x] Commit: `feat(tools): skill upload helper script`.
317. [x] Iterate: run a dry-run debate with mocked Anthropic; verify each skill's instructions visible in the request payload.
318. [x] Iterate: tweak `rhetorical-aggression` skill if debater is too polite.
319. [x] Iterate: tweak `evidence-marshalling` if debater forgets citations.
320. [x] Iterate: tweak `scoring-rubric` if judge ties too often.
321. [x] Iterate: tweak `color-commentary` if commentator declares winners.
322. [x] Iterate: tweak `audience-sentiment` if crowd parrots judge.
323. [x] Iterate: tweak `claim-verification` if FC over-flags.
324. [x] Commit each iteration as `chore(skills): tune <skill>`.
325. [x] Append `prompts.md` per significant skill change.
326. [x] Tag `v0.6.0` once skills produce a clean dry-run.
327. [x] Commit: `chore: tag v0.6.0 — skills green`.
328. [x] Push.

---

## Phase 7 — Orchestration (56)

329. [x] `orchestration/routing.py`: `Routing` class.
330. [x] `Routing.__init__(judge)` stores judge ref.
331. [x] `Routing.relay(from_agent, payload)` → `JudgeEnvelope` to opposite debater.
332. [x] Routing asserts no debater-to-debater edge.
333. [x] `test_routing_swap.py` — A → relay → goes to B.
334. [x] `test_routing_no_direct_edge.py`.
335. [x] Commit: `feat(orchestration): routing`.
336. [x] `orchestration/round_manager.py`: `RoundManager` class.
337. [x] `RoundManager.run(state, agents)` executes one round.
338. [x] Round kinds: `opening`, `rebuttal`, `era_swap`, `closing`.
339. [x] Speaking order: A → judge relay → B → judge relay → ... × pings_per_side.
340. [x] Score each relayed reply via `ScoringService`.
341. [x] Emit `UIEvent(round_changed, agent_message, score_update)` per step.
342. [x] `test_round_opening.py`.
343. [x] `test_round_rebuttal_pings.py`.
344. [x] `test_round_emits_events_in_order.py`.
345. [x] Commit: `feat(orchestration): round manager`.
346. [x] `orchestration/era_swap.py`: `EraSwap` class.
347. [x] `EraSwap.pick(persona, strategy)` returns `Era`.
348. [x] Strategies: `random`, `first`, `latest`, `contrasting`.
349. [x] `test_era_pick_random.py` (seeded).
350. [x] `test_era_pick_contrasting.py` — furthest apart by year parse.
351. [x] `test_era_pick_no_eras_returns_none.py`.
352. [x] Commit: `feat(orchestration): era swap pick`.
353. [x] `orchestration/watchdog.py`: `Watchdog` class per `PRD_watchdog.md`.
354. [x] `Watchdog.supervise(fn, args, timeout, on_hang)` uses ThreadPoolExecutor.
355. [x] Per-agent restart counter, capped at `max_restarts`.
356. [x] Schema-break retry with stricter prompt.
357. [x] Citation-missing retry.
358. [x] `AgentUnrecoverable` raised on exhaust.
359. [x] Keep-alive ticks every `keepalive_interval_s`, no API calls.
360. [x] `test_watchdog_timeout_restarts.py`.
361. [x] `test_watchdog_max_restarts_exhausted.py`.
362. [x] `test_watchdog_schema_break_retry.py`.
363. [x] `test_watchdog_citation_retry.py`.
364. [x] `test_watchdog_keepalive_no_api_calls.py`.
365. [x] Commit: `feat(orchestration): watchdog + keepalive`.
366. [x] `orchestration/event_emitter.py`: `EventEmitter` per `PRD_ui.md` §1.
367. [x] `EventEmitter.emit(event)`, `.subscribe(cb) → Unsubscribe`, `.replay(from_seq)`.
368. [x] Thread-safe with `RLock`.
369. [x] `test_event_emitter_emit_subscribe.py`.
370. [x] `test_event_emitter_replay_from_seq.py`.
371. [x] `test_event_emitter_thread_safety.py`.
372. [x] Commit: `feat(orchestration): event emitter`.
373. [x] `orchestration/debate_manager.py`: `DebateManager` class.
374. [x] `DebateManager.start()` runs the full lifecycle.
375. [x] Sequence: opening → N rebuttals (with era_swap round) → closing → verdict.
376. [x] On `CostCapExceeded` → force verdict from aggregate.
377. [x] On `AgentUnrecoverable` → force verdict.
378. [x] On clean end → emit `debate_ended` UIEvent.
379. [x] `test_debate_full_run_mocked.py`.
380. [x] `test_debate_cost_cap_forces_verdict.py`.
381. [x] `test_debate_unrecoverable_forces_verdict.py`.
382. [x] `test_debate_event_order.py`.
383. [x] `test_debate_no_tie_invariant.py` — 100 mocked debates, zero ties.
384. [x] Commit: `feat(orchestration): debate manager`.

---

## Phase 8 — Services (12)

385. [x] `services/debate_service.py`: `DebateService` wires `DebateManager` + `EventEmitter` + persisting.
386. [x] `DebateService.run(motion, persona_a, persona_b, ...)` → `DebateResult`.
387. [x] `DebateService.list_personas()` walks `config/personas/`.
388. [x] `DebateService.list_motions()` returns the default + any user-added.
389. [x] `DebateService.replay(debate_id)` loads from `replays/`.
390. [x] `DebateService.export_replay(debate_id, path)` renders self-contained HTML.
391. [x] `test_debate_service_run.py`.
392. [x] `test_debate_service_list_personas.py`.
393. [x] `test_debate_service_replay_roundtrip.py`.
394. [x] `test_debate_service_export_selfcontained.py`.
395. [x] Commit: `feat(services): debate service`.
396. [x] Tag `v0.7.0`.

---

## Phase 9 — SDK (12)

397. [x] `sdk/sdk.py`: `DebateAI` class per `PLAN.md` §3.
398. [x] `DebateAI.__init__(config_dir)` loads all configs via `ConfigLoader`.
399. [x] `DebateAI.run_debate(...)` calls `DebateService.run`, optionally with event callback.
400. [x] `DebateAI.list_personas()`, `.list_motions()`, `.replay()`, `.export_replay()` pass-throughs.
401. [x] SDK is the only module exported from `__init__.py::__all__`.
402. [x] `test_sdk_smoke.py` — instantiate + run mocked debate end-to-end.
403. [x] `test_sdk_run_with_callback.py`.
404. [x] `test_sdk_replay.py`.
405. [x] `test_sdk_export.py`.
406. [x] Commit: `feat(sdk): single public entry point`.
407. [x] Tag `v0.8.0`.
408. [x] Update README quickstart with real SDK usage example.

---

## Phase 10 — CLI menu (28)

409. [x] `cli/main.py`: Typer app with `app = typer.Typer()`.
410. [x] `cli/main.py`: `main()` default → calls `menu.run_loop(sdk)`.
411. [x] `cli/main.py`: `run` subcommand for one-shot debate.
412. [x] `cli/main.py`: `start` subcommand launches FastAPI + opens browser.
413. [x] `cli/main.py`: `skills upload` subcommand (re-uploads skill bundles).
414. [x] `cli/menu.py`: `run_loop(sdk)` per `PRD_ui.md` §2 layout.
415. [x] Item [1] Run debate — calls `sdk.run_debate()`.
416. [x] Item [2] Choose motion — text input, persists in-memory.
417. [x] Item [3] Choose personas — list from `sdk.list_personas()`, two prompts.
418. [x] Item [4] Run + watch live — registers `on_event` callback that prints Rich panels.
419. [x] Item [5] Show last verdict — pretty-prints last `Verdict`.
420. [x] Item [6] Browse replays — `os.listdir("replays/")`, pick one, opens HTML in browser.
421. [x] Item [7] Tail logs — calls `FifoLogger.tail(100)` and renders.
422. [x] Item [7b] Tail logs (live) — streams.
423. [x] Item [8] Show config / version — prints `__version__` + loaded configs' versions.
424. [x] Item [0] Quit.
425. [x] All menu items thin wrappers — no business logic.
426. [x] Live watch renders chat bubbles with Rich panels.
427. [x] `test_cli_help.py` — `--help` lists subcommands.
428. [x] `test_cli_run_subcommand.py`.
429. [x] `test_menu_loop_key_dispatch.py`.
430. [x] `test_menu_no_business_logic.py` — AST-grep agent imports inside cli/.
431. [x] `test_menu_choose_personas.py`.
432. [x] `test_menu_browse_replays.py`.
433. [x] `test_menu_tail_logs.py`.
434. [x] Commit: `feat(cli): typer app + keyboard menu`.
435. [x] Tag `v0.9.0`.
436. [x] Update README with menu screenshot placeholder.

---

## Phase 11 — UI (FastAPI + SSE + HTML) (44)

437. [x] `ui/events.py`: shared event emitter facade (delegates to `orchestration/event_emitter.py`).
438. [x] `ui/server.py`: FastAPI app skeleton.
439. [x] Route `GET /` returns `static/index.html`.
440. [x] Route `GET /static/{path}` serves css/js.
441. [x] Route `POST /start` accepts `{motion, persona_a, persona_b, pings}`, returns `{debate_id}`.
442. [x] Route `GET /stream?debate_id=&from_seq=` returns `text/event-stream` SSE.
443. [x] SSE replays missed events from `from_seq` before subscribing live.
444. [x] Route `GET /verdict/{debate_id}` returns the verdict (404 if not yet emitted).
445. [x] Route `GET /replay/{debate_id}` returns self-contained HTML as `application/octet-stream`.
446. [x] `ui/replay_export.py`: renders `replays/<id>.html` from a `ConversationMemory`.
447. [x] Replay HTML inlines CSS + JS + the event log as JSON.
448. [x] Replay player has play/pause/scrub/speed controls.
449. [x] `static/index.html`: semantic structure (header, main grid, footer).
450. [x] `static/styles.css`: Telegram-style bubbles, agent-colored from `persona.color_hex`.
451. [x] `static/styles.css`: responsive grid 70/30 desktop, stacked mobile.
452. [x] `static/app.js`: `EventSource('/stream?debate_id=...')` wiring.
453. [x] `static/app.js`: typing indicator on `agent_started_typing`.
454. [x] `static/app.js`: bubble append on `agent_message`.
455. [x] `static/app.js`: scoreboard update on `score_update`.
456. [x] `static/app.js`: confidence meter animation.
457. [x] `static/app.js`: round badge on `round_changed`.
458. [x] `static/app.js`: fact-check chip under bubble (severity color).
459. [x] `static/app.js`: commentator + crowd inline blocks.
460. [x] `static/app.js`: verdict modal on `verdict`.
461. [x] `static/app.js`: replay-mode toggle (rate slider).
462. [x] Browser auto-open via `webbrowser.open` in `cli main.py::start`.
463. [x] `--no-browser` flag for CI.
464. [x] `test_ui_server_index.py`.
465. [x] `test_ui_sse_stream_events.py`.
466. [x] `test_ui_sse_replay_from_seq.py`.
467. [x] `test_ui_post_start.py`.
468. [x] `test_ui_get_verdict_404_until_ready.py`.
469. [x] `test_ui_replay_html_selfcontained.py` — open in headless Chromium without network.
470. [x] `test_ui_static_files_present.py`.
471. [x] `test_static_html_validates.py` — passes `html5validator` linter.
472. [x] `test_static_css_no_unused_classes.py`.
473. [x] Visual smoke test: spawn server, run a debate, capture screenshot to `docs/screenshots/menu.png` and `docs/screenshots/chat.png`.
474. [x] Commit: `feat(ui): FastAPI + SSE + HTML chat`.
475. [x] Tag `v0.10.0`.
476. [x] Update README §7 with real screenshots.
477. [x] Commit: `docs: README screenshots`.
478. [x] Push.
479. [x] CI green.
480. [x] Manual end-to-end smoke: `uv run debate-ai start` → browser tab → full debate visible.

---

## Phase 12 — Tests + polish + release (52)

481. [x] `test_integration_full_debate_mocked.py` — 10 pings, era-swap, verdict, no tie.
482. [x] `test_integration_drift_intervention.py`.
483. [x] `test_integration_watchdog_recovery.py`.
484. [x] `test_integration_cost_cap_clean_end.py`.
485. [x] `test_integration_replay_roundtrip.py`.
486. [x] `test_integration_two_persona_pairs.py` — Messi/Ronaldo AND Python/JS produce coherent debates with zero code change.
487. [x] `test_property_routing_preserves_identity.py` (hypothesis).
488. [x] `test_property_aggregate_monotonic.py`.
489. [x] `test_property_logger_never_drops.py`.
490. [x] `test_e2e_recorded_session.py` (vcrpy, manual-only).
491. [x] Coverage check ≥ 85 % globally.
492. [x] Ruff check zero violations.
493. [x] File-size lint: no `*.py` over 150 LoC (excl. blanks/comments).
494. [x] Add `scripts/check_file_size.py` and wire into CI.
495. [x] Add `scripts/check_no_forbidden_edges.py` — AST-grep forbidden module imports per `docs/architecture.md` §4.
496. [x] Wire forbidden-edges check into CI.
497. [x] Generate `docs/COMPLIANCE.md` table mapping brief §8 items to code + tests.
498. [x] Add `scripts/gen_compliance.py` that emits `COMPLIANCE.md` from grepping the tree.
499. [x] Wire compliance generator into CI (fails if any row is unchecked).
500. [x] Manual debate run for the README session-1 transcript.
501. [x] Save full session-1 transcript to `docs/session1.md`.
502. [x] Embed session-1 highlights in README §7.
503. [x] Take fresh screenshots from the session-1 replay.
504. [x] `docs/prompts.md` — final pass cleaning up prompt iteration log.
505. [x] Refresh `prompts.md` with the prompt that produced the best judge verdict.
506. [x] Ensure every public module has a docstring.
507. [x] Ensure every public class has a docstring.
508. [x] Ensure every public function has a docstring.
509. [x] `ruff format` once across the tree.
510. [x] Run full test suite + coverage one final time.
511. [x] Verify zero hardcoded values via `scripts/check_no_magic.py` grep.
512. [x] Tag `v1.0.0`.
513. [x] Commit: `chore: release v1.0.0`.
514. [x] Push tag.
515. [x] Flip GitHub repo to public.
516. [x] Add `rmisegal@gmail.com` as collaborator (belt-and-suspenders even if public).
517. [x] Verify lecturer can clone — try in a fresh dir.
518. [x] Fill out the Moodle Word template; save as PDF named `<group_code>-ex02.pdf`.
519. [x] Each group member submits the PDF separately on Moodle.
520. [x] Verify Moodle confirmation emails for both members.
521. [x] Sanity check: open `replays/<latest>.html` in a fresh browser; debate plays back.
522. [x] Sanity check: kill -9 a debater agent mid-debate; watchdog recovers.
523. [x] Sanity check: cost cap forces verdict cleanly.
524. [x] Sanity check: `uv run debate-ai start --no-browser` runs headless.
525. [x] Sanity check: deleting `config/personas/ronaldo.json` and running with `--persona-b python` works.
526. [x] Sanity check: every menu item produces a sensible output.
527. [x] Sanity check: `ruff check` clean on a fresh clone + `uv sync`.
528. [x] Sanity check: `pytest --cov` ≥ 85 % on a fresh clone.
529. [x] Final README diff pass — every claim in README has matching code/tests.
530. [x] Final PRD diff pass — every PRD reference still exists in the code tree.
531. [x] Archive `prompts.md` with a "v1.0.0 lock" header line.
532. [x] Celebrate. Notify partner. Submit.
