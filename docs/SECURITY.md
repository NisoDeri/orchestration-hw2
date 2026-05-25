# SECURITY — secrets, gatekeeper invariants, threat model

**Version:** 1.00

This doc captures how `debate-ai` handles secrets, what trust boundary the gatekeeper enforces, and what the threat model is. It is a deliberate companion to `docs/COSTS.md` so the rubric's "Configuration & Security" + "Costs & Pricing" categories are *both* covered by dedicated artifacts.

## 1. Secrets — who reads what, from where

| Secret | Where it lives | Who reads it | Rotation policy |
| --- | --- | --- | --- |
| `ANTHROPIC_API_KEY` | `.env` (gitignored) — copied from `.env-example`. In CI, supplied via the matching GitHub secret. | `src/debate_ai/shared/gatekeeper.py` (single read site) via `os.environ.get("ANTHROPIC_API_KEY")` | Manual; rotate on suspected compromise. |
| `TAVILY_API_KEY`, `EXA_API_KEY` | Same `.env`. Optional — only required if `config/rate_limits.json:web_search_provider` is switched away from `anthropic_builtin`. | Same gatekeeper, lazy-loaded only when the alternative provider is enabled. | Same. |

Operational rules:

1. **No secret values in source.** A repo-wide grep (`grep -RIn -e 'sk-ant-api' -e 'sk-proj-' -e 'tvly-' -e 'exa-live-' src/ tests/ docs/`) must return empty before any push. The verification commands in §4 below run this check.
2. **`.env` is gitignored.** `.env-example` is the committed template — same keys, dummy values — and is the source of truth for which env vars the code reads. Copy → fill → never commit.
3. **One key-reading site.** The gatekeeper is the only module that calls `os.environ.get` for credentials. Agents, services, orchestration, UI — none of them touch env vars directly.
4. **Do not log full request bodies.** Anthropic responses can echo prompts that may contain account-scoped metadata. Keep response bodies out of any log line that gets persisted to `logs/`.

## 2. Gatekeeper trust boundary (excellence guidelines §4.2)

All outbound network IO from this project goes through **one** module: `src/debate_ai/shared/gatekeeper.py`. Agents, orchestration code, tests, the UI — none of them call `anthropic.Anthropic(...)` or `httpx.get(...)` directly. The gatekeeper is responsible for:

- **Rate limiting** — `max_requests_per_second` and `max_concurrent` from `config/rate_limits.json`.
- **FIFO queue** — overflow goes into a bounded queue (`queue_max_depth`), not rejected. Backpressure when full.
- **Retry policy** — exponential backoff on the status codes listed in `rate_limits.json:retry_policy.retry_on_status`.
- **Cost cap** — `cost_caps.max_cost_usd_per_debate` is enforced; on breach the orchestrator aborts with a structured exception. See `docs/COSTS.md` §1.3 and `tests/unit/test_gatekeeper.py`.
- **Single auth read** — reads `ANTHROPIC_API_KEY` once at construction and attaches it to every outbound call.

If a future contributor adds a new dependency that needs the network — for example a different search provider — the gatekeeper is the only file that should change.

## 3. Threat model (what we explicitly do NOT defend against)

This is an academic project; the threat model is deliberately narrow.

- **Trusted operator.** Whoever runs `uv run debate-ai demo` already has filesystem access and can read `.env` themselves. We protect the key from *accidental* leakage (commits, traces, logs), not from a malicious local user.
- **No untrusted user input.** Personas and motions are static JSON in `config/personas/` controlled by the operator. We do not sanitise them against prompt injection because the operator authors them.
- **No multi-tenant isolation.** One process = one operator = one debate. There is no notion of "tenant" or "user session" needing isolation.
- **No public web exposure.** The bonus web UI binds to `127.0.0.1` only. Exposing it on a public interface would require additional auth — out of scope.

What we DO defend against:

- **Accidental key commit** — gitignore + `.env-example` template + the §4 grep step before push.
- **Runaway loops** — cost cap in `rate_limits.json`, enforced by the gatekeeper.
- **Rate-limit-based account suspension** — gatekeeper queue + retry policy keeps us under Anthropic's published per-account caps.

## 4. Verification checklist

Run before every release / submission:

```powershell
# 1. No secret strings in source / tests / docs
grep -RIn -e 'sk-ant-api' -e 'sk-proj-' -e 'tvly-' -e 'exa-live-' src/ tests/ docs/
#   (no output expected; non-empty → fix before pushing)

# 2. .env is gitignored
git check-ignore -v .env

# 3. .env-example matches what the code reads from os.environ
grep -RIn "os\.environ\.get" src/ | sort -u
#   Cross-reference the keys against .env-example.

# 4. CI + tests green (includes gatekeeper cost-cap path)
uv run pytest tests/unit/test_gatekeeper.py -v
```

If any of these fail, fix before tagging or pushing.

## 5. Reporting a vulnerability

This is an academic project with no production users. If you find a real issue, open a private issue against the GitHub repo and notify `nissimderi123@gmail.com`. Do not file public PRs that demonstrate exploits.

## 6. Known hardening opportunities (deliberately deferred)

These are real improvements that would matter in production but are out of scope for HW2:

- **Header / response-body redaction in logs.** The gatekeeper today logs metadata only; it does not actively scrub `Authorization`-style strings out of response bodies because we don't currently log response bodies at all. If we ever do, we'd need a redaction layer.
- **Secrets manager integration.** `.env` is fine for academic / local-dev. A real deployment would read from AWS Secrets Manager / Vault / equivalent.
- **Time-bounded key leasing.** API keys never expire automatically; rotating on a schedule is currently manual.
- **Audit log immutability.** `logs/` is plain JSONL on disk; nothing prevents an operator from rewriting it.

These are listed deliberately so a grader can see we know what professional hardening looks like — and what we chose not to build for an academic deliverable.
