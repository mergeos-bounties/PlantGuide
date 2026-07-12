from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from plantguide.cli import app
from plantguide.integrations.sdk import care_report_from_sample, care_report_from_tags


def test_care_report_from_sample_schema() -> None:
    report = care_report_from_sample(Path("data/samples/obs_monstera.json"), top_k=2)

    assert report["report_type"] == "plantguide.app.care_report.v1"
    assert report["integration_version"] == "plantguide.sdk.v1"
    assert report["sample_id"] == "obs_monstera"
    assert report["top_species_id"] == "monstera_deliciosa"
    assert report["top_match"]["species_id"] == "monstera_deliciosa"
    assert len(report["matches"]) == 2
    assert report["care_card"]["species_id"] == "monstera_deliciosa"
    assert report["ready_for_ui"] is True
    assert report["license_safe_evidence"] == {
        "source": "data/samples/obs_monstera.json",
        "source_type": "sample_fixture",
        "external_assets": [],
    }


def test_care_report_from_tags_schema() -> None:
    report = care_report_from_tags(
        "tropical,fenestrated leaves,climbing,indoor,large leaves",
        top_k=1,
    )

    assert report["sample_id"] is None
    assert report["top_species_id"] == "monstera_deliciosa"
    assert report["care_card"]["common_name"] == "Monstera"
    assert report["license_safe_evidence"]["source_type"] == "inline_tags"


def test_app_demo_cli_writes_report(tmp_path: Path) -> None:
    out_path = tmp_path / "e2e-monstera-care-report.json"
    result = CliRunner().invoke(
        app,
        [
            "app",
            "demo",
            "--sample",
            "data/samples/obs_monstera.json",
            "--out",
            str(out_path),
            "-k",
            "2",
        ],
    )

    assert result.exit_code == 0, result.output
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert report["top_species_id"] == "monstera_deliciosa"
    assert report["care_card"]["species_id"] == "monstera_deliciosa"
    assert "Care report" in result.output
