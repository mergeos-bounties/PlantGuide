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


def _set_safety_defaults(care: dict) -> None:
    """Set default safety flags based on toxicity string.

    Mutates the care dict in-place, setting ``is_pet_safe`` based on the
    ``toxicity`` field according to known toxicity strings.
    """
    toxicity = care.get("toxicity", "").strip()

    # If toxicity is empty, set to Unknown and leave is_pet_safe as None
    if not toxicity:
        care["toxicity"] = "Unknown"
        care["is_pet_safe"] = None
        return

    toxic_lower = toxicity.lower()

    # Definitely safe
    if any(
        s in toxic_lower
        for s in (
            "non-toxic to pets",
            "generally considered non-toxic to pets",
            "culinary herb; generally safe when used as food",
            "edible for humans; not a pet food",
            "not a pet food",
            "safe for pets",
            "non-toxic",
            "non-toxic to dogs and cats",
        )
    ):
        care["is_pet_safe"] = True
        return

    # Definitely unsafe
    if any(
        s in toxic_lower
        for s in (
            "toxic if ingested",
            "toxic to pets",
            "toxic to dogs and cats",
            "toxic to cats",
            "toxic to dogs",
            "poisonous",
            "harmful if ingested",
            "toxic",
            "toxic to animals",
        )
    ):
        care["is_pet_safe"] = False
        return

    # Mildly toxic -> treat as unsafe
    if "mildly toxic" in toxic_lower or "slightly toxic" in toxic_lower:
        care["is_pet_safe"] = False
        return

    # Unknown or not specified -> None
    care["is_pet_safe"] = None


def load_species(path: Path) -> dict:
    payload = load_json(path)
    payload.setdefault("id", path.stem)
    payload.setdefault("common_name", path.stem.replace("_", " ").title())
    payload.setdefault(
        "scientific_name", payload.get("id", "").replace("_", " ").title()
    )
    payload.setdefault("tags", [])
    payload.setdefault("care", {})
    _set_safety_defaults(payload["care"])
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