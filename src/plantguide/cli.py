from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from plantguide import __version__
from plantguide.care.cards import care_card_for_species, watering_hint
from plantguide.collection import add_plant, due_soon, list_plants
from plantguide.data.loader import list_species_files, load_species
from plantguide.identify.pipeline import identify_from_sample, identify_from_tags
from plantguide.integrations.sdk import care_report_from_sample, care_report_from_tags
from plantguide.train.toy_train import train_toy

app = typer.Typer(
    help="PlantGuide — plant identification and species care guidance.",
    no_args_is_help=True,
)
species_app = typer.Typer(help="Species catalog")
identify_app = typer.Typer(help="Identify plants from traits/tags")
care_app = typer.Typer(help="Care guidance")
app_app = typer.Typer(help="App embedding demos")
train_app = typer.Typer(help="Training / calibration")
app.add_typer(species_app, name="species")
app.add_typer(identify_app, name="identify")
app.add_typer(care_app, name="care")
app.add_typer(app_app, name="app")
app.add_typer(train_app, name="train")
collection_app = typer.Typer(help="User plant collection")
app.add_typer(collection_app, name="collection")
console = Console()


@app.command("version")
def version_cmd() -> None:
    console.print(f"PlantGuide {__version__}")
    console.print(f"Species in catalog: {len(list_species_files())}")


@species_app.command("list")
def species_list() -> None:
    files = list_species_files()
    if not files:
        console.print("[yellow]No species in data/species[/yellow]")
        raise typer.Exit()
    table = Table(title=f"Species ({len(files)})")
    table.add_column("ID")
    table.add_column("Common name")
    table.add_column("Tags")
    for path in files:
        sp = load_species(path)
        tags = ", ".join((sp.get("tags") or [])[:5])
        table.add_row(str(sp.get("id")), str(sp.get("common_name")), tags)
    console.print(table)


@identify_app.command("tags")
def identify_tags(
    tags: str = typer.Option(..., "--tags", "-t", help="Comma-separated traits"),
    top: int = typer.Option(3, "--top", "-k", min=1, max=20),
) -> None:
    console.print_json(data=identify_from_tags(tags, top_k=top))


@identify_app.command("sample")
def identify_sample(
    file: Path = typer.Option(..., "--file", "-f", exists=True, dir_okay=False),
    top: int = typer.Option(3, "--top", "-k", min=1, max=20),
) -> None:
    console.print_json(data=identify_from_sample(file, top_k=top))


@care_app.command("show")
def care_show(species: str = typer.Option(..., "--species", "-s")) -> None:
    try:
        console.print_json(data=care_card_for_species(species))
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@care_app.command("water")
def care_water(
    species: str = typer.Option(..., "--species", "-s"),
    season: str = typer.Option("summer", "--season"),
) -> None:
    try:
        console.print_json(data=watering_hint(species, season=season))
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@care_app.command("svg")
def care_svg(
    species: str = typer.Option(..., "--species", "-s"),
    out: Path | None = typer.Option(None, "--out", "-o"),
) -> None:
    """Export a simple SVG care card."""
    from plantguide.care.export_svg import write_care_svg
    from plantguide.config import OUT_DIR

    try:
        path = out or (OUT_DIR / f"{species}-care.svg")
        write_care_svg(species, path)
        console.print(f"[green]SVG[/green] {path}")
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@app_app.command("demo")
def app_demo(
    sample: Path | None = typer.Option(
        None,
        "--sample",
        exists=True,
        dir_okay=False,
        help="Observation JSON fixture to turn into an app care report.",
    ),
    tags: str | None = typer.Option(
        None,
        "--tags",
        "-t",
        help="Comma-separated observation tags to turn into an app care report.",
    ),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write report JSON here."),
    top: int = typer.Option(3, "--top", "-k", min=1, max=20),
) -> None:
    """Generate the documented app care-report JSON from sample data or tags."""
    if bool(sample) == bool(tags):
        console.print("[red]Provide exactly one of --sample or --tags.[/red]")
        raise typer.Exit(code=1)

    report = (
        care_report_from_sample(sample, top_k=top)
        if sample is not None
        else care_report_from_tags(tags or "", top_k=top)
    )
    if out is None:
        console.print_json(data=report)
        return

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Care report[/green] {out}")


