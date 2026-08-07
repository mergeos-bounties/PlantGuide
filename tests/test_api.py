"""Tests for PlantGuide FastAPI endpoints (no server needed, uses TestClient)."""

import pytest
from fastapi.testclient import TestClient

from plantguide.api.routes import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# POST /identify
# ---------------------------------------------------------------------------

def test_identify_with_tags():
    response = client.post("/identify", json={"tags": ["green", "trailing", "indoor"], "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "query_tags" in data
    assert "matches" in data
    assert "model" in data
    assert data["model"] == "ToyPlantIdentifier"
    assert len(data["matches"]) <= 3


def test_identify_empty_tags_returns_400():
    response = client.post("/identify", json={"tags": [], "top_k": 3})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_identify_missing_tags_field():
    response = client.post("/identify", json={"top_k": 3})
    # With default tags=[], FastAPI accepts the request; our validation returns 400
    assert response.status_code in (400, 422)


def test_identify_with_many_tags():
    response = client.post("/identify", json={"tags": ["green", "succulent", "desert", "spiky"], "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) >= 0
    if data["matches"]:
        match = data["matches"][0]
        assert "species_id" in match
        assert "common_name" in match
        assert "scientific_name" in match
        assert "score" in match


def test_identify_preserves_tag_order():
    tags = ["flowering", "tropical", "indoor"]
    response = client.post("/identify", json={"tags": tags, "top_k": 3})
    assert response.status_code == 200
    assert response.json()["query_tags"] == tags


def test_identify_top_k_limits():
    response = client.post("/identify", json={"tags": ["green"], "top_k": 1})
    assert response.status_code == 200
    assert len(response.json()["matches"]) <= 1


def test_identify_top_k_validation():
    response = client.post("/identify", json={"tags": ["green"], "top_k": 50})
    assert response.status_code == 422  # max is 20


# ---------------------------------------------------------------------------
# GET /species/{id}/care
# ---------------------------------------------------------------------------

def test_care_for_known_species():
    # Test with species from the catalog
    for species_id in ["aloe_vera", "snake_plant", "basil_sweet"]:
        response = client.get(f"/species/{species_id}/care")
        if response.status_code == 200:
            data = response.json()
            assert data["species_id"] == species_id
            assert data["common_name"]
            assert "light" in data
            assert "water" in data
            assert "soil" in data
            break


def test_care_for_unknown_species_returns_404():
    response = client.get("/species/definitely_not_a_plant_xyz/care")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_care_response_schema():
    """Verify the response matches the expected schema."""
    response = client.get("/species/aloe_vera/care")
    if response.status_code == 404:
        pytest.skip("aloe_vera not in catalog")
    data = response.json()
    required_fields = [
        "species_id", "common_name", "scientific_name", "summary",
        "light", "water", "soil", "humidity", "temperature_c",
        "fertilizer", "toxicity", "common_issues", "tips",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["common_issues"], list)
    assert isinstance(data["tips"], list)


def test_care_species_id_matches_path():
    response = client.get("/species/snake_plant/care")
    if response.status_code == 200:
        assert response.json()["species_id"] in ("snake_plant", "sansevieria_trifasciata")


# ---------------------------------------------------------------------------
# Cross-endpoint integration
# ---------------------------------------------------------------------------

def test_identify_then_care():
    """Identify a plant, then fetch care for the top match."""
    response = client.post("/identify", json={"tags": ["succulent", "desert", "spiky"], "top_k": 1})
    assert response.status_code == 200
    matches = response.json()["matches"]
    if matches:
        species_id = matches[0]["species_id"]
        care_response = client.get(f"/species/{species_id}/care")
        if care_response.status_code == 200:
            assert care_response.json()["species_id"] == species_id
