"""Tests for FastAPI routes (bounty #9)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from plantguide.api.routes import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_identify_basic() -> None:
    resp = client.post("/identify", json={
        "tags": ["tropical", "fenestrated leaves", "climbing", "large leaves"],
        "top_k": 3,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) == 3
    assert data["matches"][0]["species_id"] == "monstera_deliciosa"
    assert "top_care" in data
    assert data["top_care"]["common_name"] == "Monstera"


def test_identify_minimal() -> None:
    resp = client.post("/identify", json={
        "tags": ["succulent"],
        "top_k": 1,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) == 1
    assert data["matches"][0]["score"] > 0


def test_identify_no_care() -> None:
    resp = client.post("/identify?with_care=false", json={
        "tags": ["cactus", "spines"],
        "top_k": 2,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "top_care" not in data or data["top_care"] is None


def test_identify_empty_tags() -> None:
    resp = client.post("/identify", json={
        "tags": [],
        "top_k": 3,
    })
    assert resp.status_code == 422  # validation error


def test_get_care_card() -> None:
    resp = client.get("/species/monstera_deliciosa/care")
    assert resp.status_code == 200
    data = resp.json()
    assert data["species_id"] == "monstera_deliciosa"
    assert data["common_name"] == "Monstera"
    assert data["summary"]
    assert isinstance(data["common_issues"], list)
    assert isinstance(data["tips"], list)


def test_get_care_card_not_found() -> None:
    resp = client.get("/species/nonexistent_plant/care")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_identify_custom_k() -> None:
    resp = client.post("/identify", json={
        "tags": ["green", "leafy", "indoor"],
        "top_k": 5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) == 5
