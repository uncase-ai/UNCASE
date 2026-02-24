"""CLI subcommand for tool management operations."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from uncase.tools import get_registry, get_tool, list_tools
from uncase.tools.schemas import ToolDefinition

tool_app = typer.Typer(
    name="tool",
    help="Tool management commands.",
    no_args_is_help=True,
)

console = Console()


def _ensure_builtins_loaded() -> None:
    """Ensure built-in tools are registered."""
    with contextlib.suppress(ImportError):
        import uncase.tools._builtin  # noqa: F401


@tool_app.command("list")
def list_cmd(
    domain: str = typer.Option(None, "--domain", help="Filter tools by domain namespace."),
    category: str = typer.Option(None, "--category", help="Filter tools by category."),
) -> None:
    """List registered tools."""
    _ensure_builtins_loaded()
    registry = get_registry()

    # Get all tool names, then filter.
    names = list_tools()
    if not names:
        console.print("[yellow]No tools registered.[/yellow]")
        raise typer.Exit(code=1)

    tools: list[ToolDefinition] = []
    if domain:
        tools = registry.list_by_domain(domain)
    elif category:
        tools = registry.list_by_category(category)
    else:
        tools = [registry.get(name) for name in names]

    if not tools:
        console.print("[yellow]No tools match the given filters.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Registered Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Category")
    table.add_column("Domains")
    table.add_column("Auth")
    table.add_column("Mode")

    for tool in sorted(tools, key=lambda t: t.name):
        auth = "[green]Yes[/green]" if tool.requires_auth else "[dim]No[/dim]"
        domains = ", ".join(tool.domains) if tool.domains else "-"
        table.add_row(tool.name, tool.category or "-", domains, auth, tool.execution_mode)

    console.print(table)


@tool_app.command()
def show(
    name: str = typer.Argument(..., help="Tool name to display."),
) -> None:
    """Show detailed tool definition."""
    _ensure_builtins_loaded()

    try:
        tool = get_tool(name)
    except Exception as e:
        console.print(f"[red]Tool not found: {e}[/red]")
        raise typer.Exit(code=1) from None

    console.print(Panel(f"[bold cyan]{tool.name}[/bold cyan] (v{tool.version})", title="Tool Definition"))
    console.print(f"[bold]Description:[/bold] {tool.description}")
    console.print(f"[bold]Category:[/bold] {tool.category or '-'}")
    console.print(f"[bold]Domains:[/bold] {', '.join(tool.domains) if tool.domains else '-'}")
    console.print(f"[bold]Auth required:[/bold] {tool.requires_auth}")
    console.print(f"[bold]Execution mode:[/bold] {tool.execution_mode}")

    console.print("\n[bold]Input schema:[/bold]")
    console.print(json.dumps(tool.input_schema, indent=2, ensure_ascii=False))

    if tool.output_schema:
        console.print("\n[bold]Output schema:[/bold]")
        console.print(json.dumps(tool.output_schema, indent=2, ensure_ascii=False))

    if tool.metadata:
        console.print("\n[bold]Metadata:[/bold]")
        console.print(json.dumps(tool.metadata, indent=2, ensure_ascii=False))


@tool_app.command()
def validate(
    file: Path = typer.Argument(..., help="Path to JSON file with a tool definition."),
) -> None:
    """Validate a tool definition JSON file."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(code=1)

    data = json.loads(file.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else [data]

    errors = 0
    for i, item in enumerate(items):
        name = item.get("name", f"index_{i}")
        try:
            ToolDefinition.model_validate(item)
            console.print(f"  [green]OK[/green] {name}")
        except Exception as e:
            console.print(f"  [red]FAIL[/red] {name}: {e}")
            errors += 1

    console.print()
    total = len(items)
    if errors == 0:
        console.print(f"[green]All {total} tool definition(s) valid.[/green]")
    else:
        console.print(f"[red]{errors}/{total} tool definition(s) failed validation.[/red]")
        raise typer.Exit(code=1)
