"""CLI entry point — thin Typer shell over the SDK."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

app = typer.Typer(help="Messi vs Ronaldo debate — settled by Claude.")
console = Console()


@app.callback(invoke_without_command=True)
def _menu(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    from debate_ai.cli.menu import interactive_menu
    interactive_menu()


@app.command()
def run(
    config_dir: Annotated[Path | None, typer.Option("--config", help="Config directory")] = None,
) -> None:
    """Run a single debate and print the result."""
    from debate_ai.sdk.sdk import run_debate
    console.print("[bold]Starting Messi vs Ronaldo debate…[/bold]")
    _print_result(run_debate(config_dir=config_dir))


@app.command()
def demo() -> None:
    """Run a demo debate with pre-scripted agents (no API key needed)."""
    from debate_ai.sdk.sdk import run_demo
    console.print("[bold]Running demo debate (pre-scripted, no API key)…[/bold]\n")
    _print_result(run_demo())


@app.command()
def start(
    host: Annotated[str, typer.Option(help="Bind address")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port number")] = 8000,
) -> None:
    """Launch the HTML chat UI (FastAPI + SSE)."""
    from debate_ai.ui.server import launch
    launch(host=host, port=port)


@app.command()
def config() -> None:
    """Show current config summary."""
    from debate_ai.sdk.sdk import get_config
    cfg = get_config()
    console.print(f"Motion: {cfg['motion']}")
    console.print(f"Pings per side: {cfg['pings_per_side']}")
    console.print(f"Era-swap round: {cfg['era_swap_round']}")
    console.print(f"Personas: {', '.join(cfg['personas'])}")


def _print_result(result: Any) -> None:
    v = result.verdict
    console.print(f"\n[bold green]Winner: {v.winner}[/bold green]")
    console.print(f"Score: {v.score_a:.1f} – {v.score_b:.1f}")
    console.print(f"Reasoning: {v.reasoning}")
    console.print(f"Turns: {result.turn_count}  Cost: ${result.cost_usd:.4f}")
