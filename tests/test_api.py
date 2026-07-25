"""Tests for the PlantGuide FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from plantguide.api.app import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestIdentify:
    def test_identify_with_tags(self) -> None:
        resp = client.post("/identify", json={"tags": ["succulent", "thick leaves", "drought"]})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["matches"]) > 0
        assert data["model"] == "ToyPlantIdentifier"
        assert data["query_tags"] == ["succulent", "thick leaves", "drought"]
        # Top match should have species_id, score, tags
        top = data["matches"][0]
        assert "species_id" in top
        assert "score" in top
        assert "common_name" in top
        # Care card should be included
        assert data["top_care"] is not None

    def test_identify_with_top_k(self) -> None:
        resp = client.post("/identify", json={"tags": ["green", "indoor"], "top_k": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["matches"]) <= 5

    def test_identify_empty_tags_fails(self) -> None:
        resp = client.post("/identify", json={"tags": []})
        assert resp.status_code == 422  # pydantic validation (min_length=1)

    def test_identify_invalid_top_k(self) -> None:
        resp = client.post("/identify", json={"tags": ["green"], "top_k": 0})
        assert resp.status_code == 422  # ge=1

    def test_identify_missing_tags_fails(self) -> None:
        resp = client.post("/identify", json={})
        assert resp.status_code == 422


class TestCareCard:
    def test_care_card_exists(self) -> None:
        resp = client.get("/species/pothos_golden/care")
        assert resp.status_code == 200
        data = resp.json()
        assert data["species_id"] == "pothos_golden"
        assert "common_name" in data
        assert "light" in data
        assert "water" in data
        assert "soil" in data

    def test_care_card_unknown_species(self) -> None:
        resp = client.get("/species/nonexistent_plant/care")
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data

    def test_care_card_has_all_fields(self) -> None:
        resp = client.get("/species/pothos_golden/care")
        data = resp.json()
        expected = {
            "species_id", "common_name", "scientific_name", "summary",
            "light", "water", "soil", "humidity", "temperature_c",
            "fertilizer", "toxicity", "common_issues", "tips",
        }
        assert set(data.keys()) >= expected


class TestOpenAPI:
    def test_docs_available(self) -> None:
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json(self) -> None:
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "PlantGuide API"