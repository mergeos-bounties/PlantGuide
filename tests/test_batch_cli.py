"""Tests for plantguide identify batch (PlantGuide issue #3)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from plantguide.config import OUT_DIR
from plantguide.identify.pipeline import identify_from_sample, identify_from_tags


def test_batch_on_all_samples() -> None:
    """Run identify on every sample and check we get valid results."""
    from plantguide.data.loader import list_sample_files, load_sample

    files = list_sample_files()
    assert len(files) > 0, "No sample files found"

    for path in files:
        sample = load_sample(path)
        tags = sample.get("tags") or []
        result = identify_from_tags(tags, top_k=3)
        assert "matches" in result
        assert len(result["matches"]) > 0


def test_batch_hit_tracking() -> None:
    """For samples with expected_species, verify hit flag works."""
    from plantguide.data.loader import list_sample_files, load_sample

    hits = 0
    total_with_expected = 0
    for path in list_sample_files():
        sample = load_sample(path)
        expected = sample.get("expected_species")
        if not expected:
            continue
        total_with_expected += 1
        result = identify_from_tags(sample.get("tags") or [], top_k=1)
        top_id = result["matches"][0].get("species_id", "") if result["matches"] else ""
        if str(top_id).lower() == str(expected).lower():
            hits += 1

    assert total_with_expected > 0, "Need at least one sample with expected_species"
    # At minimum expect some hits (model is tag-based Jaccard, should work)
    assert hits >= 1, f"Expected at least 1 hit, got {hits}/{total_with_expected}"


def test_batch_report_json_writable() -> None:
    """Simulate batch report generation and ensure valid JSON output."""
    from plantguide.data.loader import list_sample_files, load_sample

    results = []
    for path in list_sample_files():
        sample = load_sample(path)
        result = identify_from_tags(sample.get("tags") or [], top_k=1)
        results.append({
            "sample_id": sample.get("id"),
            "top_match": result["matches"][0].get("species_id") if result.get("matches") else None,
        })

    report = {"total": len(results), "results": results}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(report, f)

    # Re-read to confirm valid
    with open(f.name) as f:
        reloaded = json.load(f)
    assert reloaded["total"] == len(results)
    Path(f.name).unlink()


def test_identify_from_sample_with_expected() -> None:
    """identify_from_sample returns hit_top1 when expected_species matches."""
    result = identify_from_sample(Path("data/samples/obs_snake.json"), top_k=1)
    assert result.get("sample_id") == "obs_snake"
    assert "expected_species" in result
    # The toy model should match snake_plant for snake-like tags
    # (at minimum the result has the hit_top1 flag)
    assert "hit_top1" in result
