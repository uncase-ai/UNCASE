"""CLI subcommand for quality evaluation operations."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.schemas.conversation import Conversation
from uncase.schemas.quality import QUALITY_THRESHOLDS, QualityReport
from uncase.schemas.seed import SeedSchema

evaluate_app = typer.Typer(
    name="evaluate",
    help="Quality evaluation commands.",
    no_args_is_help=True,
)

console = Console()


def _render_report(report: QualityReport) -> None:
    """Render a quality report to the console."""
    status = "[green]PASS[/green]" if report.passed else "[red]FAIL[/red]"

    table = Table(title=f"Quality Report — {report.conversation_id[:16]}…")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status", justify="center")

    for field_name, (threshold, operator, _desc) in QUALITY_THRESHOLDS.items():
        value = getattr(report.metrics, field_name)

        if operator == "=":
            ok = value == threshold
            threshold_str = f"= {threshold:.2f}"
        elif operator == "<":
            ok = value < threshold
            threshold_str = f"< {threshold:.2f}"
        else:
            ok = value >= threshold
            threshold_str = f">= {threshold:.2f}"

        status_str = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
        table.add_row(field_name, f"{value:.4f}", threshold_str, status_str)

    console.print(table)
    console.print(
        Panel(
            f"Composite Score: [bold]{report.composite_score:.4f}[/bold]  |  Result: {status}",
            title="Summary",
        )
    )

    if report.failures:
        console.print("\n[red]Failures:[/red]")
        for failure in report.failures:
            console.print(f"  • {failure}")
    console.print()


@evaluate_app.command()
def run(
    conversations_file: Path = typer.Argument(..., help="JSON file with conversations (single or array)."),
    seeds_file: Path = typer.Argument(..., help="JSON file with seeds (single or array)."),
    output: Path = typer.Option(None, "--output", "-o", help="Write reports to JSON file."),
) -> None:
    """Evaluate conversation(s) against their origin seed(s).

    Pairs conversations and seeds by index. If a single seed is provided,
    it is used for all conversations.
    """
    if not conversations_file.exists():
        console.print(f"[red]File not found: {conversations_file}[/red]")
        raise typer.Exit(code=1)
    if not seeds_file.exists():
        console.print(f"[red]File not found: {seeds_file}[/red]")
        raise typer.Exit(code=1)

    try:
        conv_data = json.loads(conversations_file.read_text(encoding="utf-8"))
        seed_data = json.loads(seeds_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON parse error: {e}[/red]")
        raise typer.Exit(code=1) from None

    conv_list = conv_data if isinstance(conv_data, list) else [conv_data]
    seed_list = seed_data if isinstance(seed_data, list) else [seed_data]

    # If one seed, replicate it for all conversations
    if len(seed_list) == 1 and len(conv_list) > 1:
        seed_list = seed_list * len(conv_list)

    if len(conv_list) != len(seed_list):
        console.print(f"[red]Mismatched counts: {len(conv_list)} conversations vs {len(seed_list)} seeds.[/red]")
        raise typer.Exit(code=1)

    try:
        conversations = [Conversation.model_validate(c) for c in conv_list]
        seeds = [SeedSchema.model_validate(s) for s in seed_list]
    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(code=1) from None

    evaluator = ConversationEvaluator()
    reports: list[QualityReport] = asyncio.run(evaluator.evaluate_batch(conversations, seeds))

    for report in reports:
        _render_report(report)

    # Summary
    passed = sum(1 for r in reports if r.passed)
    failed = len(reports) - passed
    avg_score = sum(r.composite_score for r in reports) / len(reports) if reports else 0.0

    console.print(
        Panel(
            f"Total: {len(reports)}  |  "
            f"Passed: [green]{passed}[/green]  |  "
            f"Failed: [red]{failed}[/red]  |  "
            f"Avg Score: {avg_score:.4f}",
            title="Batch Summary",
        )
    )

    if output:
        output.write_text(
            json.dumps(
                [r.model_dump(mode="json") for r in reports],
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        console.print(f"\n[green]Reports written to {output}[/green]")

    if failed > 0:
        raise typer.Exit(code=1)


@evaluate_app.command()
def thresholds() -> None:
    """Display current quality thresholds and the composite score formula."""
    table = Table(title="Quality Thresholds (SCSF v1)")
    table.add_column("Metric", style="cyan")
    table.add_column("Threshold", justify="right")
    table.add_column("Description")

    for name, (value, operator, desc) in QUALITY_THRESHOLDS.items():
        table.add_row(name, f"{operator} {value:.2f}", desc)

    console.print(table)
    console.print()
    console.print(
        Panel(
            "[bold]Q = min(rouge_l, fidelidad, ttr, coherencia)[/bold]\n"
            "if privacy_score == 0.0 AND memorizacion < 0.01\n"
            "else Q = 0.0",
            title="Composite Score Formula",
        )
    )
