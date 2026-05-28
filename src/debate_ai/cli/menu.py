"""Interactive terminal menu for the debate CLI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

_MENU = """
[bold cyan]Messi vs Ronaldo Debate Engine[/bold cyan]

  [1] Run a debate          (requires ANTHROPIC_API_KEY)
  [2] Run demo              (pre-scripted, no API key needed)
  [3] Show config
  [4] List personas
  [5] Launch web UI
  [0] Exit
"""


def interactive_menu() -> None:
    console.print(Panel(_MENU.strip(), title="debate-ai", border_style="blue"))
    while True:
        choice = Prompt.ask("[bold]Choose[/bold]", choices=["0", "1", "2", "3", "4", "5"])
        if choice == "0":
            console.print("[dim]Goodbye.[/dim]")
            break
        _dispatch(choice)


def _dispatch(choice: str) -> None:
    if choice == "1":
        _run_debate()
    elif choice == "2":
        _run_demo()
    elif choice == "3":
        _show_config()
    elif choice == "4":
        _list_personas()
    elif choice == "5":
        _launch_ui()


def _run_debate() -> None:
    from debate_ai.sdk.sdk import run_debate

    console.print("[bold]Running debate…[/bold]")
    try:
        result = run_debate()
        console.print(f"\n[bold green]Winner: {result.verdict.winner}[/bold green]")
        console.print(f"Score: {result.verdict.score_a:.1f} – {result.verdict.score_b:.1f}")
        console.print(f"Reasoning: {result.verdict.reasoning}")
        console.print(f"Cost: ${result.cost_usd:.4f}")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Error:[/bold red] {exc}")


def _run_demo() -> None:
    from debate_ai.sdk.sdk import run_demo

    console.print("[bold]Running demo debate (pre-scripted)…[/bold]\n")
    try:
        result = run_demo()
        console.print(f"\nScore: {result.verdict.score_a:.1f} – {result.verdict.score_b:.1f}")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Error:[/bold red] {exc}")


def _show_config() -> None:
    from debate_ai.sdk.sdk import get_config

    cfg = get_config()
    console.print(f"Motion: {cfg['motion']}")
    console.print(f"Pings per side: {cfg['pings_per_side']}")
    console.print(f"Era-swap round: {cfg['era_swap_round']}")


def _list_personas() -> None:
    from debate_ai.sdk.sdk import list_personas

    for name in list_personas():
        console.print(f"  • {name}")


def _launch_ui() -> None:
    from debate_ai.ui.server import launch

    launch()
