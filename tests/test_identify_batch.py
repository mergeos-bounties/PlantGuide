"""Tests for `plantguide identify batch` command (issue #3)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from plantguide.cli import app

runner = CliRunner()

PHOTOS_DIR = Path("data/samples/photos")


@pytest.mark.skipif(
    not PHOTOS_DIR.exists() or not any(PHOTOS_DIR.glob("*.jpg")),
    reason="No demo photos available",
)
def test_identify_batch_runs(tmp_path: Path) -> None:
    """Batch command processes all demo photos and writes a valid JSON report."""
    out_file = tmp_path / "batch.json"
    result = runner.invoke(
        app,
        ["identify", "batch", "--photos", str(PHOTOS_DIR), "--out", str(out_file)],
    )
    assert result.exit_code == 0, result.output
    assert out_file.exists(), "Output file should be created"
    data = json.loads(out_file.read_text())
    assert "total" in data
    assert "identified" in data
    assert "results" in data
    assert data["total"] > 0
    assert len(data["results"]) == data["total"]


@pytest.mark.skipif(
    not PHOTOS_DIR.exists() or not any(PHOTOS_DIR.glob("*.jpg")),
    reason="No demo photos available",
)
def test_identify_batch_top1_hits(tmp_path: Path) -> None:
    """Each result should contain top1_species_id from a known hit."""
    out_file = tmp_path / "batch_top1.json"
    result = runner.invoke(
        app,
        ["identify", "batch", "--photos", str(PHOTOS_DIR), "--out", str(out_file), "-k", "1"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(out_file.read_text())
    identified = [r for r in data["results"] if r.get("top1_species_id")]
    assert len(identified) > 0, "At least one photo should be identified"


@pytest.mark.skipif(
    not PHOTOS_DIR.exists() or not any(PHOTOS_DIR.glob("*.jpg")),
    reason="No demo photos available",
)
def test_identify_batch_no_care(tmp_path: Path) -> None:
    """--no-care flag omits care cards from results."""
    out_file = tmp_path / "batch_nocare.json"
    result = runner.invoke(
        app,
        [
            "identify", "batch",
            "--photos", str(PHOTOS_DIR),
            "--out", str(out_file),
            "--no-care",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(out_file.read_text())
    for entry in data["results"]:
        assert "care" not in entry, "Care card should be absent with --no-care"


def test_identify_batch_empty_dir(tmp_path: Path) -> None:
    """Batch command exits with error when directory has no photos."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    out_file = tmp_path / "batch_empty.json"
    result = runner.invoke(
        app,
        ["identify", "batch", "--photos", str(empty_dir), "--out", str(out_file)],
    )
    assert result.exit_code != 0, "Should fail on empty directory"
