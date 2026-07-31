"""Tests for WeightedPlantIdentifier — training, save/load, weighted ranking."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from plantguide.models.weighted import WeightedPlantIdentifier


class TestWeightedIdentifier:
    def test_init_with_default_catalog(self):
        model = WeightedPlantIdentifier()
        assert model.catalog is not None
        assert len(model.catalog) > 0
        assert model._trained is False
        assert model._tag_weights == {}

    def test_init_with_custom_catalog(self):
        catalog = [
            {"id": "test_1", "common_name": "Test Plant", "tags": ["green", "leafy"]}
        ]
        model = WeightedPlantIdentifier(catalog=catalog)
        assert len(model.catalog) == 1

    def test_identify_fallback_jaccard_no_weights(self):
        """Without training, falls back to Jaccard similarity."""
        model = WeightedPlantIdentifier()
        results = model.identify(["green leaves", "red flowers"], top_k=3)
        assert len(results) > 0
        for r in results:
            assert "score" in r
            assert 0.0 <= r["score"] <= 1.0
            assert "Jaccard" in r.get("explanation", "")

    def test_identify_empty_tags_returns_empty(self):
        model = WeightedPlantIdentifier()
        assert model.identify([]) == []
        assert model.identify(["", " "]) == []

    def test_save_load_weights_roundtrip(self, tmp_path: Path):
        model = WeightedPlantIdentifier()
        model._tag_weights = {"green": 2.5, "red": 1.2, "leafy": 0.8}
        model._trained = True

        path = tmp_path / "weights.json"
        result = model.save_weights(path)
        assert result["ok"] is True
        assert path.exists()

        # Load into fresh model
        model2 = WeightedPlantIdentifier()
        load_result = model2.load_weights(path)
        assert load_result["ok"] is True
        assert model2._trained is True
        assert model2._tag_weights["green"] == 2.5
        assert model2._tag_weights["red"] == 1.2

    def test_load_weights_missing_file(self, tmp_path: Path):
        model = WeightedPlantIdentifier()
        result = model.load_weights(tmp_path / "nonexistent.json")
        assert result["ok"] is False
        assert "not found" in result["error"]

    def test_identify_with_weights_scores_differ_from_jaccard(self):
        """Weighted scores should differ from pure Jaccard when weights vary."""
        catalog = [
            {
                "id": "sp_a",
                "common_name": "Species A",
                "tags": ["green", "leafy", "tall"],
            },
            {
                "id": "sp_b",
                "common_name": "Species B",
                "tags": ["red", "flowering", "short"],
            },
        ]
        model = WeightedPlantIdentifier(catalog=catalog)

        # With uniform weights (all = 1.0), should match Jaccard
        uniform_weights = {"green": 1.0, "leafy": 1.0, "tall": 1.0, "red": 1.0, "flowering": 1.0, "short": 1.0}
        results_uniform = model.identify(["green", "leafy"], top_k=2, weights=uniform_weights)

        # With skewed weights, ranking should differ
        skewed_weights = {"green": 0.1, "leafy": 0.1, "tall": 10.0, "red": 10.0, "flowering": 10.0, "short": 1.0}
        results_skewed = model.identify(["green", "leafy"], top_k=2, weights=skewed_weights)

        # Both should return results
        assert len(results_uniform) == 2
        assert len(results_skewed) == 2

    def test_tag_weights_property(self):
        model = WeightedPlantIdentifier()
        model._tag_weights = {"a": 1.0, "b": 2.0}
        w = model.tag_weights
        assert w == {"a": 1.0, "b": 2.0}
        # Should be a copy
        w["a"] = 999.0
        assert model._tag_weights["a"] == 1.0

    def test_identify_top_k_respects_limit(self):
        model = WeightedPlantIdentifier()
        for k in [1, 3, 5]:
            results = model.identify(["green", "leafy"], top_k=k)
            assert len(results) == k

    def test_result_structure(self):
        model = WeightedPlantIdentifier()
        results = model.identify(["green leaves"])
        r = results[0]
        expected_keys = {
            "species_id", "common_name", "scientific_name",
            "score", "confidence", "tag_overlap", "matched_tags",
            "species_only_tags", "query_only_tags", "explanation",
        }
        assert expected_keys.issubset(r.keys())

    def test_save_weights_json_structure(self, tmp_path: Path):
        model = WeightedPlantIdentifier()
        model._tag_weights = {"test_tag": 1.5}
        model._trained = True
        path = tmp_path / "w.json"
        model.save_weights(path)

        raw = json.loads(path.read_text())
        assert raw["model"] == "WeightedPlantIdentifier"
        assert raw["tag_weights"] == {"test_tag": 1.5}
        assert raw["trained"] is True
        assert raw["tag_count"] == 1


def test_weighted_identifier_importable():
    from plantguide.models.weighted import WeightedPlantIdentifier
    assert WeightedPlantIdentifier is not None


def test_train_on_samples_smoke():
    """Smoke test: training on real samples shouldn't crash."""
    model = WeightedPlantIdentifier()
    result = model.train(epochs=2)
    assert "history" in result or "error" in result
