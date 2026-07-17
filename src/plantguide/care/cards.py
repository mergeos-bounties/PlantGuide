from __future__ import annotations

from datetime import date, timedelta

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


_SEASON_FACTORS = {
    "spring": 1.0,
    "summer": 0.8,
    "autumn": 1.2,
    "winter": 1.6,
}
_CLIMATE_FACTORS = {
    "arid": 0.8,
    "temperate": 1.0,
    "humid": 1.25,
}


def watering_schedule(
    species_id: str,
    pot_size_cm: float,
    season: str = "summer",
    climate: str = "temperate",
    as_of: date | None = None,
) -> dict:
    """Calculate three soil-check dates using an intentionally simple offline heuristic."""
    if pot_size_cm <= 0:
        raise ValueError("pot_size_cm must be greater than zero")

    season_key = season.strip().lower()
    climate_key = climate.strip().lower()
    if season_key not in _SEASON_FACTORS:
        raise ValueError(f"season must be one of: {', '.join(_SEASON_FACTORS)}")
    if climate_key not in _CLIMATE_FACTORS:
        raise ValueError(f"climate must be one of: {', '.join(_CLIMATE_FACTORS)}")

    card = care_card_for_species(species_id)
    water_guidance = str(card.get("water") or "")
    guidance_lower = water_guidance.lower()
    base_days = 7
    if any(term in guidance_lower for term in ("very infrequent", "2–4 weeks", "2-4 weeks", "sparse")):
        base_days = 18
    elif any(term in guidance_lower for term in ("fully dry", "dry completely", "soak and dry")):
        base_days = 14
    elif any(term in guidance_lower for term in ("keep evenly moist", "keep moist", "lightly moist")):
        base_days = 4

    if pot_size_cm < 12:
        pot_factor = 0.75
    elif pot_size_cm <= 20:
        pot_factor = 1.0
    elif pot_size_cm <= 30:
        pot_factor = 1.25
    else:
        pot_factor = 1.5

    interval_days = round(
        base_days * pot_factor * _SEASON_FACTORS[season_key] * _CLIMATE_FACTORS[climate_key]
    )
    interval_days = max(2, min(30, interval_days))
    start = as_of or date.today()
    next_checks = [
        (start + timedelta(days=interval_days * step)).isoformat() for step in range(1, 4)
    ]

    return {
        "species_id": card["species_id"],
        "common_name": card["common_name"],
        "pot_size_cm": pot_size_cm,
        "season": season_key,
        "climate": climate_key,
        "water_guidance": water_guidance,
        "interval_days": interval_days,
        "as_of": start.isoformat(),
        "next_check_dates": next_checks,
        "action": "Check soil moisture first; water only when the species guidance says it is dry enough.",
    }
