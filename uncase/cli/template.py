"""CLI subcommand for template operations."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.syntax import Syntax
from rich.table import Table

from uncase.schemas.conversation import Conversation
from uncase.templates import get_template, list_templates, register_all_templates

template_app = typer.Typer(
    name="template",
    help="Chat template commands.",
    no_args_is_help=True,
)

console = Console()


@template_app.command("list")
def list_cmd() -> None:
    """List all available template formats."""
    register_all_templates()
    names = list_templates()

    if not names:
        console.print("[yellow]No templates registered.[/yellow]")
        raise typer.Exit

    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name")
    table.add_column("Tool Support")
    table.add_column("Special Tokens")

    for name in names:
        tmpl = get_template(name)
        tool_support = "[green]Yes[/green]" if tmpl.supports_tool_calls else "[dim]No[/dim]"
        tokens = escape(", ".join(tmpl.get_special_tokens())) or "-"
        table.add_row(name, tmpl.display_name, tool_support, tokens)

    console.print(table)


@template_app.command()
def export(
    input: Path = typer.Argument(..., help="Path to JSON file with conversations."),  # noqa: A002
    template: str = typer.Argument(..., help="Template name to use for rendering."),
    output: Path = typer.Option(None, "-o", "--output", help="Output file path. Prints to stdout if omitted."),
) -> None:
    """Export conversations from a JSON file using a template."""
    if not input.exists():
        console.print(f"[red]File not found: {input}[/red]")
        raise typer.Exit(code=1)

    register_all_templates()

    try:
        tmpl = get_template(template)
    except Exception as e:
        console.print(f"[red]Template error: {e}[/red]")
        raise typer.Exit(code=1) from None

    data = json.loads(input.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else [data]

    conversations: list[Conversation] = []
    for i, item in enumerate(items):
        try:
            conversations.append(Conversation.model_validate(item))
        except Exception as e:
            console.print(f"[red]Validation error at index {i}: {e}[/red]")
            raise typer.Exit(code=1) from None

    rendered = tmpl.render_batch(conversations)
    result = "\n".join(rendered)

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]Exported {len(conversations)} conversation(s) to {output}[/green]")
    else:
        console.print(result)


@template_app.command()
def preview(
    input: Path = typer.Argument(..., help="Path to JSON file with conversations."),  # noqa: A002
    template: str = typer.Argument(..., help="Template name to use for rendering."),
) -> None:
    """Preview rendering of the first conversation."""
    if not input.exists():
        console.print(f"[red]File not found: {input}[/red]")
        raise typer.Exit(code=1)

    register_all_templates()

    try:
        tmpl = get_template(template)
    except Exception as e:
        console.print(f"[red]Template error: {e}[/red]")
        raise typer.Exit(code=1) from None

    data = json.loads(input.read_text(encoding="utf-8"))
    first = data[0] if isinstance(data, list) else data

    try:
        conversation = Conversation.model_validate(first)
    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(code=1) from None

    rendered = tmpl.render(conversation)
    syntax = Syntax(rendered, "text", theme="monokai", word_wrap=True)
    console.print(syntax)
