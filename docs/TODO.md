# TODO — debate-ai

**Rule.** Each task = one observable outcome, ~1 commit. Mark `[x]` when done. Phases enforce ordering — finish phase N before starting N+1 except where parallelizable items are explicitly noted.

Total: **532 tasks**.

---

## Phase 0 — Pre-flight (8)

1. [ ] Confirm group code with partner Yarden; record in `README.md` §8.
2. [ ] Confirm Anthropic API key budget for HW2 (~$5–10 expected).
3. [ ] Confirm `web_search` is enabled in Claude Console org settings.
4. [ ] Confirm Python 3.10+ on dev machine (`uv python list`).
5. [ ] Confirm `uv --version` ≥ 0.4.
6. [ ] Confirm `git --version` available.
7. [ ] Decide README language (English / Hebrew); record decision in `prompts.md`.
8. [ ] Get user approval on all docs before scaffolding.

---

## Phase 1 — Scaffolding (44)

9. [ ] `git init -b main` in `hw2/`.
10. [ ] Create `.gitignore` with `.env`, `__pycache__/`, `.venv/`, `*.egg-info`, `logs/*.jsonl`, `replays/*`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`.
11. [ ] Create `.env-example` with `ANTHROPIC_API_KEY=your_key_here` placeholder.
12. [ ] Add `LICENSE` (MIT).
13. [ ] Create `pyproject.toml` skeleton — name, version, description, authors.
14. [ ] Add dependencies in `pyproject.toml`: `anthropic`, `pydantic`, `typer`, `rich`, `fastapi`, `uvicorn`, `httpx`.
15. [ ] Add dev dependencies: `pytest`, `pytest-cov`, `pytest-asyncio`, `hypothesis`, `ruff`, `vcrpy`.
16. [ ] Configure `[tool.ruff]` in `pyproject.toml`: line-length 100, target py310, select `E,F,W,I,N,UP,B,C4,SIM`, extend-ignore `E501`.
17. [ ] Configure `[tool.coverage.run]`: source `["src/debate_ai"]`.
18. [ ] Configure `[tool.coverage.report]`: `fail_under = 85`, `exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]`.
19. [ ] Configure `[project.scripts]`: `debate-ai = "debate_ai.cli.main:app"`.
20. [ ] Run `uv sync` — succeeds, `.venv/` created.
21. [ ] Create `src/debate_ai/__init__.py` with `__version__ = "1.00"` and `__all__ = ["DebateAI"]`.
22. [ ] Create `src/debate_ai/constants.py` empty placeholder.
23. [ ] Create empty subpackages: `sdk/`, `cli/`, `agents/`, `orchestration/`, `memory/`, `models/`, `services/`, `tools/`, `ui/`, `shared/`, `utils/`, `skills/` — each with empty `__init__.py`.
24. [ ] Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`.
25. [ ] Add `tests/conftest.py` with `mock_anthropic_client` fixture stub.
26. [ ] Create `config/` directory.
27. [ ] Create `config/setup.json` skeleton with `version: "1.00"`.
28. [ ] Create `config/debate.json` with default motion (Messi vs Ronaldo) and persona pair.
29. [ ] Create `config/models.json` with per-agent role config (model, skill_id, temperature, betas, tools, tool_choice).
30. [ ] Create `config/rate_limits.json` with `max_cost_usd_per_debate: 2.00`, queue depth, retry policy.
31. [ ] Create `config/logging.json` per `PRD_logging.md` §3 example.
32. [ ] Create `config/facts.json` skeleton with `lookup_order` + a few Messi/Ronaldo claims.
33. [ ] Create `config/versions.json` declaring required versions for each config file.
34. [ ] Create `config/personas/` and add `messi.json` per `PRD_agents.md` §3 schema.
35. [ ] Add `config/personas/ronaldo.json`.
36. [ ] Add `config/personas/python.json` (alt demo — argues Python is the better first language).
37. [ ] Add `config/personas/javascript.json`.
38. [ ] Each persona file gets `eras` array with ≥ 2 era variants.
39. [ ] Create `replays/` directory with a `.gitkeep`.
40. [ ] Create `logs/` directory with a `.gitkeep`.
41. [ ] Add `prompts.md` skeleton (Prompt Engineering Log header + initial entry).
42. [ ] First commit: `chore: initial scaffolding`.
43. [ ] Push to GitHub (private at first; flip to public before submission).
44. [ ] Invite `rmisegal@gmail.com` as collaborator.
45. [ ] CI: add `.github/workflows/ci.yml` running `uv sync && uv run ruff check && uv run pytest --cov`.
46. [ ] Run `uv run ruff check` — clean.
47. [ ] Run `uv run pytest` — collects zero tests, exits 0.
48. [ ] Commit: `chore: add CI workflow`.
49. [ ] Verify CI green on a push.
50. [ ] Tag the green CI commit `v0.1.0`.
51. [ ] Update README §3 with the exact commands above.
52. [ ] Commit: `docs: update README quickstart to match scaffolding`.

---

## Phase 2 — Shared (config / version / logger / gatekeeper) (62)

