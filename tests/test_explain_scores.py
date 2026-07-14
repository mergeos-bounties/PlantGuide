"""Tests for #151: multi-tag identify explain scores."""
from __future__ import annotations

from plantguide.models.toy import ToyPlantIdentifier, _build_explanation


def test_explanation_included_in_match() -> None:
    """Each match result includes an explanation string."""
    identifier = ToyPlantIdentifier()
    results = identifier.identify(["indoor", "tropical", "green"], top_k=2)
    for r in results:
        assert "explanation" in r
        assert isinstance(r["explanation"], str)
        assert len(r["explanation"]) > 0


def test_matched_tags_explains_overlap() -> None:
    """Explanation mentions matched tags."""
    results = ToyPlantIdentifier().identify(["indoor", "tropical"], top_k=1)
    if results:
        assert "indoor" in results[0]["explanation"].lower() or \
               "tropical" in results[0]["explanation"].lower()


def test_explanation_includes_score() -> None:
    """Explanation mentions Jaccard score."""
    results = ToyPlantIdentifier().identify(["indoor", "tropical"], top_k=1)
    if results:
        assert "score" in results[0]["explanation"].lower() or \
               "jaccard" in results[0]["explanation"].lower()


def test_matched_tags_field() -> None:
    """New matched_tags field exists alongside tag_overlap."""
    results = ToyPlantIdentifier().identify(["indoor", "tropical"], top_k=1)
    if results:
        assert "matched_tags" in results[0]
        assert "species_only_tags" in results[0]
        assert "query_only_tags" in results[0]


def test_build_explanation_with_matches() -> None:
    """_build_explanation includes matched count."""
    expl = _build_explanation("Test", ["indoor", "green"], [], ["outdoor"], 0.6667)
    assert "Matched 2 tag" in expl
    assert "indoor" in expl
    assert "outdoor" in expl


def test_build_explanation_no_matches() -> None:
    """_build_explanation handles zero matches."""
    expl = _build_explanation("Test", [], ["arid"], ["indoor"], 0.0)
    assert "No direct tag matches" in expl
