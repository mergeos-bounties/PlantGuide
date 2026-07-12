from __future__ import annotations

from plantguide.data.loader import list_sample_files, list_species_files
from plantguide.identify.pipeline import identify_from_sample, identify_from_tags


def test_catalog_size() -> None:
    assert len(list_species_files()) >= 8


def test_identify_tags_monstera() -> None:
    result = identify_from_tags("tropical,fenestrated leaves,climbing,large leaves", top_k=3)
    assert result["matches"]
    assert result["matches"][0]["species_id"] == "monstera_deliciosa"
    assert "top_care" in result


def test_samples_top1_hits() -> None:
    files = list_sample_files()
    assert len(files) >= 5
    hits = 0
    for path in files:
        result = identify_from_sample(path)
        if result.get("hit_top1"):
            hits += 1
    assert hits >= int(0.7 * len(files))