53. [ ] `shared/version.py`: `CODE_VERSION = "1.00"` + helper to assert config versions.
54. [ ] Test `test_version.py::test_code_version_format`.
55. [ ] `shared/config.py`: `ConfigLoader` class skeleton.
56. [ ] `ConfigLoader.load(name)` loads `config/<name>.json` and parses to Pydantic model.
57. [ ] `ConfigLoader.validate_versions()` cross-checks `versions.json` against each loaded config.
58. [ ] Pydantic models: `SetupConfig`, `DebateConfig`, `ModelsConfig`, `RateLimitsConfig`, `LoggingConfig`, `FactsConfig`, `VersionsConfig`.
59. [ ] Each config Pydantic model has a `version: str` field validated against `versions.json`.
60. [ ] `test_config_loader.py::test_load_valid` — each fixture config loads.
61. [ ] `test_config_loader.py::test_version_mismatch_raises` — bad version in versions.json → ConfigError.
62. [ ] `test_config_loader.py::test_missing_file_raises` — missing config → ConfigError with file path.
63. [ ] Commit: `feat(shared): config loader with version validation`.
64. [ ] `shared/logger.py`: `FifoLogger` class skeleton.
65. [ ] `FifoLogger.__init__` reads `config/logging.json`, creates `dir` if absent.
66. [ ] `FifoLogger.log(level, **fields)` writes a JSON line with timestamp.
67. [ ] `FifoLogger` rotates to next file at `lines_per_file`.
68. [ ] `FifoLogger` evicts oldest file past `max_files`.
69. [ ] `FifoLogger.tail(n)` returns last n lines across files.
70. [ ] `FifoLogger.tail_live()` generator yields new lines.
71. [ ] `.cursor` persistence file for resume-after-restart.
72. [ ] `test_logger_rotation.py`.
73. [ ] `test_logger_fifo_eviction.py`.
74. [ ] `test_logger_schema.py` — every line parses as JSON, has required keys.
75. [ ] `test_logger_cursor_persistence.py`.
76. [ ] `test_logger_tail.py`.
77. [ ] Commit: `feat(shared): FIFO logger`.
78. [ ] `shared/gatekeeper.py`: `Gatekeeper` class skeleton.
79. [ ] `Gatekeeper.__init__` reads `rate_limits.json`, builds `PriorityQueue`.
80. [ ] `Gatekeeper.call(req)` enqueues and returns response.
81. [ ] Rate-limit enforcement via token bucket per provider.
82. [ ] Retry policy with exponential backoff per `retry_policy` config.
83. [ ] `Gatekeeper.cost_so_far_usd()` accumulates from Anthropic usage headers + $0.01/search.
84. [ ] Backpressure: when queue full, `call` blocks up to `max_block_s`.
85. [ ] Log every call: started → finished with token usage.
86. [ ] Cost-cap detection: `cost_so_far_usd() >= max_cost_usd_per_debate` → raise `CostCapExceeded`.
87. [ ] `test_gatekeeper_rate_limit.py` — 11th call in 1s blocks (limit=10/s).
88. [ ] `test_gatekeeper_retry.py` — first call 500s, second 200s → returns successfully.
89. [ ] `test_gatekeeper_cost_tracking.py` — fake usage headers accumulate correctly.
90. [ ] `test_gatekeeper_cost_cap.py` — over-cap raises `CostCapExceeded`.
91. [ ] `test_gatekeeper_backpressure.py` — queue full, call blocks.
92. [ ] `test_gatekeeper_logs_every_call.py` — `FifoLogger` receives both started + finished records.
93. [ ] Commit: `feat(shared): gatekeeper with rate-limit, retry, cost tracking`.
94. [ ] `shared/seeding.py`: deterministic RNG seeding for era pick + crowd lean during tests.
95. [ ] `test_seeding.py::test_seeded_choices_reproducible`.
96. [ ] Commit: `feat(shared): RNG seeding utility`.
97. [ ] `shared/exceptions.py`: declare `ConfigError`, `AgentUnrecoverable`, `CostCapExceeded`, `RouteError`, `SchemaError`.
98. [ ] `test_exceptions_inheritance.py`.
99. [ ] Commit: `feat(shared): exception hierarchy`.
100. [ ] `utils/formatting.py`: `format_envelope(env)` for log + UI text.
101. [ ] `utils/validators.py`: `is_valid_url(s)`, `is_non_empty_list(x)`.
102. [ ] `test_formatting.py` + `test_validators.py`.
103. [ ] Commit: `feat(utils): formatting + validators`.
104. [ ] `constants.py`: enum `AgentRole`, `RoundKind`, `EnvelopeKind`, `LogLevel`.
105. [ ] `test_constants.py::test_enum_values`.
106. [ ] Commit: `feat: enums in constants.py`.
107. [ ] Run `ruff check` and `pytest --cov`. Coverage on shared/ ≥ 90 %.
108. [ ] Tag `v0.2.0`.
109. [ ] Commit: `chore: tag v0.2.0 — shared layer green`.
110. [ ] Update README §6 with the actual `shared/` modules in place.
111. [ ] Commit: `docs: README sync to v0.2.0`.
112. [ ] Push.
113. [ ] CI green.
114. [ ] Verify `uv run debate-ai --help` runs (even with no real commands yet).

---

## Phase 3 — Models + Memory (54)

