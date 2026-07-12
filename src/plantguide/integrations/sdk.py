from __future__ import annotations

from plantguide.care.cards import care_card_for_species
from plantguide.identify.pipeline import identify_from_tags


def assess_for_app(tags: str | list[str], *, top_k: int = 3) -> dict:
    """Stable JSON contract for plant-care apps."""
    payload = identify_from_tags(tags, top_k=top_k, with_care=True)
    payload["integration_version"] = "plantguide.sdk.v1"
    payload["ready_for_ui"] = True
    return payload


def care_for_app(species_id: str) -> dict:
    card = care_card_for_species(species_id)
    card["integration_version"] = "plantguide.sdk.v1"
    return card
