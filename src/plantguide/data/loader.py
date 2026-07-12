from __future__ import annotations

import json
from pathlib import Path

from plantguide.config import SAMPLES_DIR, SPECIES_DIR


def list_species_files(directory: Path | None = None) -> list[Path]:
    root = directory or SPECIES_DIR
    if not root.exists():
        return []
    return sorted(root.glob("*.json"))


def list_sample_files(directory: Path | None = None) -> list[Path]:
    root = directory or SAMPLES_DIR
    if not root.exists():
        return []
    return sorted(root.glob("*.json"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_species(path: Path) -> dict:
    payload = load_json(path)
    payload.setdefault("id", path.stem)
    payload.setdefault("common_name", path.stem.replace("_", " ").title())
    payload.setdefault("scientific_name", payload.get("id", "").replace("_", " ").title())
    payload.setdefault("tags", [])
    payload.setdefault("care", {})
    return payload


def load_sample(path: Path) -> dict:
    payload = load_json(path)
    payload.setdefault("id", path.stem)
    payload.setdefault("tags", [])
    payload.setdefault("expected_species", None)
    return payload


def load_species_catalog() -> list[dict]:
    return [load_species(p) for p in list_species_files()]


def get_species_by_id(species_id: str) -> dict | None:
    key = species_id.strip().lower().replace(" ", "_")
    for species in load_species_catalog():
        sid = str(species.get("id", "")).lower()
        if sid == key:
            return species
        if str(species.get("common_name", "")).lower().replace(" ", "_") == key:
            return species
    return None
