"""Offline catalog filters built from normalized care-card fields."""

from __future__ import annotations

from collections.abc import Iterable


def filter_species_by_care(
    species: Iterable[dict], *, light: str | None = None, water: str | None = None
) -> list[dict]:
    """Return species whose light and water guidance contains every requested term."""
    light_query = (light or "").strip().lower()
    water_query = (water or "").strip().lower()

    if not light_query and not water_query:
        raise ValueError("provide --light, --water, or both")

    matches: list[dict] = []
    for item in species:
        care = item.get("care") or {}
        light_text = str(care.get("light") or "").lower()
        water_text = str(care.get("water") or "").lower()
        if light_query and light_query not in light_text:
            continue
        if water_query and water_query not in water_text:
            continue
        matches.append(item)
    return matches
