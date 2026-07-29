import pytest
import os
import tempfile
import json
from symptom_matcher import SymptomMatcher, DISCLAIMER_TEXT
from care import show_care_details

@pytest.fixture
def sample_fixtures_file():
    data = [
        {
            "id": "test_pest",
            "name": "Test Pest",
            "category": "pest",
            "tags": ["yellow spots", "sticky leaves"],
            "remedies": ["Clean leaves", "Apply soap"]
        },
        {
            "id": "test_rot",
            "name": "Root Rot",
            "category": "disease",
            "tags": ["wilting", "squishy stems"],
            "remedies": ["Repot plant"]
        }
    ]
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(data, f)
        path = f.name
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_exact_match(sample_fixtures_file):
    matcher = SymptomMatcher(fixtures_path=sample_fixtures_file)
    res = matcher.match_symptoms(["yellow spots", "sticky leaves"])

    assert len(res["matched_issues"]) == 1
    top_match = res["matched_issues"][0]
    assert top_match["id"] == "test_pest"
    assert "Clean leaves" in top_match["remedies"]
    assert res["disclaimer"] == DISCLAIMER_TEXT

def test_case_insensitive_and_whitespace(sample_fixtures_file):
    matcher = SymptomMatcher(fixtures_path=sample_fixtures_file)
    res = matcher.match_symptoms(["  YELLOW SPOTS  ", "Sticky Leaves "])

    assert len(res["matched_issues"]) == 1
    assert res["matched_issues"][0]["id"] == "test_pest"

def test_empty_or_none_input(sample_fixtures_file):
    matcher = SymptomMatcher(fixtures_path=sample_fixtures_file)
    assert matcher.match_symptoms([])["matched_issues"] == []
    assert matcher.match_symptoms(None)["matched_issues"] == []

def test_no_matching_tags(sample_fixtures_file):
    matcher = SymptomMatcher(fixtures_path=sample_fixtures_file)
    res = matcher.match_symptoms(["purple flowers", "blue roots"])
    assert res["matched_issues"] == []

def test_care_show_integration_optional():
    # Backward compatibility test without symptom tags
    base_res = show_care_details("plant123", {"water": "weekly"})
    assert base_res["plant_id"] == "plant123"
    assert base_res["diagnosis"] is None

    # Test with optional symptom tags passed
    with_diag = show_care_details("plant123", {"water": "weekly"}, symptom_tags=["sticky leaves"])
    assert with_diag["diagnosis"] is not None
    assert "matched_issues" in with_diag["diagnosis"]
