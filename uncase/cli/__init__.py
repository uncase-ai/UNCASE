"""UNCASE CLI — Command-line interface."""

from __future__ import annotations

import typer

from uncase._version import __version__
from uncase.cli.seed import seed_app

app = typer.Typer(
    name="uncase",
    help="UNCASE — Framework for high-quality synthetic conversational data.",
    no_args_is_help=True,
    add_completion=False,
)

# Register subcommands
app.add_typer(seed_app, name="seed")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"uncase {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show UNCASE version.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """UNCASE — Unbiased Neutral Convention for Agnostic Seed Engineering."""
