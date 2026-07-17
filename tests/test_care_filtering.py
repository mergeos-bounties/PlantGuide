import pytest

from plantguide.care.filtering import filter_species_by_care
from plantguide.data.loader import load_species_catalog


def test_filter_species_by_light_and_water_uses_intersection() -> None:
    species = [
        {"id": "sun", "care": {"light": "Full sun", "water": "Water weekly"}},
        {"id": "shade", "care": {"light": "Low light", "water": "Water weekly"}},
        {"id": "dry", "care": {"light": "Full sun", "water": "Let soil dry"}},
    ]

    matches = filter_species_by_care(species, light="sun", water="weekly")

    assert [item["id"] for item in matches] == ["sun"]


def test_filter_species_by_care_matches_catalog_and_requires_a_filter() -> None:
    matches = filter_species_by_care(load_species_catalog(), light="bright")

    assert matches
    assert all("bright" in str(item["care"].get("light") or "").lower() for item in matches)
    with pytest.raises(ValueError, match="provide --light"):
        filter_species_by_care(load_species_catalog())
