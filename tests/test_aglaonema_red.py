from __future__ import annotations

from pathlib import Path

from plantguide.care.cards import care_card_for_species
from plantguide.data.loader import get_species_by_id, load_sample
from plantguide.models.toy import ToyPlantIdentifier


def test_aglaonema_red_care_and_sample() -> None:
    species = get_species_by_id("aglaonema_red")
    assert species is not None
    assert "red variegation" in species["tags"]
    card = care_card_for_species("aglaonema_red")
    assert "toxic" in card["toxicity"].lower()
    sample = load_sample(Path("data/samples/obs_aglaonema_red.json"))
    assert sample["expected_species"] == "aglaonema_red"
    hits = ToyPlantIdentifier().identify(list(sample["tags"]), top_k=3)
    assert hits[0]["species_id"] == "aglaonema_red"


def test_aglaonema_red_photo_evidence_exists() -> None:
    root = Path("docs/species-photos/aglaonema_red")
    assert (root / "whole_plant.jpg").exists()
    assert (root / "leaf_closeup.jpg").exists()
    assert (root / "LICENSE.txt").exists()
