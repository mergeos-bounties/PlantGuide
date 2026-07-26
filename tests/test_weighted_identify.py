"""Tests for WeightedTagIdentifier and weighted training."""

from __future__ import annotations

import json
from pathlib import Path

from plantguide.identify.pipeline import identify_from_tags
from plantguide.models.toy import _norm
from plantguide.models.weighted import WeightedTagIdentifier, create_identifier


def test_fallback_on_empty_weights() -> None:
    ident = WeightedTagIdentifier()
    assert ident._fallback is True
    result = ident.identify(["succulent", "thick leaves", "drought"])
    assert result
    assert result[0].get("score", 0) > 0


def test_fallback_on_missing_file() -> None:
    ident = WeightedTagIdentifier(weights_path="nonexistent/weights.json")
    assert ident._fallback is True
    assert ident.weights == {}


def test_load_weights_from_dict(tmp_path: Path) -> None:
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(
        json.dumps(
            {
                "weights": {
                    "aloe_vera": {
                        "succulent": 2.5,
                        "thick leaves": 1.8,
                        "drought": 1.2,
                        "spiky": 1.0,
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    ident = WeightedTagIdentifier(weights_path=weights_file)
    assert not ident._fallback
    # Normalisation converts underscores to spaces
    assert "aloe vera" in ident.weights
    assert ident.weights["aloe vera"]["succulent"] == 2.5


def test_roundtrip_save_load(tmp_path: Path) -> None:
    weights = {
        "monstera_deliciosa": {
            "tropical": 3.0,
            "fenestrated_leaves": 2.5,
        },
        "snake_plant": {
            "drought": 2.0,
            "low_light": 1.5,
        },
    }
    ident = WeightedTagIdentifier()
    ident.weights = weights
    ident._fallback = False

    path = tmp_path / "roundtrip.json"
    ident.save_weights(path)
    assert path.exists()

    ident2 = WeightedTagIdentifier(weights_path=path)
    assert not ident2._fallback
    for sid, tv_map in weights.items():
        norm_sid = _norm(sid)
        for tag, w in tv_map.items():
            norm_tag = _norm(tag)
            assert ident2.weights[norm_sid][norm_tag] == w


def test_weighted_identify_monstera() -> None:
    ident = WeightedTagIdentifier()
    result = ident.identify(
        ["tropical", "fenestrated leaves", "climbing", "large leaves"], top_k=3
    )
    assert result
    top = result[0]
    assert top.get("species_id") == "monstera_deliciosa"


def test_weighted_scoring_differs_from_jaccard(tmp_path: Path) -> None:
    weights_file = tmp_path / "test_weights.json"
    weights_file.write_text(
        json.dumps(
            {
                "weights": {
                    "aloe vera": {
                        "succulent": 1.0,
                        "thick leaves": 1.0,
                        "drought": 1.0,
                        "spiky": 1.0,
                        "medicinal gel": 1.0,
                        "full sun tolerant": 1.0,
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    catalog = [
        {
            "id": "aloe_vera",
            "common_name": "Aloe Vera",
            "scientific_name": "Aloe vera",
            "tags": [
                "succulent",
                "thick leaves",
                "drought",
                "spiky",
                "medicinal gel",
                "full sun tolerant",
            ],
        }
    ]
    ident_weighted = WeightedTagIdentifier(catalog=catalog, weights_path=weights_file)
    assert not ident_weighted._fallback

    result = ident_weighted.identify(["succulent", "spiky"], top_k=3)
    assert result
    top = result[0]
    assert top["species_id"] == "aloe_vera"
    expected_score = round(2.0 / 6.0, 4)
    assert top["score"] == expected_score


def test_create_identifier_without_weights() -> None:
    ident = create_identifier()
    assert isinstance(ident, WeightedTagIdentifier)
    assert ident._fallback is True


def test_create_identifier_with_weights(tmp_path: Path) -> None:
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(
        json.dumps({"weights": {"dummy": {"tag": 1.0}}}) + "\n", encoding="utf-8"
    )
    ident = create_identifier(weights_path=weights_file)
    assert not ident._fallback


def test_identify_from_tags_uses_weighted_when_available(tmp_path: Path, monkeypatch) -> None:
    from plantguide.identify import pipeline as pipeline_mod

    weights_file = tmp_path / "weighted_tag_weights.json"
    weights_file.write_text(
        json.dumps(
            {
                "weights": {
                    "aloe_vera": {"succulent": 1.0, "thick leaves": 1.0},
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pipeline_mod, "WEIGHTS_DIR", tmp_path)
    pipeline_mod._WEIGHTED_IDENTIFIER = None

    result = identify_from_tags("succulent,thick leaves", top_k=3)
    assert result["model"] == "WeightedTagIdentifier"
    assert result["matches"]


def test_identify_from_tags_fallback_no_weights(tmp_path: Path, monkeypatch) -> None:
    from plantguide.identify import pipeline as pipeline_mod

    empty_dir = tmp_path / "empty_weights"
    empty_dir.mkdir()
    monkeypatch.setattr(pipeline_mod, "WEIGHTS_DIR", empty_dir)
    pipeline_mod._WEIGHTED_IDENTIFIER = None

    result = identify_from_tags("succulent,thick leaves", top_k=3)
    assert result["model"] == "ToyPlantIdentifier"
    assert result["matches"]


def test_weighted_training_end_to_end(tmp_path: Path, monkeypatch) -> None:
    from plantguide.train import weighted_train as wt_mod

    monkeypatch.setattr(wt_mod, "WEIGHTS_DIR", tmp_path / "weights")
    monkeypatch.setattr(wt_mod, "RUNS_DIR", tmp_path / "runs")

    report = wt_mod.train_weighted()
    assert report["n_labeled_samples"] >= 1
    assert report["n_species_with_weights"] >= 1
    assert report["top1_hit_rate_weighted"] >= 0.0
    assert report["top1_hit_rate_jaccard"] >= 0.0
    assert Path(report["weights_path"]).exists()

    ident = WeightedTagIdentifier(weights_path=report["weights_path"])
    assert not ident._fallback
    assert len(ident.weights) >= 1
