from __future__ import annotations

import pytest
from typer.testing import CliRunner

from plantguide.cli import app
from plantguide.data.loader import load_species_catalog
from plantguide.data.toxicity import VALID_TOXICITY_TAGS, normalize_toxicity


@pytest.mark.parametrize(
    ("value", "care_note", "expected"),
    [
        (["pet_safe", "edible"], None, ["pet_safe", "edible"]),
        (
            ["pet_safe", "toxic_to_pets", "unknown"],
            None,
            ["toxic_to_pets"],
        ),
        (None, "Non-toxic to cats and dogs", ["pet_safe"]),
        (None, "Non-toxic cactus with sharp spines", ["unknown"]),
        (None, "Mildly toxic to pets if ingested", ["toxic_to_pets"]),
        (None, "Non-toxic to humans; mildly toxic to pets", ["toxic_to_pets"]),
        ("Non-toxic", None, ["unknown"]),
        (None, None, ["unknown"]),
    ],
)
def test_normalize_toxicity(value: object, care_note: object, expected: list[str]) -> None:
    assert normalize_toxicity(value, care_note=care_note) == expected


def test_catalog_exposes_canonical_toxicity_schema() -> None:
    catalog = load_species_catalog()

    assert catalog
    for species in catalog:
        tags = species["toxicity"]
        assert isinstance(tags, list)
        assert tags
        assert len(tags) == len(set(tags))
        assert set(tags) <= {tag.value for tag in VALID_TOXICITY_TAGS}
        assert len({"pet_safe", "toxic_to_pets", "unknown"} & set(tags)) == 1


def test_species_list_pet_safe_filters_and_disclaims() -> None:
    result = CliRunner().invoke(app, ["species", "list", "--pet-safe"])

    assert result.exit_code == 0, result.output
    assert "Spider Plant" in result.output
    assert "Aloe Vera" not in result.output
    assert "not veterinary advice" in result.output
