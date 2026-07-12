"""Local JSON store for a user plant collection.

Each plant record:
    {
        "id": "PlantGuide#<n>",  # unique, sequential
        "species": "aloe_vera",
        "nickname": "Desk Aloe",        # optional
        "added_at": "2026-07-12",
        "last_watered": "2026-07-12",
        "water_every_days": 14,
        "note": "..."                   # optional
    }

The collection lives under ``data/collection/plants.json`` (overridable via the
``PLANTGUIDE_COLLECTION_DIR`` environment variable). No network, no ROS, no
runtime deps beyond the standard library.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


def _collection_dir() -> Path:
    raw = os.getenv("PLANTGUIDE_COLLECTION_DIR")
    if raw:
        path = Path(raw)
    else:
        path = Path(__file__).resolve().parents[2] / "data" / "collection"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _store_path() -> Path:
    return _collection_dir() / "plants.json"


def _today() -> date:
    return date.today()


def _parse(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _load() -> list[dict[str, Any]]:
    p = _store_path()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save(records: list[dict[str, Any]]) -> None:
    _store_path().write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _next_id(records: list[dict[str, Any]]) -> str:
    max_n = 0
    for r in records:
        m = re.match(r"PlantGuide#(\d+)", str(r.get("id", "")))
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"PlantGuide#{max_n + 1}"


def add_plant(
    species: str,
    water_every_days: int,
    nickname: str | None = None,
    last_watered: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Add a plant to the collection and return the created record."""
    if water_every_days <= 0:
        raise ValueError("water_every_days must be positive")
    today = _today()
    records = _load()
    rec: dict[str, Any] = {
        "id": _next_id(records),
        "species": species,
        "added_at": _fmt(today),
        "last_watered": last_watered or _fmt(today),
        "water_every_days": water_every_days,
    }
    if nickname:
        rec["nickname"] = nickname
    if note:
        rec["note"] = note
    records.append(rec)
    _save(records)
    return rec


def list_plants() -> list[dict[str, Any]]:
    """Return all plants in the collection (oldest first)."""
    return _load()


def water_plant(plant_id: str, on_date: str | None = None) -> dict[str, Any]:
    """Mark a plant as watered; returns the updated record or raises KeyError."""
    records = _load()
    for r in records:
        if r.get("id") == plant_id:
            r["last_watered"] = on_date or _fmt(_today())
            _save(records)
            return r
    raise KeyError(f"plant id not found: {plant_id}")


def due_soon(
    within_days: int = 3, as_of: str | None = None
) -> list[dict[str, Any]]:
    """Return plants whose next watering is due within ``within_days`` (inclusive)."""
    if within_days < 0:
        raise ValueError("within_days must be >= 0")
    today = _parse(as_of) if as_of else _today()
    out: list[dict[str, Any]] = []
    for r in _load():
        try:
            last = _parse(r["last_watered"])
            every = int(r["water_every_days"])
        except (KeyError, ValueError):
            continue
        due = last + timedelta(days=every)
        days_left = (due - today).days
        if days_left <= within_days:
            enriched = dict(r)
            enriched["due_date"] = _fmt(due)
            enriched["days_left"] = days_left
            out.append(enriched)
    out.sort(key=lambda x: x["days_left"])
    return out


def next_watering(plant: dict[str, Any], as_of: str | None = None) -> date:
    """Compute the next due date for a plant record."""
    last = _parse(plant["last_watered"])
    every = int(plant["water_every_days"])
    return last + timedelta(days=every)
