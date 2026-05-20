"""Rich console output for demo debate — prints each turn live."""
from __future__ import annotations

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from debate_ai.models.message_models import UIEvent

console = Console()

_COLORS = {"debater-a": "blue", "debater-b": "red", "judge": "yellow"}
_NAMES = {"debater-a": "Messi", "debater-b": "Ronaldo", "judge": "Judge"}


def demo_subscriber(event: UIEvent) -> None:
    """Subscribe to EventEmitter and print each event to the terminal."""
    kind = event.kind
    p = event.payload
    if kind == "debate_started":
        console.print(Panel(f"[bold]{p.get('motion', '')}[/bold]", title="DEBATE STARTED"))
    elif kind == "round_changed":
        console.print(f"\n[dim]--- Round {p.get('round', '?')} ({p.get('kind', '')}) ---[/dim]")
    elif kind == "agent_message":
        agent = p.get("agent", "?")
        color = _COLORS.get(agent, "white")
        name = _NAMES.get(agent, agent)
        arg = p.get("argument", "")
        console.print(f"  [{color} bold]{name}:[/{color} bold] {arg}")
        time.sleep(0.3)
    elif kind == "score_update":
        agent = p.get("agent", "?")
        s = p.get("score", {})
        total = sum(s.get(k, 0) for k in ("logic", "evidence", "persuasion", "counter"))
        console.print(f"  [dim]  Score: {total:.1f}/40[/dim]")
    elif kind == "verdict":
        _print_verdict(p)
    elif kind == "debate_ended":
        console.print(f"\n[bold green]Debate ended. Winner: {p.get('winner', '?')}[/bold green]")


def _print_verdict(p: dict) -> None:
    console.print()
    table = Table(title="FINAL VERDICT", show_header=True)
    table.add_column("", style="bold")
    table.add_column("Messi (A)", justify="center")
    table.add_column("Ronaldo (B)", justify="center")
    table.add_row("Total", f"{p.get('score_a', 0):.1f}", f"{p.get('score_b', 0):.1f}")
    rb = p.get("rubric_breakdown", {})
    for key in ("logic", "evidence", "persuasion", "counter"):
        a_val = rb.get("debater-a", {}).get(key, 0)
        b_val = rb.get("debater-b", {}).get(key, 0)
        table.add_row(key.capitalize(), f"{a_val:.1f}", f"{b_val:.1f}")
    console.print(table)
    console.print(f"\n[italic]{p.get('reasoning', '')}[/italic]")
