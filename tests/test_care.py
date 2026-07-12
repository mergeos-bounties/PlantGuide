from __future__ import annotations

import pytest

from plantguide.care.cards import care_card_for_species, watering_hint


def test_care_card() -> None:
    card = care_card_for_species("snake_plant")
    assert card["common_name"]
    assert card["water"]
    assert isinstance(card["tips"], list)


def test_unknown_species() -> None:
    with pytest.raises(KeyError):
        care_card_for_species("not_a_real_plant_xyz")


def test_watering_hint() -> None:
    hint = watering_hint("aloe_vera", season="winter")
    assert hint["season"] == "winter"
    assert hint["seasonal_note"]
