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
from plantguide.identify.pipeline import (
    identify_from_image,
    identify_from_sample,
    identify_from_tags,
)
from plantguide.integrations.sdk import care_report_from_sample, care_report_from_tags
from plantguide.train.toy_train import train_toy

app = typer.Typer(
    help="PlantGuide — photo/tag plant ID + species care guidance.",
    no_args_is_help=True,
)
species_app = typer.Typer(help="Species catalog")
identify_app = typer.Typer(help="Identify plants from photo, tags, or sample JSON")
care_app = typer.Typer(help="Care guidance")
app_app = typer.Typer(help="App embedding demos")
train_app = typer.Typer(help="Training / calibration")
demo_app = typer.Typer(help="End-to-end demos (photo ID + care)")
app.add_typer(species_app, name="species")
app.add_typer(identify_app, name="identify")
app.add_typer(care_app, name="care")
app.add_typer(app_app, name="app")
app.add_typer(train_app, name="train")
app.add_typer(demo_app, name="demo")
collection_app = typer.Typer(help="User plant collection")
app.add_typer(collection_app, name="collection")
console = Console(markup=False)


@app.command("version")
def version_cmd() -> None:
    console.print(f"PlantGuide {__version__}")
    console.print(f"Species in catalog: {len(list_species_files())}")
    from plantguide.identify.vision import list_demo_photos

    photos = list_demo_photos()
    ready = sum(1 for p in photos if p.get("exists"))
    console.print(f"Demo plant photos: {ready}/{len(photos)}")


@app.command("stats")
def stats_cmd() -> None:
    """Catalog inventory: species count, tag histogram (top tags)."""
    from collections import Counter

    tags: Counter[str] = Counter()
    for path in list_species_files():
        sp = load_species(path)
        for t in sp.get("tags") or []:
            tags[str(t).lower()] += 1
    console.print_json(
        data={
            "version": __version__,
            "species": len(list_species_files()),
            "top_tags": tags.most_common(12),
        }
    )


@species_app.command("list")
def species_list(pet_safe: bool | None = typer.Option(None, "--pet-safe/--no-pet-safe", help="Filter by pet safety")) -> None:
    files = list_species_files()
    if not files:
        console.print("[yellow]No species in data/species[/yellow]")
        raise typer.Exit()
    table = Table(title=f"Species ({len(files)})")
    table.add_column("ID")
    table.add_column("Common name")
    table.add_column("Tags")
    table.add_column("Pet safe")
    for path in files:
        sp = load_species(path)
        safe = sp.get("care", {}).get("is_pet_safe")
        if pet_safe is not None and safe != pet_safe:
            continue
        tags = ", ".join((sp.get("tags") or [])[:5])
        safe_str = "[dim]unknown[/dim]" if safe is None else ("[green]yes[/green]" if safe else "[red]no[/red]")
        table.add_row(str(sp.get("id")), str(sp.get("common_name")), tags, safe_str)
    console.print(table)


@species_app.command("search")
def species_search(
    query: str = typer.Argument(..., help="Substring over id/common/scientific/tags"),
    limit: int = typer.Option(15, "--limit", "-n", min=1, max=50),
) -> None:
    """Search species catalog offline."""
    q = query.strip().lower()
    hits = []
    for path in list_species_files():
        sp = load_species(path)
        blob = " ".join(
            [
                str(sp.get("id") or ""),
                str(sp.get("common_name") or ""),
                str(sp.get("scientific_name") or ""),
                " ".join(sp.get("tags") or []),
            ]
        ).lower()
        if q in blob:
            hits.append(sp)
        if len(hits) >= limit:
            break
    table = Table(title=f"Species search: {query} ({len(hits)})")
    table.add_column("ID")
    table.add_column("Common")
    table.add_column("Scientific")
    for sp in hits:
        table.add_row(
            str(sp.get("id")),
            str(sp.get("common_name")),
            str(sp.get("scientific_name") or ""),
        )
    console.print(table)


@species_app.command("care")
def species_care_cmd(
    species_id: str = typer.Argument(..., help="Species id e.g. snake_plant"),
    svg: bool = typer.Option(False, "--svg", help="Also write SVG care card under data/out"),
) -> None:
    """Show care card for one species; optional SVG export."""
    from plantguide.care.export_svg import write_care_svg
    from plantguide.config import OUT_DIR

    card = care_card_for_species(species_id)
    console.print_json(data=card)
    console.print(f"[cyan]water hint[/cyan] {watering_hint(species_id)}")
    if svg:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"care_{species_id}.svg"
        write_care_svg(species_id, path)
        console.print(f"[green]SVG[/green] {path}")


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


@identify_app.command("image")
def identify_image_cmd(
    image: Path = typer.Option(
        ...,
        "--image",
        "-i",
        exists=True,
        dir_okay=False,
        help="Plant photo (JPG/PNG). Demo photos under data/samples/photos/",
    ),
    top: int = typer.Option(3, "--top", "-k", min=1, max=20),
    no_care: bool = typer.Option(False, "--no-care", help="Skip care card in result"),
) -> None:
    """Identify a plant from a photo (offline visual tags + catalog match)."""
    try:
        data = identify_from_image(image, top_k=top, with_care=not no_care)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    # Friendly human summary + full JSON
    matches = data.get("matches") or []
    if matches:
        top_m = matches[0]
        console.print(
            f"[bold green]Top match:[/bold green] {top_m.get('common_name')} "
            f"({top_m.get('species_id')})  score={top_m.get('score')}"
        )
        if data.get("top_care"):
            care = data["top_care"]
            console.print(f"[cyan]Care summary:[/cyan] {care.get('summary')}")
            console.print(f"  light: {care.get('light')}")
            console.print(f"  water: {care.get('water')}")
    console.print_json(data=data)


