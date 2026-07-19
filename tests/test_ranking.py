"""Tests for the enhanced ranking model (#11)."""

from __future__ import annotations

from plantguide.identify.ranking import compute_weighted_scores, _compute_tag_weight, _fuzzy_match


SIMPLE_CATALOG = [
    {
        "id": "monstera_deliciosa",
        "common_name": "Monstera",
        "scientific_name": "Monstera deliciosa",
        "tags": ["tropical", "fenestrated leaves", "climbing", "indoor", "large leaves"],
    },
    {
        "id": "chlorophytum_comosum",
        "common_name": "Spider Plant",
        "scientific_name": "Chlorophytum comosum",
        "tags": ["indoor", "easy care", "trailing", "air purifying", "green and white"],
    },
    {
        "id": "cactus_astrophytum",
        "common_name": "Star Cactus",
        "scientific_name": "Astrophytum asterias",
        "tags": ["succulent", "cactus", "desert", "slow growing", "yellow flowers"],
    },
]


def test_weighted_scoring_returns_sorted_matches() -> None:
    results = compute_weighted_scores(
        ["tropical", "indoor", "large leaves", "fenestrated"],
        SIMPLE_CATALOG,
    )
    assert len(results) == 3
    # Monstera should be top
    assert results[0]["species_id"] == "monstera_deliciosa"
    assert results[0]["score"] >= results[1]["score"]


def test_weighted_scoring_includes_explanation() -> None:
    results = compute_weighted_scores(
        ["tropical", "fenestrated leaves"],
        SIMPLE_CATALOG,
    )
    assert "explanation" in results[0]
    assert results[0]["explanation"]
    assert len(results[0]["matched_tags"]) >= 1


def test_no_match_returns_low_score() -> None:
    results = compute_weighted_scores(
        ["aquatic", "underwater", "submerged"],
        SIMPLE_CATALOG,
    )
    assert results[0]["score"] == results[0]["score"]  # not NaN
    assert results[0]["score"] < 0.3  # low match


def test_fuzzy_match() -> None:
    assert _fuzzy_match("low light", "bright indirect light")
    assert _fuzzy_match("indoor", "indoor tropical")
    assert not _fuzzy_match("aquatic", "desert")


def test_tag_weight_default() -> None:
    w = _compute_tag_weight("fenestrated leaves")
    assert w >= 0.4


def test_tag_weight_rare_specific() -> None:
    w = _compute_tag_weight("variegated white stripe")
    assert w >= 1.0


def test_results_include_metadata() -> None:
    results = compute_weighted_scores(
        ["tropical", "indoor", "large leaves"],
        SIMPLE_CATALOG,
    )
    r = results[0]
    assert "species_id" in r
    assert "common_name" in r
    assert "matched_tags" in r
    assert "species_only_tags" in r
    assert "query_only_tags" in r
    assert "score" in r


def test_all_tags_unmatched() -> None:
    results = compute_weighted_scores(
        ["imaginary", "fake"],
        SIMPLE_CATALOG,
    )
    for r in results:
        assert len(r["matched_tags"]) == 0
        assert r["score"] < 0.3


def test_scoring_differentiates_similar_tags() -> None:
    """Query matching should differentiate between species with different tag sets."""
    results = compute_weighted_scores(
        ["succulent", "desert", "cactus", "slow growing"],
        SIMPLE_CATALOG,
    )
    assert results[0]["species_id"] == "cactus_astrophytum"
