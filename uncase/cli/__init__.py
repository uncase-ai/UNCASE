"""UNCASE CLI — Interfaz de línea de comandos."""

from __future__ import annotations

import typer

from uncase._version import __version__

app = typer.Typer(
    name="uncase",
    help="UNCASE — Framework para datos conversacionales sintéticos de alta calidad.",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Muestra la versión y termina."""
    if value:
        typer.echo(f"uncase {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Mostrar versión de UNCASE.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """UNCASE — Unbiased Neutral Convention for Agnostic Seed Engineering."""
