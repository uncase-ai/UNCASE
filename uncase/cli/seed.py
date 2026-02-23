"""CLI subcommand for seed operations."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from uncase.schemas.seed import SeedSchema

seed_app = typer.Typer(
    name="seed",
    help="Seed management commands.",
    no_args_is_help=True,
)

console = Console()


@seed_app.command()
def validate(
    file: Path = typer.Argument(..., help="Path to a JSON file with seeds (single or array)."),
) -> None:
    """Validate seeds in a JSON file against SeedSchema v1."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(code=1)

    data = json.loads(file.read_text(encoding="utf-8"))
    seeds_data = data if isinstance(data, list) else [data]

    errors = 0
    for i, seed_data in enumerate(seeds_data):
        seed_id = seed_data.get("seed_id", f"index_{i}")
        try:
            SeedSchema.model_validate(seed_data)
            console.print(f"  [green]OK[/green] {seed_id}")
        except Exception as e:
            console.print(f"  [red]FAIL[/red] {seed_id}: {e}")
            errors += 1

    console.print()
    total = len(seeds_data)
    if errors == 0:
        console.print(f"[green]All {total} seed(s) valid.[/green]")
    else:
        console.print(f"[red]{errors}/{total} seed(s) failed validation.[/red]")
        raise typer.Exit(code=1)


@seed_app.command()
def show(
    file: Path = typer.Argument(..., help="Path to a JSON file with seeds."),
) -> None:
    """Display seeds from a JSON file in a table."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(code=1)

    data = json.loads(file.read_text(encoding="utf-8"))
    seeds_data = data if isinstance(data, list) else [data]

    table = Table(title="Seeds")
    table.add_column("Seed ID", style="cyan")
    table.add_column("Domain")
    table.add_column("Objective")
    table.add_column("Roles")
    table.add_column("Turns")

    for seed_data in seeds_data:
        try:
            seed = SeedSchema.model_validate(seed_data)
            table.add_row(
                seed.seed_id,
                seed.dominio,
                seed.objetivo[:60] + "..." if len(seed.objetivo) > 60 else seed.objetivo,
                ", ".join(seed.roles),
                f"{seed.pasos_turnos.turnos_min}-{seed.pasos_turnos.turnos_max}",
            )
        except Exception as e:
            table.add_row(
                seed_data.get("seed_id", "?"),
                "ERROR",
                str(e)[:60],
                "-",
                "-",
            )

    console.print(table)
