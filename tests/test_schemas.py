"""Tests for Pydantic schema validation (PlantGuide issue #4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from plantguide.data.loader import load_json
from plantguide.schemas import (
    CareInfo,
    ObservationSample,
    Species,
    validate_sample,
    validate_species,
)


# ---------------------------------------------------------------------------
# Species schema
# ---------------------------------------------------------------------------

def test_species_valid_minimal() -> None:
    """Species with only required fields."""
    sp = Species.model_validate({"id": "test_plant"})
    assert sp.id == "test_plant"
    assert sp.common_name == ""
    assert sp.tags == []


def test_species_valid_full() -> None:
    """Full species entry from a real fixture."""
    raw = load_json(Path("data/species/snake_plant.json"))
    sp = validate_species(raw)
    assert sp.id == "snake_plant"
    assert sp.common_name == "Snake Plant"
    assert "succulent" in sp.tags
    assert sp.care.light != ""
    assert "toxic_to_pets" in sp.toxicity


def test_species_missing_id_raises() -> None:
    """Species without id should fail validation."""
    with pytest.raises(ValidationError):
        Species.model_validate({"common_name": "No ID"})


def test_species_empty_id_raises() -> None:
    """Species with empty string id should fail."""
    with pytest.raises(ValidationError):
        Species.model_validate({"id": ""})


def test_species_id_normalized() -> None:
    """Species id is normalized to lowercase slug."""
    sp = Species.model_validate({"id": "  Snake Plant  "})
    assert sp.id == "snake_plant"


def test_species_default_care() -> None:
    """Species without care field gets sensible defaults."""
    sp = Species.model_validate({"id": "foo"})
    assert sp.care.light == ""
    assert sp.care.common_issues == []


def test_all_species_fixtures_valid() -> None:
    """Every species JSON file under data/species/ must pass validation."""
    from plantguide.data.loader import list_species_files

    errors = []
    for path in list_species_files():
        try:
            validate_species(load_json(path))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")

    assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# ObservationSample schema
# ---------------------------------------------------------------------------

def test_sample_valid_minimal() -> None:
    """Sample with only id."""
    s = ObservationSample.model_validate({"id": "obs_foo"})
    assert s.id == "obs_foo"
    assert s.tags == []
    assert s.expected_species is None


def test_sample_valid_full() -> None:
    """Sample from real fixture."""
    raw = load_json(Path("data/samples/obs_monstera.json"))
    s = validate_sample(raw)
    assert s.id == "obs_monstera"
    assert "tropical" in s.tags
    assert s.expected_species == "monstera_deliciosa"


def test_sample_missing_id_ok_for_legacy() -> None:
    """Sample without id gets empty default (legacy fixture compat)."""
    s = ObservationSample.model_validate({"tags": ["green"]})
    assert s.id == ""  # legacy: no id required


def test_sample_empty_id_ok() -> None:
    """Sample with empty id stays empty (legacy fixture compat)."""
    s = ObservationSample.model_validate({"id": ""})
    assert s.id == ""


def test_all_samples_fixtures_valid() -> None:
    """Every sample JSON file under data/samples/ must pass validation."""
    from plantguide.data.loader import list_sample_files

    errors = []
    for path in list_sample_files():
        try:
            validate_sample(load_json(path))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")

    assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# CareInfo defaults
# ---------------------------------------------------------------------------

def test_care_info_defaults() -> None:
    """CareInfo with no fields has all empty defaults."""
    ci = CareInfo()
    assert ci.light == ""
    assert ci.water == ""
    assert ci.common_issues == []
    assert ci.tips == []


# ---------------------------------------------------------------------------
# Edge cases — bad JSON fixtures
# ---------------------------------------------------------------------------

def test_bad_species_missing_care_fields_ok() -> None:
    """Missing care sub-fields are filled with defaults, not an error."""
    sp = Species.model_validate({
        "id": "minimal",
        "care": {"light": "bright"}  # only one field set
    })
    assert sp.care.light == "bright"
    assert sp.care.water == ""  # defaulted


def test_bad_sample_extra_fields_ok() -> None:
    """Extra unknown fields are ignored (Pydantic default)."""
    s = ObservationSample.model_validate({
        "id": "obs_x",
        "tags": ["a"],
        "extra_field_ignored": 123,
    })
    assert s.id == "obs_x"