115. [ ] `models/debate_models.py`: `Persona` Pydantic model from `PRD_agents.md` §3 schema.
116. [ ] `models/debate_models.py`: `Era` model with `label`, `system_addendum`.
117. [ ] `models/debate_models.py`: `RoundKind` enum re-export from constants.
118. [ ] `models/debate_models.py`: `DebateConfig` model.
119. [ ] `models/debate_models.py`: `DebateState` model with `history`, `scoreboard`, `current_round`.
120. [ ] `models/debate_models.py`: `Round` model.
121. [ ] `models/debate_models.py`: `ScoreAggregate` model — running totals per debater.
122. [ ] `models/debate_models.py`: `TurnScore` model — 4 dimensions × float.
123. [ ] `models/message_models.py`: `JudgeEnvelope` model per `PRD_judge.md` §3.
124. [ ] `models/message_models.py`: `DebaterReply` model per `PRD_agents.md` §3.
125. [ ] `DebaterReply.citations` non-empty validator.
126. [ ] `DebaterReply.references_opponent` non-empty validator (allow empty only on round 1 opening).
127. [ ] `models/message_models.py`: `Verdict` model.
128. [ ] `Verdict.score_a != Verdict.score_b` validator (no-tie).
129. [ ] `models/message_models.py`: `CommentaryReply` model.
130. [ ] `models/message_models.py`: `CrowdReply` model.
131. [ ] `models/message_models.py`: `FactCheckReply` model with nested `Claim` list.
132. [ ] `models/message_models.py`: `UIEvent` discriminated union per `PRD_ui.md` §1.
133. [ ] `AgentReply = Union[DebaterReply, CommentaryReply, ...]`.
134. [ ] Each model has `__init_subclass__` ensuring no extra fields (`model_config.extra = "forbid"`).
135. [ ] `test_persona_load.py` — load each shipped persona JSON, validate.
136. [ ] `test_envelope_round_trip.py` — model → JSON → model identical.
137. [ ] `test_verdict_no_tie.py` — `Verdict(score_a=70, score_b=70)` raises.
138. [ ] `test_debater_reply_citations_required.py`.
139. [ ] `test_debater_reply_references_opponent_required.py`.
140. [ ] `test_ui_event_discriminator.py` — `kind` field correctly routes payload.
141. [ ] Commit: `feat(models): Pydantic message + state models`.
142. [ ] `memory/conversation_memory.py`: `TranscriptEntry` model.
143. [ ] `memory/conversation_memory.py`: `ConversationMemory` class skeleton.
144. [ ] `ConversationMemory.append(envelope)` stamps `seq` + `in_round`.
145. [ ] `ConversationMemory.latest_for(agent_id)` returns most recent entry the agent should see.
146. [ ] `ConversationMemory.view_for(agent_id)` delegates to `ContextBuilder`.
147. [ ] `test_memory_append_seq_monotonic.py`.
148. [ ] `test_memory_in_round_correct.py`.
149. [ ] `memory/context_builder.py`: `ContextBuilder` class skeleton.
150. [ ] `ContextBuilder.build(agent_id, mem)` implements visibility rules from `PRD_memory.md` §2.
151. [ ] Per-agent visibility: Judge sees all.
152. [ ] Per-agent visibility: Debater sees only own-addressed + judge-broadcast.
153. [ ] Per-agent visibility: Commentator sees last round.
154. [ ] Per-agent visibility: Crowd sees latest debater envelope only.
155. [ ] Per-agent visibility: Fact-Checker sees latest debater envelope only.
156. [ ] Static prefix is byte-identical across turns when transcript prefix unchanged (cache stability).
157. [ ] `test_visibility_judge_sees_all.py`.
158. [ ] `test_visibility_debater_isolation.py`.
159. [ ] `test_visibility_commentator_one_round.py`.
160. [ ] `test_visibility_crowd_latest_only.py`.
161. [ ] `test_visibility_factchecker_latest_only.py`.
162. [ ] `test_context_builder_cache_stability.py`.
163. [ ] Commit: `feat(memory): transcript + per-agent context builder`.
164. [ ] Coverage on `models/` + `memory/` ≥ 90 %.
165. [ ] Run `ruff check`.
166. [ ] Tag `v0.3.0`.
167. [ ] Commit: `chore: tag v0.3.0 — models + memory green`.
168. [ ] Update README §6.

---

## Phase 4 — Tools layer (web_search, web_fetch, citation, Wikipedia MCP) (42)

