"""Rich console output for demo debate — chat-style with all agents."""

from __future__ import annotations

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from debate_ai.agents.demo_support_data import (
    COMMENTATOR_LINES,
    CROWD_REACTIONS,
    FACT_CHECKS,
    JUDGE_PROMPTS,
)
from debate_ai.models.message_models import UIEvent

console = Console()
_C = {
    "debater-a": "blue",
    "debater-b": "red",
    "judge": "yellow",
    "commentator": "magenta",
    "crowd": "cyan",
    "fact-checker": "green",
}
_N = {
    "debater-a": "Messi",
    "debater-b": "Ronaldo",
    "judge": "Judge",
    "commentator": "Commentator",
    "crowd": "Crowd",
    "fact-checker": "Fact-Checker",
}
_turn = 0


def _typing(name: str, color: str) -> None:
    console.print(f"  [dim]{name} is typing...[/dim]", end="")
    time.sleep(0.5)
    console.print("\r" + " " * 40 + "\r", end="")


def _chat(role: str, text: str) -> None:
    color = _C.get(role, "white")
    name = _N.get(role, role)
    _typing(name, color)
    console.print(f"  [{color} bold]{name}:[/{color} bold] {text}")
    time.sleep(0.3)


def demo_subscriber(event: UIEvent) -> None:
    global _turn  # noqa: PLW0603
    kind, p = event.kind, event.payload
    if kind == "debate_started":
        _start_debate(p)
    elif kind == "round_changed":
        rnd, rk = p.get("round", 0), p.get("kind", "")
        label = {
            "opening": "OPENING",
            "rebuttal": "REBUTTAL",
            "era_swap": "ERA-SWAP",
            "closing": "CLOSING",
        }.get(rk, rk)
        console.print(f"\n{'=' * 60}")
        console.print(f"[bold yellow]  Round {rnd} — {label}[/bold yellow]")
        console.print(f"{'=' * 60}")
    elif kind == "agent_message":
        _handle_turn(p)
    elif kind == "score_update":
        _print_score(p)
    elif kind == "verdict":
        _print_verdict(p)
    elif kind == "debate_ended":
        w = _N.get(p.get("winner"), p.get("winner"))
        console.print(f"\n[bold green]Debate ended. Winner: {w}[/bold green]")


def _start_debate(p: dict) -> None:
    console.print()
    console.print(
        Panel(
            f"[bold white]{p.get('motion', '')}[/bold white]\n\n"
            "[dim]Judge scores PERSUASION only. Lies are allowed.\n"
            "All messages route: Child -> Father (Judge) -> Child[/dim]",
            title="DEBATE STARTED",
            border_style="green",
        )
    )
    _chat("judge", JUDGE_PROMPTS[0])


def _handle_turn(p: dict) -> None:
    global _turn  # noqa: PLW0603
    agent = p.get("agent", "?")
    arg = p.get("argument", "")
    jp_idx = min(_turn + 1, len(JUDGE_PROMPTS) - 1)
    _chat("judge", JUDGE_PROMPTS[jp_idx])
    time.sleep(0.2)
    _chat(agent, arg)
    cite = p.get("cite", "")
    if cite:
        console.print(f"  [dim]    Citation: {cite}[/dim]")
    _print_support(_turn)
    _turn += 1


def _print_support(idx: int) -> None:
    if idx < len(COMMENTATOR_LINES):
        _chat("commentator", COMMENTATOR_LINES[idx])
    if idx < len(CROWD_REACTIONS):
        emojis, liner, lean = CROWD_REACTIONS[idx]
        direction = "Messi" if lean > 0 else "Ronaldo" if lean < 0 else "split"
        _chat("crowd", f"{''.join(emojis)} {liner} [dim](leaning {direction})[/dim]")
    if idx < len(FACT_CHECKS) and FACT_CHECKS[idx]:
        for fc in FACT_CHECKS[idx]:
            v = fc["verdict"].upper()
            color = "green" if v == "CORRECT" else "red" if v == "INCORRECT" else "yellow"
            _chat("fact-checker", f'[{color}]{v}[/{color}]: "{fc["claim"]}" — {fc["note"]}')


def _print_score(p: dict) -> None:
    s = p.get("score", {})
    name = _N.get(p.get("agent", "?"), "?")
    parts = [
        f"{k[:4].title()}: {s.get(k, 0):.1f}"
        for k in ("logic", "evidence", "persuasion", "counter")
    ]
    total = sum(s.get(k, 0) for k in ("logic", "evidence", "persuasion", "counter"))
    console.print(f"  [dim]  Judge scores {name}: {' | '.join(parts)} = {total:.1f}/40[/dim]")


def _print_verdict(p: dict) -> None:
    console.print(f"\n{'=' * 60}")
    table = Table(title="FINAL VERDICT", show_header=True, border_style="green")
    table.add_column("Category", style="bold")
    table.add_column("Messi (A)", justify="center", style="blue")
    table.add_column("Ronaldo (B)", justify="center", style="red")
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{p.get('score_a', 0):.1f}[/bold]",
        f"[bold]{p.get('score_b', 0):.1f}[/bold]",
    )
    rb = p.get("rubric_breakdown", {})
    for key in ("logic", "evidence", "persuasion", "counter"):
        a, b = rb.get("debater-a", {}).get(key, 0), rb.get("debater-b", {}).get(key, 0)
        ma = "[bold green]" if a > b else ""
        mb = "[bold green]" if b > a else ""
        table.add_row(key.capitalize(), f"{ma}{a:.1f}", f"{mb}{b:.1f}")
    console.print(table)
    console.print(f"\n[italic]{p.get('reasoning', '')}[/italic]")
