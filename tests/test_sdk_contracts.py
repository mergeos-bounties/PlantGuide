from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from plantguide.integrations.sdk import care_report_from_sample, care_report_from_tags

SCHEMA_PATH = Path("schemas/plantguide-care-report.schema.json")
TYPES_PATH = Path("schemas/plantguide-sdk.d.ts")


def test_care_report_schema_matches_sample_payload_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    report = care_report_from_sample(Path("data/samples/obs_monstera.json"), top_k=2)

    assert set(schema["required"]) == set(report)
    assert schema["properties"]["report_type"]["const"] == report["report_type"]
    assert schema["properties"]["integration_version"]["const"] == report["integration_version"]
    assert schema["properties"]["license_safe_evidence"]["properties"]["source_type"]["enum"]
    _assert_required_keys(
        schema["$defs"]["care_card"]["required"],
        report["care_card"],
    )
    _assert_required_keys(
        schema["$defs"]["match"]["required"],
        report["top_match"],
    )


def test_care_report_schema_matches_inline_tags_payload_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    report = care_report_from_tags("succulent,thick leaves,drought", top_k=1)

    assert set(schema["required"]) == set(report)
    assert report["sample_id"] is None
    assert report["license_safe_evidence"]["source_type"] == "inline_tags"
    _assert_required_keys(
        schema["$defs"]["care_card"]["required"],
        report["care_card"],
    )
    _assert_required_keys(
        schema["$defs"]["match"]["required"],
        report["top_match"],
    )


def test_typescript_contract_exports_match_schema_names() -> None:
    types = TYPES_PATH.read_text(encoding="utf-8")

    assert "export interface PlantGuideCareReport" in types
    assert "report_type: \"plantguide.app.care_report.v1\"" in types
    assert "integration_version: \"plantguide.sdk.v1\"" in types
    assert "source_type: \"sample_fixture\" | \"inline_tags\"" in types
    assert "export interface PlantGuideCareCard" in types


def _assert_required_keys(required: list[str], payload: Any) -> None:
    assert isinstance(payload, dict)
    missing = set(required) - set(payload)
    assert not missing