169. [ ] `tools/web_search_tool.py`: `Citation` model (`url`, `title`, `snippet`).
170. [ ] `tools/web_search_tool.py`: `SearchProvider` ABC.
171. [ ] `tools/web_search_tool.py`: `AnthropicBuiltinSearch` provider returning `tool_choice + tools` config snippet (passed to agent's Anthropic call).
172. [ ] `tools/web_search_tool.py`: `TavilySearch` provider fallback.
173. [ ] `tools/web_search_tool.py`: `ExaSearch` provider fallback.
174. [ ] `tools/web_search_tool.py`: `OmniSearch` provider fallback.
175. [ ] `tools/web_search_tool.py`: `search(query, provider=...)` dispatch on config.
176. [ ] `tools/citation_tool.py`: `Citation.from_anthropic_block(block)` parser.
177. [ ] `tools/citation_tool.py`: `Citation.fetch_text(url)` via Anthropic `web_fetch` server tool.
178. [ ] `tools/wikipedia_mcp.py`: stdio-based MCP client wrapper.
179. [ ] `tools/wikipedia_mcp.py`: `WikipediaMCP.summary(title)`, `.search(query)`.
180. [ ] Wikipedia MCP launches `uvx wikipedia-mcp` as subprocess.
181. [ ] `test_search_dispatch.py` — config provider change swaps implementation.
182. [ ] `test_anthropic_builtin_search.py` — emits correct tool config block.
183. [ ] `test_tavily_search.py` — mocked HTTP, hits correct endpoint with API key.
184. [ ] `test_exa_search.py` — mocked HTTP.
185. [ ] `test_citation_from_anthropic_block.py` — parses `web_search_tool_result` block.
186. [ ] `test_citation_fetch_text.py` — fetches a URL via `web_fetch`.
187. [ ] `test_wikipedia_mcp_summary.py` — subprocess launches, summary returns.
188. [ ] `test_wikipedia_mcp_search.py`.
189. [ ] Commit: `feat(tools): search + citation + wikipedia mcp`.
190. [ ] Coverage on `tools/` ≥ 90 %.
191. [ ] Tag `v0.4.0`.
192. [ ] Commit: `chore: tag v0.4.0 — tools green`.
193. [ ] `services/facts_service.py`: `FactsService` class.
194. [ ] `FactsService.extract_checkable_claims(text)` heuristic split.
195. [ ] `FactsService.verify(claim)` walks `lookup_order` from `facts.json`.
196. [ ] `FactsService.verify` returns `Verdict("correct"|"incorrect"|"misleading"|"unverifiable")` with severity.
197. [ ] `test_facts_service_local_hit.py` — `facts.json` resolves first.
198. [ ] `test_facts_service_wikipedia_fallback.py`.
199. [ ] `test_facts_service_web_search_last_resort.py`.
200. [ ] `test_facts_service_unverifiable.py`.
201. [ ] Commit: `feat(services): facts service for fact-checker`.
202. [ ] `services/scoring_service.py`: `ScoringService` class.
203. [ ] `ScoringService.score_turn(reply)` returns `TurnScore`.
204. [ ] `ScoringService.aggregate(turn_scores)` returns `ScoreAggregate`.
205. [ ] `ScoringService.detect_drift(history)` returns `bool` per `PRD_judge.md` §7.
206. [ ] `ScoringService.lie_catch_bonus(reply, opponent_history)` returns +1 floor on persuasion.
207. [ ] `test_score_turn.py`.
208. [ ] `test_aggregate.py`.
209. [ ] `test_detect_drift.py`.
210. [ ] `test_lie_catch_bonus.py`.

---

## Phase 5 — Agents (86)

211. [ ] `agents/base_agent.py`: `BaseAgent` ABC per `PRD_agents.md` §2.
212. [ ] `BaseAgent.__init__` validates `skill_id` bundle exists on disk.
213. [ ] `BaseAgent._call_anthropic` chokepoint routes via `Gatekeeper`.
214. [ ] `BaseAgent._validate_reply` raises `SchemaError` on bad payload.
215. [ ] `BaseAgent.alive()` heartbeat for watchdog.
216. [ ] `agents/mixins.py`: `JsonReplyMixin` extracts JSON from `tool_use` blocks.
217. [ ] `agents/mixins.py`: `CitedReplyMixin` asserts non-empty citations.
218. [ ] `agents/mixins.py`: `MemoryAwareMixin` formats per-agent context.
219. [ ] `agents/mixins.py`: `SkillBoundMixin` injects `container.skills`.
220. [ ] `test_base_agent_gatekeeper_called.py`.
221. [ ] `test_base_agent_schema_validation.py`.
222. [ ] `test_mixin_json_extraction.py`.
223. [ ] `test_mixin_cited_required.py`.
224. [ ] `test_mixin_memory_aware_visibility.py`.
225. [ ] `test_mixin_skill_bound_payload.py`.
226. [ ] Commit: `feat(agents): BaseAgent + mixins`.
227. [ ] `agents/debater_agent.py`: `DebaterAgent` per `PRD_agents.md` §3.
228. [ ] `DebaterAgent.__init__` loads `persona` from `config/personas/<name>.json`.
229. [ ] `DebaterAgent.respond(envelope)` returns `DebaterReply`.
230. [ ] `DebaterAgent.switch_era(era)` swaps `current_era`.
231. [ ] System prompt assembly: persona base + era addendum (if set) + skill instructions.
232. [ ] Tool config: `web_search_20260209` always, `tool_choice: {"type": "any"}`.
233. [ ] `test_debater_persona_load.py`.
234. [ ] `test_debater_respond_returns_reply.py` (mocked Anthropic).
235. [ ] `test_debater_era_switch.py`.
236. [ ] `test_debater_system_prompt_era_addendum.py`.
237. [ ] `test_debater_drift_resistance.py` — given an agreeing opponent, still contradicts.
238. [ ] `test_debater_citations_present.py`.
239. [ ] `test_debater_references_opponent_present.py`.
240. [ ] Commit: `feat(agents): DebaterAgent`.
241. [ ] `agents/judge_agent.py`: `JudgeAgent` per `PRD_judge.md`.
242. [ ] `JudgeAgent.__init__` loads `scoring-rubric` skill + `ScoringService`.
243. [ ] `JudgeAgent.relay(from, to, payload)` returns `JudgeEnvelope`.
244. [ ] `JudgeAgent.score_turn(reply)` delegates to `ScoringService`.
245. [ ] `JudgeAgent.verdict(running)` calls Anthropic to write verdict prose, validates no-tie.
246. [ ] `JudgeAgent` system prompt OMITS the motion text.
247. [ ] `cache_control: ephemeral` on system prompt + transcript prefix.
248. [ ] `JudgeAgent.detect_drift` calls `ScoringService.detect_drift`, emits re-anchor ruling.
249. [ ] `test_judge_relay_routing.py`.
250. [ ] `test_judge_score_turn.py`.
251. [ ] `test_judge_verdict_no_tie_retry.py`.
252. [ ] `test_judge_verdict_no_tie_fallback.py` (aggregate winner).
253. [ ] `test_judge_topic_ignorance.py`.
254. [ ] `test_judge_prompt_cache_stability.py`.
255. [ ] `test_judge_drift_detected.py`.
256. [ ] Commit: `feat(agents): JudgeAgent`.
257. [ ] `agents/commentator_agent.py`: `CommentatorAgent`.
258. [ ] `CommentatorAgent.respond` per `PRD_color_crew.md` §1.
259. [ ] `max_tokens=80`.
260. [ ] `test_commentator_one_sentence.py`.
261. [ ] `test_commentator_no_winner_claim.py`.
262. [ ] Commit: `feat(agents): CommentatorAgent`.
263. [ ] `agents/crowd_agent.py`: `CrowdAgent`.
264. [ ] `CrowdAgent.respond` per `PRD_color_crew.md` §2.
265. [ ] `CrowdAgent` context is *latest debater envelope only* (no scoreboard).
266. [ ] `CrowdReply.emojis` 1–5.
267. [ ] `CrowdReply.one_liner` ≤ 8 words.
268. [ ] `test_crowd_respond.py`.
269. [ ] `test_crowd_emoji_count.py`.
270. [ ] `test_crowd_oneliner_length.py`.
271. [ ] `test_crowd_no_scoreboard_leak.py`.
272. [ ] Commit: `feat(agents): CrowdAgent`.
273. [ ] `agents/factchecker_agent.py`: `FactCheckerAgent`.
274. [ ] `FactCheckerAgent.respond` per `PRD_factchecker.md` §6.
275. [ ] Delegates claim extraction + verification to `FactsService`.
276. [ ] Multi-claim per turn supported.
277. [ ] `test_factchecker_respond.py`.
278. [ ] `test_factchecker_multi_claim.py`.
279. [ ] `test_factchecker_does_not_score.py` — `score_turn` byte-identical with/without FC events.
280. [ ] `test_factchecker_priority.py`.
281. [ ] `test_factchecker_severity_classification.py`.
282. [ ] Commit: `feat(agents): FactCheckerAgent`.
283. [ ] Agent factory: `agents/factory.py::build_agent(role, config) → BaseAgent`.
284. [ ] Factory uses `config/models.json` to bind each role to model/skill/tools/temperature.
285. [ ] `test_agent_factory.py`.
286. [ ] Commit: `feat(agents): agent factory`.
287. [ ] Coverage on `agents/` ≥ 90 %.
288. [ ] Tag `v0.5.0`.
289. [ ] Commit: `chore: tag v0.5.0 — agents green`.
290. [ ] Push, CI green.
291. [ ] Update README §6 with the agent module list.
292. [ ] Commit: `docs: README sync to v0.5.0`.
293. [ ] Append a `prompts.md` entry: "Prompt for `rhetorical-aggression` skill — first iteration".
294. [ ] Append a `prompts.md` entry per skill (6 total).
295. [ ] Append a `prompts.md` entry: "Judge no-tie retry phrasing".
296. [ ] Verify no agent module references another agent module (forbidden by class diagram).

---

## Phase 6 — Skills bundles (32)

297. [ ] `src/debate_ai/skills/rhetorical-aggression/SKILL.md` — instruction set.
298. [ ] `skills/rhetorical-aggression/scripts/.gitkeep`.
299. [ ] `skills/rhetorical-aggression/resources/.gitkeep`.
300. [ ] `skills/evidence-marshalling/SKILL.md`.
301. [ ] `skills/evidence-marshalling/scripts/.gitkeep`.
302. [ ] `skills/scoring-rubric/SKILL.md` — judge rubric + no-tie + relay protocol.
303. [ ] `skills/scoring-rubric/scripts/.gitkeep`.
304. [ ] `skills/color-commentary/SKILL.md`.
305. [ ] `skills/audience-sentiment/SKILL.md`.
306. [ ] `skills/claim-verification/SKILL.md` — facts.json → wikipedia → web_search priority.
307. [ ] Upload each of the 6 skills via `/v1/skills` API → record returned IDs.
308. [ ] Pin skill IDs in `config/models.json`.
309. [ ] `tools/skill_upload.py` helper script to re-upload skills (`uv run debate-ai skills upload`).
310. [ ] `test_skill_bundles_on_disk.py` — each of 6 has SKILL.md.
311. [ ] `test_skill_upload_script.py` — mocks `/v1/skills` endpoint.
312. [ ] `test_skill_id_in_models_config.py`.
313. [ ] Each `SKILL.md` ≤ 200 lines.
314. [ ] Each `SKILL.md` references the JSON schema the agent must obey.
315. [ ] Commit per skill: `feat(skills): <skill-id> bundle`.
316. [ ] Commit: `feat(tools): skill upload helper script`.
317. [ ] Iterate: run a dry-run debate with mocked Anthropic; verify each skill's instructions visible in the request payload.
318. [ ] Iterate: tweak `rhetorical-aggression` skill if debater is too polite.
319. [ ] Iterate: tweak `evidence-marshalling` if debater forgets citations.
320. [ ] Iterate: tweak `scoring-rubric` if judge ties too often.
321. [ ] Iterate: tweak `color-commentary` if commentator declares winners.
322. [ ] Iterate: tweak `audience-sentiment` if crowd parrots judge.
323. [ ] Iterate: tweak `claim-verification` if FC over-flags.
324. [ ] Commit each iteration as `chore(skills): tune <skill>`.
325. [ ] Append `prompts.md` per significant skill change.
326. [ ] Tag `v0.6.0` once skills produce a clean dry-run.
327. [ ] Commit: `chore: tag v0.6.0 — skills green`.
328. [ ] Push.

---

## Phase 7 — Orchestration (56)

329. [ ] `orchestration/routing.py`: `Routing` class.
330. [ ] `Routing.__init__(judge)` stores judge ref.
331. [ ] `Routing.relay(from_agent, payload)` → `JudgeEnvelope` to opposite debater.
332. [ ] Routing asserts no debater-to-debater edge.
333. [ ] `test_routing_swap.py` — A → relay → goes to B.
334. [ ] `test_routing_no_direct_edge.py`.
335. [ ] Commit: `feat(orchestration): routing`.
336. [ ] `orchestration/round_manager.py`: `RoundManager` class.
337. [ ] `RoundManager.run(state, agents)` executes one round.
338. [ ] Round kinds: `opening`, `rebuttal`, `era_swap`, `closing`.
339. [ ] Speaking order: A → judge relay → B → judge relay → ... × pings_per_side.
340. [ ] Score each relayed reply via `ScoringService`.
341. [ ] Emit `UIEvent(round_changed, agent_message, score_update)` per step.
342. [ ] `test_round_opening.py`.
343. [ ] `test_round_rebuttal_pings.py`.
344. [ ] `test_round_emits_events_in_order.py`.
345. [ ] Commit: `feat(orchestration): round manager`.
346. [ ] `orchestration/era_swap.py`: `EraSwap` class.
347. [ ] `EraSwap.pick(persona, strategy)` returns `Era`.
348. [ ] Strategies: `random`, `first`, `latest`, `contrasting`.
349. [ ] `test_era_pick_random.py` (seeded).
350. [ ] `test_era_pick_contrasting.py` — furthest apart by year parse.
351. [ ] `test_era_pick_no_eras_returns_none.py`.
352. [ ] Commit: `feat(orchestration): era swap pick`.
353. [ ] `orchestration/watchdog.py`: `Watchdog` class per `PRD_watchdog.md`.
354. [ ] `Watchdog.supervise(fn, args, timeout, on_hang)` uses ThreadPoolExecutor.
355. [ ] Per-agent restart counter, capped at `max_restarts`.
356. [ ] Schema-break retry with stricter prompt.
357. [ ] Citation-missing retry.
358. [ ] `AgentUnrecoverable` raised on exhaust.
359. [ ] Keep-alive ticks every `keepalive_interval_s`, no API calls.
360. [ ] `test_watchdog_timeout_restarts.py`.
361. [ ] `test_watchdog_max_restarts_exhausted.py`.
362. [ ] `test_watchdog_schema_break_retry.py`.
363. [ ] `test_watchdog_citation_retry.py`.
364. [ ] `test_watchdog_keepalive_no_api_calls.py`.
365. [ ] Commit: `feat(orchestration): watchdog + keepalive`.
366. [ ] `orchestration/event_emitter.py`: `EventEmitter` per `PRD_ui.md` §1.
367. [ ] `EventEmitter.emit(event)`, `.subscribe(cb) → Unsubscribe`, `.replay(from_seq)`.
368. [ ] Thread-safe with `RLock`.
369. [ ] `test_event_emitter_emit_subscribe.py`.
370. [ ] `test_event_emitter_replay_from_seq.py`.
371. [ ] `test_event_emitter_thread_safety.py`.
372. [ ] Commit: `feat(orchestration): event emitter`.
373. [ ] `orchestration/debate_manager.py`: `DebateManager` class.
374. [ ] `DebateManager.start()` runs the full lifecycle.
375. [ ] Sequence: opening → N rebuttals (with era_swap round) → closing → verdict.
376. [ ] On `CostCapExceeded` → force verdict from aggregate.
377. [ ] On `AgentUnrecoverable` → force verdict.
378. [ ] On clean end → emit `debate_ended` UIEvent.
379. [ ] `test_debate_full_run_mocked.py`.
380. [ ] `test_debate_cost_cap_forces_verdict.py`.
381. [ ] `test_debate_unrecoverable_forces_verdict.py`.
382. [ ] `test_debate_event_order.py`.
383. [ ] `test_debate_no_tie_invariant.py` — 100 mocked debates, zero ties.
384. [ ] Commit: `feat(orchestration): debate manager`.

---

## Phase 8 — Services (12)

385. [ ] `services/debate_service.py`: `DebateService` wires `DebateManager` + `EventEmitter` + persisting.
386. [ ] `DebateService.run(motion, persona_a, persona_b, ...)` → `DebateResult`.
387. [ ] `DebateService.list_personas()` walks `config/personas/`.
388. [ ] `DebateService.list_motions()` returns the default + any user-added.
389. [ ] `DebateService.replay(debate_id)` loads from `replays/`.
390. [ ] `DebateService.export_replay(debate_id, path)` renders self-contained HTML.
391. [ ] `test_debate_service_run.py`.
392. [ ] `test_debate_service_list_personas.py`.
393. [ ] `test_debate_service_replay_roundtrip.py`.
394. [ ] `test_debate_service_export_selfcontained.py`.
395. [ ] Commit: `feat(services): debate service`.
396. [ ] Tag `v0.7.0`.

---

## Phase 9 — SDK (12)

397. [ ] `sdk/sdk.py`: `DebateAI` class per `PLAN.md` §3.
398. [ ] `DebateAI.__init__(config_dir)` loads all configs via `ConfigLoader`.
399. [ ] `DebateAI.run_debate(...)` calls `DebateService.run`, optionally with event callback.
400. [ ] `DebateAI.list_personas()`, `.list_motions()`, `.replay()`, `.export_replay()` pass-throughs.
401. [ ] SDK is the only module exported from `__init__.py::__all__`.
402. [ ] `test_sdk_smoke.py` — instantiate + run mocked debate end-to-end.
403. [ ] `test_sdk_run_with_callback.py`.
404. [ ] `test_sdk_replay.py`.
405. [ ] `test_sdk_export.py`.
406. [ ] Commit: `feat(sdk): single public entry point`.
407. [ ] Tag `v0.8.0`.
408. [ ] Update README quickstart with real SDK usage example.

---

## Phase 10 — CLI menu (28)

409. [ ] `cli/main.py`: Typer app with `app = typer.Typer()`.
410. [ ] `cli/main.py`: `main()` default → calls `menu.run_loop(sdk)`.
411. [ ] `cli/main.py`: `run` subcommand for one-shot debate.
412. [ ] `cli/main.py`: `start` subcommand launches FastAPI + opens browser.
413. [ ] `cli/main.py`: `skills upload` subcommand (re-uploads skill bundles).
414. [ ] `cli/menu.py`: `run_loop(sdk)` per `PRD_ui.md` §2 layout.
415. [ ] Item [1] Run debate — calls `sdk.run_debate()`.
416. [ ] Item [2] Choose motion — text input, persists in-memory.
417. [ ] Item [3] Choose personas — list from `sdk.list_personas()`, two prompts.
418. [ ] Item [4] Run + watch live — registers `on_event` callback that prints Rich panels.
419. [ ] Item [5] Show last verdict — pretty-prints last `Verdict`.
420. [ ] Item [6] Browse replays — `os.listdir("replays/")`, pick one, opens HTML in browser.
421. [ ] Item [7] Tail logs — calls `FifoLogger.tail(100)` and renders.
422. [ ] Item [7b] Tail logs (live) — streams.
423. [ ] Item [8] Show config / version — prints `__version__` + loaded configs' versions.
424. [ ] Item [0] Quit.
425. [ ] All menu items thin wrappers — no business logic.
426. [ ] Live watch renders chat bubbles with Rich panels.
427. [ ] `test_cli_help.py` — `--help` lists subcommands.
428. [ ] `test_cli_run_subcommand.py`.
429. [ ] `test_menu_loop_key_dispatch.py`.
430. [ ] `test_menu_no_business_logic.py` — AST-grep agent imports inside cli/.
431. [ ] `test_menu_choose_personas.py`.
432. [ ] `test_menu_browse_replays.py`.
433. [ ] `test_menu_tail_logs.py`.
434. [ ] Commit: `feat(cli): typer app + keyboard menu`.
435. [ ] Tag `v0.9.0`.
436. [ ] Update README with menu screenshot placeholder.

---

## Phase 11 — UI (FastAPI + SSE + HTML) (44)

437. [ ] `ui/events.py`: shared event emitter facade (delegates to `orchestration/event_emitter.py`).
438. [ ] `ui/server.py`: FastAPI app skeleton.
439. [ ] Route `GET /` returns `static/index.html`.
440. [ ] Route `GET /static/{path}` serves css/js.
441. [ ] Route `POST /start` accepts `{motion, persona_a, persona_b, pings}`, returns `{debate_id}`.
442. [ ] Route `GET /stream?debate_id=&from_seq=` returns `text/event-stream` SSE.
443. [ ] SSE replays missed events from `from_seq` before subscribing live.
444. [ ] Route `GET /verdict/{debate_id}` returns the verdict (404 if not yet emitted).
445. [ ] Route `GET /replay/{debate_id}` returns self-contained HTML as `application/octet-stream`.
446. [ ] `ui/replay_export.py`: renders `replays/<id>.html` from a `ConversationMemory`.
447. [ ] Replay HTML inlines CSS + JS + the event log as JSON.
448. [ ] Replay player has play/pause/scrub/speed controls.
449. [ ] `static/index.html`: semantic structure (header, main grid, footer).
450. [ ] `static/styles.css`: Telegram-style bubbles, agent-colored from `persona.color_hex`.
451. [ ] `static/styles.css`: responsive grid 70/30 desktop, stacked mobile.
452. [ ] `static/app.js`: `EventSource('/stream?debate_id=...')` wiring.
453. [ ] `static/app.js`: typing indicator on `agent_started_typing`.
454. [ ] `static/app.js`: bubble append on `agent_message`.
455. [ ] `static/app.js`: scoreboard update on `score_update`.
456. [ ] `static/app.js`: confidence meter animation.
457. [ ] `static/app.js`: round badge on `round_changed`.
458. [ ] `static/app.js`: fact-check chip under bubble (severity color).
459. [ ] `static/app.js`: commentator + crowd inline blocks.
460. [ ] `static/app.js`: verdict modal on `verdict`.
461. [ ] `static/app.js`: replay-mode toggle (rate slider).
462. [ ] Browser auto-open via `webbrowser.open` in `cli main.py::start`.
463. [ ] `--no-browser` flag for CI.
464. [ ] `test_ui_server_index.py`.
465. [ ] `test_ui_sse_stream_events.py`.
466. [ ] `test_ui_sse_replay_from_seq.py`.
467. [ ] `test_ui_post_start.py`.
468. [ ] `test_ui_get_verdict_404_until_ready.py`.
469. [ ] `test_ui_replay_html_selfcontained.py` — open in headless Chromium without network.
470. [ ] `test_ui_static_files_present.py`.
471. [ ] `test_static_html_validates.py` — passes `html5validator` linter.
472. [ ] `test_static_css_no_unused_classes.py`.
473. [ ] Visual smoke test: spawn server, run a debate, capture screenshot to `docs/screenshots/menu.png` and `docs/screenshots/chat.png`.
474. [ ] Commit: `feat(ui): FastAPI + SSE + HTML chat`.
475. [ ] Tag `v0.10.0`.
476. [ ] Update README §7 with real screenshots.
477. [ ] Commit: `docs: README screenshots`.
478. [ ] Push.
479. [ ] CI green.
480. [ ] Manual end-to-end smoke: `uv run debate-ai start` → browser tab → full debate visible.

---

## Phase 12 — Tests + polish + release (52)

481. [ ] `test_integration_full_debate_mocked.py` — 10 pings, era-swap, verdict, no tie.
482. [ ] `test_integration_drift_intervention.py`.
483. [ ] `test_integration_watchdog_recovery.py`.
484. [ ] `test_integration_cost_cap_clean_end.py`.
485. [ ] `test_integration_replay_roundtrip.py`.
486. [ ] `test_integration_two_persona_pairs.py` — Messi/Ronaldo AND Python/JS produce coherent debates with zero code change.
487. [ ] `test_property_routing_preserves_identity.py` (hypothesis).
488. [ ] `test_property_aggregate_monotonic.py`.
489. [ ] `test_property_logger_never_drops.py`.
490. [ ] `test_e2e_recorded_session.py` (vcrpy, manual-only).
491. [ ] Coverage check ≥ 85 % globally.
492. [ ] Ruff check zero violations.
493. [ ] File-size lint: no `*.py` over 150 LoC (excl. blanks/comments).
494. [ ] Add `scripts/check_file_size.py` and wire into CI.
495. [ ] Add `scripts/check_no_forbidden_edges.py` — AST-grep forbidden module imports per `docs/architecture.md` §4.
496. [ ] Wire forbidden-edges check into CI.
497. [ ] Generate `docs/COMPLIANCE.md` table mapping brief §8 items to code + tests.
498. [ ] Add `scripts/gen_compliance.py` that emits `COMPLIANCE.md` from grepping the tree.
499. [ ] Wire compliance generator into CI (fails if any row is unchecked).
500. [ ] Manual debate run for the README session-1 transcript.
501. [ ] Save full session-1 transcript to `docs/session1.md`.
502. [ ] Embed session-1 highlights in README §7.
503. [ ] Take fresh screenshots from the session-1 replay.
504. [ ] `docs/prompts.md` — final pass cleaning up prompt iteration log.
505. [ ] Refresh `prompts.md` with the prompt that produced the best judge verdict.
506. [ ] Ensure every public module has a docstring.
507. [ ] Ensure every public class has a docstring.
508. [ ] Ensure every public function has a docstring.
509. [ ] `ruff format` once across the tree.
510. [ ] Run full test suite + coverage one final time.
511. [ ] Verify zero hardcoded values via `scripts/check_no_magic.py` grep.
512. [ ] Tag `v1.0.0`.
513. [ ] Commit: `chore: release v1.0.0`.
514. [ ] Push tag.
515. [ ] Flip GitHub repo to public.
516. [ ] Add `rmisegal@gmail.com` as collaborator (belt-and-suspenders even if public).
517. [ ] Verify lecturer can clone — try in a fresh dir.
518. [ ] Fill out the Moodle Word template; save as PDF named `<group_code>-ex02.pdf`.
519. [ ] Each group member submits the PDF separately on Moodle.
520. [ ] Verify Moodle confirmation emails for both members.
521. [ ] Sanity check: open `replays/<latest>.html` in a fresh browser; debate plays back.
522. [ ] Sanity check: kill -9 a debater agent mid-debate; watchdog recovers.
523. [ ] Sanity check: cost cap forces verdict cleanly.
524. [ ] Sanity check: `uv run debate-ai start --no-browser` runs headless.
525. [ ] Sanity check: deleting `config/personas/ronaldo.json` and running with `--persona-b python` works.
526. [ ] Sanity check: every menu item produces a sensible output.
527. [ ] Sanity check: `ruff check` clean on a fresh clone + `uv sync`.
528. [ ] Sanity check: `pytest --cov` ≥ 85 % on a fresh clone.
529. [ ] Final README diff pass — every claim in README has matching code/tests.
530. [ ] Final PRD diff pass — every PRD reference still exists in the code tree.
531. [ ] Archive `prompts.md` with a "v1.0.0 lock" header line.
532. [ ] Celebrate. Notify partner. Submit.
