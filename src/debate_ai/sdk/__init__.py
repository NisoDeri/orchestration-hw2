"""SDK layer — the only public entry point.

Per ``docs/PLAN.md`` §3 and ``CLAUDE.md`` Locked design rule 9, every piece of
business logic must be reachable through this module. CLI, UI, and tests all
consume the SDK; nothing else.
"""
