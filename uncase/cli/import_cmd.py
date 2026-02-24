"""CLI subcommand for data import operations."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from uncase.core.parser import CSVConversationParser, JSONLConversationParser

import_app = typer.Typer(
    name="import",
    help="Data import commands.",
    no_args_is_help=True,
)

console = Console()


@import_app.command()
def csv(
    file: Path = typer.Argument(..., help="Path to CSV file with conversations."),
    domain: str = typer.Option(None, "--domain", help="Override domain on imported conversations."),
    seed_id: str = typer.Option(None, "--seed-id", help="Override seed ID on imported conversations."),
    output: Path = typer.Option(None, "-o", "--output", help="Output JSON file path. Prints to stdout if omitted."),
) -> None:
    """Import conversations from a CSV file."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(code=1)

    parser = CSVConversationParser()
    try:
        conversations = asyncio.run(parser.parse_file(file))
    except Exception as e:
        console.print(f"[red]CSV parse error: {e}[/red]")
        raise typer.Exit(code=1) from None

    # Apply optional overrides.
    for conv in conversations:
        if domain:
            conv.dominio = domain
        if seed_id:
            conv.seed_id = seed_id

    result = json.dumps(
        [conv.model_dump(mode="json") for conv in conversations],
        ensure_ascii=False,
        indent=2,
    )

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]Imported {len(conversations)} conversation(s) to {output}[/green]")
    else:
        console.print(result)

    console.print(
        Panel(
            f"Conversations imported: [bold]{len(conversations)}[/bold]  |  Source: [cyan]{file.name}[/cyan]",
            title="Import Summary",
        )
    )


@import_app.command()
def jsonl(
    file: Path = typer.Argument(..., help="Path to JSONL file with conversations."),
    format: str = typer.Option("auto", "--format", "-f", help="Source format: auto, openai, sharegpt, uncase."),  # noqa: A002
    output: Path = typer.Option(None, "-o", "--output", help="Output JSON file path. Prints to stdout if omitted."),
) -> None:
    """Import conversations from a JSONL file."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(code=1)

    parser = JSONLConversationParser()
    try:
        conversations = asyncio.run(parser.parse_file(file, source_format=format))
    except Exception as e:
        console.print(f"[red]JSONL parse error: {e}[/red]")
        raise typer.Exit(code=1) from None

    result = json.dumps(
        [conv.model_dump(mode="json") for conv in conversations],
        ensure_ascii=False,
        indent=2,
    )

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]Imported {len(conversations)} conversation(s) to {output}[/green]")
    else:
        console.print(result)

    console.print(
        Panel(
            f"Conversations imported: [bold]{len(conversations)}[/bold]  |  "
            f"Source: [cyan]{file.name}[/cyan]  |  "
            f"Format: [cyan]{format}[/cyan]",
            title="Import Summary",
        )
    )
