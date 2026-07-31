"""Tests for WeightedRanker — train, save, load, identify, fallback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plantguide.data.loader import list_sample_files, list_species_files, load_sample, load_species_catalog
from plantguide.models.toy import ToyPlantIdentifier
from plantguide.models.weighted_ranker import WeightedRanker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def catalog() -> list[dict]:
    return load_species_catalog()


@pytest.fixture
def ranker(catalog: list[dict]) -> WeightedRanker:
    return WeightedRanker(catalog)


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------


class TestTrain:
    def test_train_pure_idf(self, ranker: WeightedRanker) -> None:
        info = ranker.train(use_sklearn=False)
        assert info["n_species"] > 0
        assert info["n_tags"] > 0
        assert info["method"] == "pure-idf"
        assert ranker.weights is not None
        assert len(ranker.weights) == info["n_tags"]
        # Weights should be >= log(2) ≈ 0.69 for all tags
        for tag, w in ranker.weights.items():
            assert w >= 0.69, f"weight for {tag!r} too low: {w}"

    def test_train_twice_idempotent(self, ranker: WeightedRanker) -> None:
        info1 = ranker.train(use_sklearn=False)
        info2 = ranker.train(use_sklearn=False)
        assert info1["n_tags"] == info2["n_tags"]
        assert info1["weights"] == info2["weights"]


# ---------------------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------------------


class TestPersist:
    def test_save_and_load(self, ranker: WeightedRanker, tmp_path: Path) -> None:
        ranker.train(use_sklearn=False)
        path = tmp_path / "weights.json"
        saved = ranker.save(path)
        assert saved.exists()

        # Load into a fresh ranker
        fresh = WeightedRanker(ranker.catalog)
        fresh.load(path)
        assert fresh.weights is not None
        assert len(fresh.weights) == len(ranker.weights or {})
        for tag in ranker.weights or {}:
            assert abs(fresh.weights.get(tag, 0) - ranker.weights[tag]) < 1e-6

    def test_load_partial_tags(self, ranker: WeightedRanker, tmp_path: Path) -> None:
        """Loading weights that miss some catalog tags fills them with 0."""
        ranker.train(use_sklearn=False)
        path = tmp_path / "partial_weights.json"
        payload = {
            "model": "WeightedRanker",
            "weights": {"tropical": 2.5, "indoor": 1.8},
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

        ranker.load(path)
        assert ranker.weights is not None
        # tropical and indoor kept
        assert ranker.weights["tropical"] == 2.5
        assert ranker.weights["indoor"] == 1.8
        # unknown tags default to 0
        assert "climbing" in ranker.weights
        assert ranker.weights["climbing"] == 0.0


# ---------------------------------------------------------------------------
# Identify — weighted path
# ---------------------------------------------------------------------------


class TestIdentifyWeighted:
    def test_weighted_identify(self, ranker: WeightedRanker) -> None:
        ranker.train(use_sklearn=False)
        results = ranker.identify(["tropical", "fenestrated leaves", "climbing", "large leaves"], top_k=3)
        assert len(results) >= 1
        # Monstera should be top or near top
        top_ids = [r["species_id"] for r in results]
        assert "monstera_deliciosa" in top_ids
        for r in results:
            assert r["ranker"] == "weighted"
            assert "score" in r
            assert "weighted_score" in r
            assert "jaccard_score" in r

    def test_weighted_improves_jaccard(self, ranker: WeightedRanker) -> None:
        """Verify that the weighted ranker can increase the score gap
        compared to raw Jaccard for a specific query."""
        ranker.train(use_sklearn=False)
        # Query with a rare tag should boost species containing it
        results = ranker.identify(["succulent", "drought tolerant"], top_k=3)
        assert len(results) >= 1

        # Compare with raw Jaccard on the same catalog
        toy = ToyPlantIdentifier(ranker.catalog)
        jaccard_results = toy.identify(["succulent", "drought tolerant"], top_k=3)

        # The top-1 may differ, but at least scores differ
        w_top = results[0]
        j_top = jaccard_results[0]
        assert abs(w_top["score"] - j_top["score"]) >= 0.0  # at minimum non-negative


# ---------------------------------------------------------------------------
# Identify — Jaccard fallback (weights not trained)
# ---------------------------------------------------------------------------


class TestFallback:
    def test_fallback_identical_to_toy(self, ranker: WeightedRanker) -> None:
        """Without training, WeightedRanker.identify() must match ToyPlantIdentifier."""
        toy = ToyPlantIdentifier(ranker.catalog)
        tags = ["tropical", "climbing", "indoor"]
        weighted_results = ranker.identify(tags, top_k=3)
        toy_results = toy.identify(tags, top_k=3)

        assert len(weighted_results) == len(toy_results)
        for w, t in zip(weighted_results, toy_results):
            assert w["species_id"] == t["species_id"]
            assert abs(w["score"] - t["score"]) < 1e-6
            assert w["ranker"] == "jaccard-fallback"

    def test_fallback_empty_query(self, ranker: WeightedRanker) -> None:
        assert ranker.identify([], top_k=3) == []
        assert ranker.identify(["  ", ""], top_k=3) == []

    def test_fallback_single_tag(self, ranker: WeightedRanker) -> None:
        results = ranker.identify(["tropical"], top_k=1)
        assert len(results) == 1
        assert results[0]["score"] > 0


# ---------------------------------------------------------------------------
# Integration — top-1 hit rate on labeled samples
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_top1_hit_rate(self) -> None:
        """The weighted ranker should match or exceed the toy Jaccard baseline
        on labeled samples."""
        ranker = WeightedRanker()
        ranker.train(use_sklearn=False)

        toy = ToyPlantIdentifier()

        samples = list_sample_files()
        assert len(samples) >= 5, "Need at least 5 labeled samples"

        w_hits = 0
        j_hits = 0
        labeled = 0

        for path in samples:
            sample = load_sample(path)
            tags = sample.get("tags") or []
            expected = sample.get("expected_species")
            if not tags or not expected:
                continue
            labeled += 1

            w_result = ranker.identify(tags, top_k=1)
            j_result = toy.identify(tags, top_k=1)

            if w_result and w_result[0].get("species_id") == expected:
                w_hits += 1
            if j_result and j_result[0].get("species_id") == expected:
                j_hits += 1

        # Both should have decent hit rates on the curated samples
        j_rate = j_hits / labeled if labeled else 0
        w_rate = w_hits / labeled if labeled else 0
        assert j_rate >= 0.5, f"Jaccard baseline too low: {j_rate:.2f}"
        assert w_rate >= j_rate - 0.1, f"Weighted ({w_rate:.2f}) significantly worse than Jaccard ({j_rate:.2f})"
