"""Validate that schemas/ matches real Python SDK payloads.

Runs against the bundled data/ fixtures (no network required).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402

try:
    import jsonschema  # type: ignore
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


SCHEMAS = ROOT / "schemas"
SPECIES_DIR = ROOT / "data" / "species"
SAMPLES_DIR = ROOT / "data" / "samples"


@pytest.fixture(scope="module")
def species_schema():
    return json.loads((SCHEMAS / "species.schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def observation_schema():
    return json.loads((SCHEMAS / "observation.schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def care_card_schema():
    return json.loads((SCHEMAS / "care_card.schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def identify_response_schema():
    return json.loads((SCHEMAS / "identify_response.schema.json").read_text(encoding="utf-8"))


def _iter_species_files():
    return sorted(SPECIES_DIR.glob("*.json"))


def _iter_sample_files():
    return sorted(SAMPLES_DIR.glob("obs_*.json"))


# ----- Structural (no jsonschema required) ---------------------------------

def test_species_schema_has_required_fields(species_schema):
    for k in ("$schema", "title", "type", "required", "properties"):
        assert k in species_schema


def test_observation_schema_has_required_fields(observation_schema):
    for k in ("$schema", "title", "type", "required", "properties"):
        assert k in observation_schema


def test_care_card_schema_has_required_fields(care_card_schema):
    assert "species_id" in care_card_schema["required"]


def test_identify_response_schema_matches(matches_in_required=True):
    schema = json.loads((SCHEMAS / "identify_response.schema.json").read_text(encoding="utf-8"))
    assert "matches" in schema["required"]


# ----- Shape vs Python payloads --------------------------------------------

def test_species_files_validate_against_schema(species_schema):
    if not HAS_JSONSCHEMA:
        pytest.skip("jsonschema not installed (pip install jsonschema)")
    bad = []
    for f in _iter_species_files():
        payload = json.loads(f.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(payload, species_schema)
        except jsonschema.ValidationError as e:
            bad.append((f.name, e.message))
    assert not bad, f"invalid species files: {bad}"


def test_observation_files_validate_against_schema(observation_schema):
    if not HAS_JSONSCHEMA:
        pytest.skip("jsonschema not installed")
    bad = []
    for f in _iter_sample_files():
        payload = json.loads(f.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(payload, observation_schema)
        except jsonschema.ValidationError as e:
            bad.append((f.name, e.message))
    assert not bad, f"invalid observation files: {bad}"


def test_care_card_schema_matches_python_care_card():
    """Build a CareCard via the Python loader and validate it against the schema."""
    if not HAS_JSONSCHEMA:
        pytest.skip("jsonschema not installed")
    from plantguide.care.cards import care_card_for_species

    schema = json.loads((SCHEMAS / "care_card.schema.json").read_text(encoding="utf-8"))
    for f in _iter_species_files()[:5]:
        species_id = json.loads(f.read_text(encoding="utf-8"))["id"]
        card = care_card_for_species(species_id)
        jsonschema.validate(card, schema)


def test_identify_response_schema_matches_python_sdk():
    """Build an IdentifyResponse via assess_for_app() and validate."""
    if not HAS_JSONSCHEMA:
        pytest.skip("jsonschema not installed")
    import jsonschema  # type: ignore
    from plantguide.integrations.sdk import assess_for_app

    # top_care is now inlined, so no $ref resolution needed.
    schema = json.loads((SCHEMAS / "identify_response.schema.json").read_text(encoding="utf-8"))
    payload = assess_for_app(["calathea", "humidity", "indoor"])
    jsonschema.validate(payload, schema)


def test_sdk_assess_for_app_has_expected_keys():
    """Smoke-check the integration_version + ready_for_ui contract."""
    from plantguide.integrations.sdk import assess_for_app
    r = assess_for_app(["calathea"])
    assert r["integration_version"] == "plantguide.sdk.v1"
    assert r["ready_for_ui"] is True
    assert isinstance(r["matches"], list)


def test_sdk_care_for_app_shape():
    from plantguide.integrations.sdk import care_for_app
    r = care_for_app("calathea_orbifolia")
    assert r["integration_version"] == "plantguide.sdk.v1"
    assert "care" not in r  # top-level, not nested


def test_every_species_id_is_snake_case(species_schema):
    pattern = species_schema["properties"]["id"]["pattern"]
    import re
    for f in _iter_species_files():
        sid = json.loads(f.read_text(encoding="utf-8"))["id"]
        assert re.match(pattern, sid), f"bad species id in {f.name}: {sid}"