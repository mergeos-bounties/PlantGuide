from __future__ import annotations

from plantguide.data.loader import get_species_by_id


def care_card_for_species(species_id: str) -> dict:
    species = get_species_by_id(species_id)
    if species is None:
        raise KeyError(f"unknown species {species_id!r}")
    care = dict(species.get("care") or {})
    return {
        "species_id": species.get("id"),
        "common_name": species.get("common_name"),
        "scientific_name": species.get("scientific_name"),
        "summary": care.get("summary")
        or f"General care tips for {species.get('common_name')}.",
        "light": care.get("light", "Bright indirect light"),
        "water": care.get("water", "Water when the top soil is dry"),
        "soil": care.get("soil", "Well-draining potting mix"),
        "humidity": care.get("humidity", "Average household humidity"),
        "temperature_c": care.get("temperature_c", "18-27"),
        "fertilizer": care.get("fertilizer", "Balanced fertilizer monthly in growing season"),
        "toxicity": care.get("toxicity", "Unknown — keep away from pets if unsure"),
        "common_issues": care.get("common_issues") or [],
        "tips": care.get("tips") or [],
    }


def watering_hint(species_id: str, season: str = "summer") -> dict:
    card = care_card_for_species(species_id)
    season_key = season.strip().lower()
    base = str(card.get("water") or "")
    extra = {
        "summer": "Check soil more often; heat increases evaporation.",
        "winter": "Reduce frequency; plants grow slower in cool months.",
        "rainy": "Ensure drainage; avoid waterlogged roots.",
    }.get(season_key, "Adjust to your climate and pot size.")
    return {
        "species_id": card["species_id"],
        "season": season_key,
        "water": base,
        "seasonal_note": extra,
    }