@identify_app.command("disease")
def identify_disease(
    symptoms: str = typer.Option(..., "--symptoms", "-s", help="e.g. yellow,rot,droop"),
    top: int = typer.Option(5, "--top", "-k", min=1, max=20),
) -> None:
    """Match symptom tags against species common issues."""
    from plantguide.identify.disease import match_diseases

    console.print_json(data=match_diseases(symptoms, top_k=top))


@train_app.command("toy")
def train_toy_cmd(epochs: int = typer.Option(3, "--epochs", "-e", min=1, max=50)) -> None:
    report = train_toy(epochs=epochs)
    last = report["history"][-1]["top1_hit_rate"]
    console.print(f"[green]Calibration complete[/green] top1_hit_rate={last}")
    console.print(f"Report: {report['report_path']}")


@train_app.command("report")
def train_report() -> None:
    path = Path("data/runs/toy_train_report.json")
    if not path.exists():
        console.print("[yellow]No report yet. Run: plantguide train toy[/yellow]")
        raise typer.Exit(code=1)
    console.print(path.read_text(encoding="utf-8"))


@collection_app.command("add")
def collection_add(
    species: str = typer.Option(..., "--species", "-s"),
    water_every_days: int = typer.Option(14, "--every", "-e", min=1),
    nickname: str | None = typer.Option(None, "--nickname", "-n"),
    last_watered: str | None = None,
    note: str | None = None,
) -> None:
    """Add a plant to your collection."""
    try:
        rec = add_plant(
            species,
            water_every_days,
            nickname=nickname,
            last_watered=last_watered,
            note=note,
        )
        console.print(f"[green]Added[/green] {rec['id']} ({species})")
        console.print(f"  Water every {rec['water_every_days']} days")
        if rec.get("nickname"):
            console.print(f"  Nickname: {rec['nickname']}")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1) from e


@collection_app.command("list")
def collection_list() -> None:
    """List all plants in your collection."""
    plants = list_plants()
    if not plants:
        console.print("[yellow]No plants in collection. Run: plantguide collection add[/yellow]")
        raise typer.Exit()
    table = Table(title="Your Plants")
    table.add_column("ID")
    table.add_column("Species")
    table.add_column("Nickname")
    table.add_column("Added")
    table.add_column("Last Watered")
    table.add_column("Due")
    for p in plants:
        table.add_row(
            p.get("id", ""),
            p.get("species", ""),
            p.get("nickname", "") or "-",
            p.get("added_at", ""),
            p.get("last_watered", ""),
            _due_str(p),
        )
    console.print(table)


@collection_app.command("due")
def collection_due(
    within_days: int = typer.Option(7, "--days", "-d", min=0, max=30),
) -> None:
    """Show plants due for watering within N days."""
    plants = due_soon(within_days=within_days)
    if not plants:
        console.print("[green]All caught up — no plants due![/green]")
        raise typer.Exit()
    table = Table(title=f"Due within {within_days} days")
    table.add_column("ID")
    table.add_column("Species")
    table.add_column("Days Left")
    table.add_column("Due Date")
    table.add_column("Nickname")
    for p in plants:
        table.add_row(
            p["id"],
            p["species"],
            str(p["days_left"]),
            p["due_date"],
            p.get("nickname", "") or "-",
        )
    console.print(table)


def _due_str(plant: dict[str, Any]) -> str:
    from plantguide.collection.store import next_watering

    due = next_watering(plant)
    today = date.today()
    days_left = (due - today).days
    if days_left < 0:
        return f"[red]{-days_left}d late[/red]"
    if days_left == 0:
        return "[green]today[/green]"
    if days_left == 1:
        return "[yellow]tomorrow[/yellow]"
    return f"{days_left}d"


if __name__ == "__main__":
    app()
