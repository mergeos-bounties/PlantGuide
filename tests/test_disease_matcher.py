import pytest
from plantguide.disease_matcher import DiseaseMatcher
import json
import os

@pytest.fixture
def test_diseases_file(tmp_path):
    diseases_data = [
        {
            "name": "Test Disease",
            "symptoms": ["test symptom 1", "test symptom 2"],
            "description": "Test description",
            "remedies": ["Test remedy 1", "Test remedy 2"]
        }
    ]
    file_path = tmp_path / "test_diseases.json"
    with open(file_path, 'w') as f:
        json.dump(diseases_data, f)
    return str(file_path)

def test_match_symptoms(test_diseases_file):
    matcher = DiseaseMatcher(test_diseases_file)
    matches = matcher.match_symptoms(["test symptom 1", "test symptom 2"])
    assert len(matches) == 1
    assert matches[0]['name'] == "Test Disease"

def test_get_disease_info(test_diseases_file):
    matcher = DiseaseMatcher(test_diseases_file)
    info = matcher.get_disease_info("Test Disease")
    assert info is not None
    assert info['name'] == "Test Disease"
    assert "Test description" in info['description']
    assert len(info['remedies']) == 2

def test_no_matches(test_diseases_file):
    matcher = DiseaseMatcher(test_diseases_file)
    matches = matcher.match_symptoms(["unknown symptom"])
    assert len(matches) == 0

def test_disease_not_found(test_diseases_file):
    matcher = DiseaseMatcher(test_diseases_file)
    info = matcher.get_disease_info("Unknown Disease")
    assert info is None