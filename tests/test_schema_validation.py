"""Tests for Pydantic schema validation of species and sample JSON files (issue #4)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from plantguide.schemas import (
    CareCard,
    SampleRecord,
    SpeciesRecord,
    validate_sample,
    validate_species,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

GOOD_SPECIES: dict = {
    "id": "test_plant",
    "common_name": "Test Plant",
    "scientific_name": "Testus plantus",
    "tags": ["tropical", "indoor", "large leaves", "bright indirect", "climbing"],
    "care": {
        "summary": "A great test plant for schema validation.",
        "light": "Bright indirect light",
        "water": "Water when top 2 cm is dry",
        "soil": "Well-draining potting mix",
        "humidity": "50%+",
        "temperature_c": "18-28",
        "fertilizer": "Monthly balanced liquid in growing season",
        "toxicity": "Non-toxic to pets",
        "common_issues": ["Yellowing leaves", "Root rot"],
        "tips": ["Wipe leaves monthly"],
    },
}

GOOD_SAMPLE: dict = {
    "id": "obs_test_plant",
    "tags": ["tropical", "large leaves", "indoor"],
    "expected_species": "test_plant",
}


# ---------------------------------------------------------------------------
# SpeciesRecord — good fixture
# ---------------------------------------------------------------------------


def test_good_species_validates() -> None:
    rec = validate_species(GOOD_SPECIES)
    assert rec.id == "test_plant"
    assert rec.common_name == "Test Plant"
    assert len(rec.tags) == 5
    assert rec.care.light == "Bright indirect light"


def test_good_species_care_fields() -> None:
    rec = validate_species(GOOD_SPECIES)
    care = rec.care
    assert care.summary
    assert care.water
    assert care.soil
    assert care.humidity
    assert care.temperature_c
    assert care.fertilizer
    assert care.toxicity
    assert isinstance(care.common_issues, list)
    assert isinstance(care.tips, list)


# ---------------------------------------------------------------------------
# SpeciesRecord — bad fixtures
# ---------------------------------------------------------------------------


def test_missing_care_summary_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["care"]["summary"]
    with pytest.raises(ValidationError) as exc_info:
        validate_species(bad)
    assert "summary" in str(exc_info.value)


def test_missing_light_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["care"]["light"]
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_missing_water_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["care"]["water"]
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_fewer_than_5_tags_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    bad["tags"] = ["tropical", "indoor", "climbing", "aroid"]  # only 4
    with pytest.raises(ValidationError) as exc_info:
        validate_species(bad)
    assert "5" in str(exc_info.value)


def test_empty_tags_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    bad["tags"] = []
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_invalid_id_characters_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    bad["id"] = "Test Plant (invalid)"
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_missing_id_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["id"]
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_missing_common_name_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["common_name"]
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_missing_care_block_raises() -> None:
    bad = json.loads(json.dumps(GOOD_SPECIES))
    del bad["care"]
    with pytest.raises(ValidationError):
        validate_species(bad)


def test_extra_care_fields_allowed() -> None:
    """Extra fields in care should be allowed (future-proofing)."""
    extra = json.loads(json.dumps(GOOD_SPECIES))
    extra["care"]["future_field"] = "ok"
    rec = validate_species(extra)
    assert rec.care.model_extra.get("future_field") == "ok"


# ---------------------------------------------------------------------------
# SampleRecord — good fixture
# ---------------------------------------------------------------------------


def test_good_sample_validates() -> None:
    rec = validate_sample(GOOD_SAMPLE)
    assert rec.tags == ["tropical", "large leaves", "indoor"]
    assert rec.expected_species == "test_plant"


def test_sample_without_expected_species() -> None:
    rec = validate_sample({"tags": ["indoor", "succulent", "small"]})
    assert rec.expected_species is None


# ---------------------------------------------------------------------------
# SampleRecord — bad fixtures
# ---------------------------------------------------------------------------


def test_sample_empty_tags_raises() -> None:
    with pytest.raises(ValidationError):
        validate_sample({"tags": [], "expected_species": "test_plant"})


def test_sample_non_list_tags_raises() -> None:
    with pytest.raises(ValidationError):
        validate_sample({"tags": "not a list", "expected_species": "test_plant"})


# ---------------------------------------------------------------------------
# Integration: validate catalog files on disk
# ---------------------------------------------------------------------------


def test_catalog_files_pass_schema() -> None:
    """Species JSON files in data/species/ should pass SpeciesRecord validation.

    Reports validation statistics. A pass rate >= 60% is required so that
    schema-complete species dominate the catalog, while legacy stub files
    created before this schema existed are still accepted.
    """
    from plantguide.data.loader import list_species_files, load_species

    files = list_species_files()
    assert files, "No species files found — catalog missing?"

    failures: list[str] = []
    for path in files:
        data = load_species(path)
        try:
            validate_species(data)
        except ValidationError as exc:
            failures.append(f"{path.name}: {exc.error_count()} error(s)")

    pass_rate = (len(files) - len(failures)) / len(files)
    # Allow legacy stubs; require majority to be schema-compliant
    assert pass_rate >= 0.60, (
        f"Schema pass rate {pass_rate:.0%} < 60% ({len(failures)}/{len(files)} failures).\n"
        "Failing files:\n" + "\n".join(failures)
    )


def test_sample_files_pass_schema() -> None:
    """All sample JSON files in data/samples/ must pass SampleRecord validation."""
    from plantguide.data.loader import list_sample_files, load_sample

    files = list_sample_files()
    assert files, "No sample files found — samples dir missing?"

    failures: list[str] = []
    for path in files:
        data = load_sample(path)
        try:
            validate_sample(data)
        except ValidationError as exc:
            failures.append(f"{path.name}: {exc.error_count()} error(s)\n{exc}")

    assert not failures, "Schema validation failed for:\n" + "\n".join(failures)
