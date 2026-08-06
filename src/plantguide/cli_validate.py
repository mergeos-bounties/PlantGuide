"""CLI commands for catalog / sample validation."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from plantguide.data.loader import list_sample_files, list_species_files, load_json
from plantguide.schemas import validate_sample, validate_species

console = Console()
validate_app = typer.Typer(help="Validate species catalog and observation samples")


@validate_app.command("species")
def validate_species_cmd(
    directory: Path | None = typer.Option(
        None, "--dir", "-d", exists=True, file_okay=False, help="Species directory (default: data/species)"
    ),
) -> None:
    """Validate every JSON file in the species catalog against the Pydantic schema."""
    files = list_species_files(directory)
    if not files:
        console.print("[yellow]No species files found.[/yellow]")
        raise typer.Exit(code=1)

    ok = 0
    errors: list[tuple[str, str]] = []
    for path in files:
        try:
            raw = load_json(path)
            validate_species(raw)
            ok += 1
        except Exception as exc:
            errors.append((path.name, str(exc)))

    console.print(f"[bold]Species validated:[/bold] {ok}/{len(files)}")
    if errors:
        console.print("[red]Errors:[/red]")
        for name, msg in errors:
            console.print(f"  [red]{name}[/red]: {msg}")
        raise typer.Exit(code=1)
    console.print("[green]All species valid ✓[/green]")


@validate_app.command("samples")
def validate_samples_cmd(
    directory: Path | None = typer.Option(
        None, "--dir", "-d", exists=True, file_okay=False, help="Samples directory (default: data/samples)"
    ),
) -> None:
    """Validate every JSON file in the sample directory against the Pydantic schema."""
    files = list_sample_files(directory)
    if not files:
        console.print("[yellow]No sample files found.[/yellow]")
        raise typer.Exit(code=1)

    ok = 0
    errors: list[tuple[str, str]] = []
    for path in files:
        try:
            raw = load_json(path)
            validate_sample(raw)
            ok += 1
        except Exception as exc:
            errors.append((path.name, str(exc)))

    console.print(f"[bold]Samples validated:[/bold] {ok}/{len(files)}")
    if errors:
        console.print("[red]Errors:[/red]")
        for name, msg in errors:
            console.print(f"  [red]{name}[/red]: {msg}")
        raise typer.Exit(code=1)
    console.print("[green]All samples valid ✓[/green]")


@validate_app.command("all")
def validate_all_cmd() -> None:
    """Validate both species catalog and all observation samples."""
    import sys

    # Save original argv and simulate sub-commands
    try:
        validate_species_cmd()
    except typer.Exit as e:
        if e.exit_code != 0:
            console.print("[red]Species validation failed — stopping.[/red]")
            raise

    console.print()
    try:
        validate_samples_cmd()
    except typer.Exit as e:
        if e.exit_code != 0:
            console.print("[red]Sample validation failed.[/red]")
            raise
