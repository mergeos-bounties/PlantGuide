from __future__ import annotations

from plantguide.care.cards import care_card_for_species
from plantguide.data.loader import get_species_by_id, load_sample, list_sample_files


OUTDOOR_VEG_PACK = (
    "bitter_melon",
    "eggplant_purple",
    "ginger_culinary",
    "turmeric",
    "malabar_spinach",
    "lemongrass_citronella",
    "okra_abelmoschus",
    "ipomoea_aquatica",
    "capsicum_jalapeno",
    "allium_fistulosum",
)


def test_outdoor_vegetable_pack_has_at_least_eight_full_care_cards() -> None:
    assert len(OUTDOOR_VEG_PACK) >= 8
    for species_id in OUTDOOR_VEG_PACK:
        species = get_species_by_id(species_id)
        assert species is not None, species_id
        tags = {t.lower() for t in (species.get("tags") or [])}
        assert "outdoor" in tags or "tropical" in tags or "subtropical" in tags
        assert "edible" in tags or "herb" in tags or "spice" in tags or "aromatic" in tags
        care = species.get("care") or {}
        assert care.get("summary")
        assert care.get("climate_notes")
        card = care_card_for_species(species_id)
        assert card["common_name"]
        assert card["light"]
        assert card["water"]
        assert isinstance(card["tips"], list) and card["tips"]


def test_outdoor_vegetable_pack_observation_samples() -> None:
    samples = {p.stem: p for p in list_sample_files()}
    for species_id in OUTDOOR_VEG_PACK:
        path = samples.get(f"obs_{species_id}")
        assert path is not None, species_id
        sample = load_sample(path)
        assert sample.get("expected_species") == species_id
        assert sample.get("tags")
