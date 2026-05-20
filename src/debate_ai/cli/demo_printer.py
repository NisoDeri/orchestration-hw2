"""Rich console output for demo debate — prints each turn live."""
from __future__ import annotations

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from debate_ai.models.message_models import UIEvent

console = Console()
_COLORS = {"debater-a": "blue", "debater-b": "red", "judge": "yellow"}
_NAMES = {"debater-a": "Messi (Pro)", "debater-b": "Ronaldo (Con)", "judge": "Judge"}
_ROUND_LABELS = {
    "opening": "OPENING STATEMENTS", "rebuttal": "REBUTTAL",
    "era_swap": "ERA-SWAP ROUND", "closing": "CLOSING STATEMENTS",
}


def demo_subscriber(event: UIEvent) -> None:
    kind, p = event.kind, event.payload
    if kind == "debate_started":
        console.print()
        console.print(Panel(
            f"[bold white]{p.get('motion', '')}[/bold white]\n\n"
            "[dim]Judge scores PERSUASION, not factual correctness.\n"
            "Topology: Child -> Father -> Child (all messages routed through Judge)[/dim]",
            title="DEBATE STARTED", border_style="green",
        ))
    elif kind == "round_changed":
        rnd = p.get("round", "?")
        label = _ROUND_LABELS.get(p.get("kind", ""), p.get("kind", ""))
        console.print(f"\n{'='*60}")
        console.print(f"[bold yellow]  Round {rnd} — {label}[/bold yellow]")
        console.print(f"{'='*60}")
    elif kind == "agent_message":
        _print_turn(p)
    elif kind == "score_update":
        _print_score(p)
    elif kind == "verdict":
        _print_verdict(p)
    elif kind == "debate_ended":
        console.print(f"\n[bold green]Debate ended. Winner: {_NAMES.get(p.get('winner'), p.get('winner'))}[/bold green]")


def _print_turn(p: dict) -> None:
    agent = p.get("agent", "?")
    color = _COLORS.get(agent, "white")
    name = _NAMES.get(agent, agent)
    arg = p.get("argument", "")
    console.print(f"\n  [{color} bold]{name}:[/{color} bold]")
    console.print(f"  {arg}")
    time.sleep(0.4)


def _print_score(p: dict) -> None:
    agent = p.get("agent", "?")
    s = p.get("score", {})
    name = _NAMES.get(agent, agent)
    parts = [f"{k.capitalize()}: {s.get(k, 0):.1f}" for k in ("logic", "evidence", "persuasion", "counter")]
    total = sum(s.get(k, 0) for k in ("logic", "evidence", "persuasion", "counter"))
    console.print(f"  [dim]  Judge scores {name}: {' | '.join(parts)} = {total:.1f}/40[/dim]")


def _print_verdict(p: dict) -> None:
    console.print(f"\n{'='*60}")
    table = Table(title="FINAL VERDICT", show_header=True, border_style="green")
    table.add_column("Category", style="bold")
    table.add_column("Messi (A)", justify="center", style="blue")
    table.add_column("Ronaldo (B)", justify="center", style="red")
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{p.get('score_a', 0):.1f}[/bold]",
                  f"[bold]{p.get('score_b', 0):.1f}[/bold]")
    rb = p.get("rubric_breakdown", {})
    for key in ("logic", "evidence", "persuasion", "counter"):
        a_val = rb.get("debater-a", {}).get(key, 0)
        b_val = rb.get("debater-b", {}).get(key, 0)
        marker_a = "[bold green]" if a_val > b_val else ""
        marker_b = "[bold green]" if b_val > a_val else ""
        table.add_row(key.capitalize(),
                      f"{marker_a}{a_val:.1f}", f"{marker_b}{b_val:.1f}")
    console.print(table)
    console.print(f"\n[italic]{p.get('reasoning', '')}[/italic]")