@demo_app.command("photo")
def demo_photo_cmd(
    image: Path | None = typer.Option(
        None,
        "--image",
        "-i",
        exists=True,
        dir_okay=False,
        help="Optional photo; default uses bundled data/samples/photos/",
    ),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write full report JSON"),
    svg: bool = typer.Option(True, "--svg/--no-svg", help="Also write SVG care card"),
) -> None:
    """End-to-end demo: plant photo → species ID → care + watering (+ SVG)."""
    from plantguide.care.export_svg import write_care_svg
    from plantguide.config import OUT_DIR
    from plantguide.identify.vision import list_demo_photos, photo_care_demo

    try:
        report = photo_care_demo(image, top_k=3)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("[yellow]Generate fixtures:[/yellow] python scripts/generate_demo_photos.py")
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    species_id = report.get("species_id")
    console.print("[bold]PlantGuide photo demo[/bold]")
    console.print(f"  image:   {report.get('image')}")
    console.print(f"  species: {report.get('common_name')} ({species_id})")
    idn = report.get("identify") or {}
    if idn.get("hit_top1") is not None:
        console.print(f"  hit@1:   {idn.get('hit_top1')} (expected {idn.get('expected_species')})")
    care = report.get("care") or {}
    if care:
        console.print(f"  light:   {care.get('light')}")
        console.print(f"  water:   {care.get('water')}")
        console.print(f"  soil:    {care.get('soil')}")
        tips = care.get("tips") or []
        if tips:
            console.print(f"  tip:     {tips[0]}")
    water = report.get("watering") or {}
    if water:
        console.print(f"  season:  {water.get('seasonal_note')}")

    svg_path = None
    if svg and species_id:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        svg_path = OUT_DIR / f"{species_id}-care.svg"
        try:
            write_care_svg(str(species_id), svg_path)
            console.print(f"[green]SVG care card[/green] {svg_path}")
            report["care_svg"] = str(svg_path)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[yellow]SVG skipped:[/yellow] {exc}")

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        console.print(f"[green]Report[/green] {out}")
    else:
        console.print_json(data=report)

    # List other demo photos
    others = [p for p in list_demo_photos() if p.get("exists")]
    if others:
        console.print("[dim]Other demo photos:[/dim] " + ", ".join(p["file"] for p in others))


@demo_app.command("photos")
def demo_photos_list() -> None:
    """List bundled plant photos for the photo-ID demo."""
    from plantguide.identify.vision import list_demo_photos

    photos = list_demo_photos()
    if not photos:
        console.print("[yellow]No photos. Run: python scripts/generate_demo_photos.py[/yellow]")
        raise typer.Exit(code=1)
    table = Table(title="Demo plant photos")
    table.add_column("File")
    table.add_column("Expected species")
    table.add_column("Ready")
    for p in photos:
        table.add_row(
            str(p.get("file")),
            str(p.get("expected_species")),
            "yes" if p.get("exists") else "missing",
        )
    console.print(table)


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


@care_app.command("calendar")
def care_calendar(
    out: Path | None = typer.Option(None, "--out", "-o", help="Output file path"),
    fmt: str = typer.Option("json", "--format", "-f", help="Export format: json or ics"),
    year: int = typer.Option(2026, "--year", "-y", help="Calendar year"),
    collection: bool = typer.Option(
        False, "--collection", "-c", help="Only species in user collection"
    ),
) -> None:
    """Generate a multi-month care calendar (fertilize + repot) for export."""
    from plantguide.care.planner import (
        generate_calendar,
        generate_catalog_calendar,
        export_json,
        export_ics,
    )
    from plantguide.collection import list_plants
    from plantguide.config import OUT_DIR
    from plantguide.data.loader import load_species_catalog, get_species_by_id

    if collection:
        plants = list_plants()
        if not plants:
            console.print("[yellow]No plants in collection. Use --collection or add plants first.[/yellow]")
            raise typer.Exit()
        species_list = []
        for p in plants:
            sp = get_species_by_id(p["species"])
            if sp:
                species_list.append(sp)
            else:
                console.print(f"[yellow]Warning: species {p['species']} not found[/yellow]")
        events = generate_calendar(species_list, year=year)
    else:
        events = generate_catalog_calendar(year=year)

    if not events:
        console.print("[yellow]No care events generated.[/yellow]")
        raise typer.Exit()

    if out is None:
        out = OUT_DIR / f"care_calendar_{year}.{fmt}"

    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "ics":
        export_ics(events, out)
    else:
        export_json(events, out)

    console.print(f"[green]{'ICS' if fmt == 'ics' else 'JSON'} calendar[/green] {out}")
    console.print(f"  Events: {len(events)}, Species: {len(set(e['species_id'] for e in events))}")


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
