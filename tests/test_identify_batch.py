"""Tests for `plantguide identify batch` command (issue #3)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from plantguide.cli import app
from plantguide.identify.pipeline import identify_from_sample

runner = CliRunner()


def test_batch_default_samples_dir(tmp_path: Path) -> None:
    """Batch command runs on the real samples dir and writes a report."""
    out = tmp_path / "batch.json"
    result = runner.invoke(app, ["identify", "batch", "--out", str(out)])
    assert result.exit_code == 0, f"CLI error: {result.output}"
    assert out.exists(), "Report file was not created"
    report = json.loads(out.read_text())
    assert "total_samples" in report
    assert "top1_hits" in report
    assert "top1_hit_rate" in report
    assert "results" in report
    assert report["total_samples"] >= 1


def test_batch_report_structure(tmp_path: Path) -> None:
    """Report JSON has all required top-level keys."""
    out = tmp_path / "report.json"
    runner.invoke(app, ["identify", "batch", "--out", str(out)])
    report = json.loads(out.read_text())
    for key in ("total_samples", "samples_with_expected_species", "top1_hits", "top1_hit_rate", "results"):
        assert key in report, f"Missing key: {key}"


def test_batch_hit_rate_within_bounds(tmp_path: Path) -> None:
    """Top-1 hit rate is between 0 and 1 when labelled samples exist."""
    out = tmp_path / "batch.json"
    runner.invoke(app, ["identify", "batch", "--out", str(out)])
    report = json.loads(out.read_text())
    rate = report.get("top1_hit_rate")
    if rate is not None:
        assert 0.0 <= rate <= 1.0


def test_batch_at_least_70_percent_hit_rate(tmp_path: Path) -> None:
    """Baseline quality: top-1 hit rate >= 70% on labelled catalog samples."""
    out = tmp_path / "batch.json"
    runner.invoke(app, ["identify", "batch", "--out", str(out)])
    report = json.loads(out.read_text())
    rate = report.get("top1_hit_rate")
    labelled = report.get("samples_with_expected_species", 0)
    if labelled >= 5 and rate is not None:
        assert rate >= 0.70, f"Hit rate {rate:.0%} is below 70%"


def test_batch_custom_dir(tmp_path: Path) -> None:
    """Batch command works on a custom directory of sample JSON files."""
    # Create a tiny fixture sample dir
    sample = {
        "id": "obs_monstera",
        "tags": ["tropical", "fenestrated leaves", "climbing", "indoor", "large leaves"],
        "expected_species": "monstera_deliciosa",
    }
    sample_file = tmp_path / "obs_monstera.json"
    sample_file.write_text(json.dumps(sample))

    out = tmp_path / "out.json"
    result = runner.invoke(app, ["identify", "batch", "--dir", str(tmp_path), "--out", str(out)])
    assert result.exit_code == 0, f"CLI error: {result.output}"

    report = json.loads(out.read_text())
    assert report["total_samples"] == 1
    assert report["samples_with_expected_species"] == 1
    # Monstera should be a strong hit
    assert report["top1_hits"] == 1
    assert report["top1_hit_rate"] == 1.0


def test_batch_empty_dir(tmp_path: Path) -> None:
    """Batch command exits with code 1 when no samples are found."""
    out = tmp_path / "batch.json"
    result = runner.invoke(app, ["identify", "batch", "--dir", str(tmp_path), "--out", str(out)])
    assert result.exit_code == 1


def test_batch_no_expected_species(tmp_path: Path) -> None:
    """Samples without expected_species contribute to total but not hit rate."""
    sample = {"tags": ["tropical", "indoor", "large leaves"]}
    (tmp_path / "obs_unknown.json").write_text(json.dumps(sample))

    out = tmp_path / "batch.json"
    result = runner.invoke(app, ["identify", "batch", "--dir", str(tmp_path), "--out", str(out)])
    assert result.exit_code == 0

    report = json.loads(out.read_text())
    assert report["total_samples"] == 1
    assert report["samples_with_expected_species"] == 0
    assert report["top1_hit_rate"] is None


def test_batch_results_have_matches(tmp_path: Path) -> None:
    """Each result entry contains a matches list."""
    sample = {
        "tags": ["tropical", "fenestrated leaves", "climbing", "indoor", "large leaves"],
        "expected_species": "monstera_deliciosa",
    }
    (tmp_path / "obs_test.json").write_text(json.dumps(sample))
    out = tmp_path / "batch.json"
    runner.invoke(app, ["identify", "batch", "--dir", str(tmp_path), "--out", str(out)])
    report = json.loads(out.read_text())
    first = report["results"][0]
    assert "matches" in first
    assert len(first["matches"]) >= 1
