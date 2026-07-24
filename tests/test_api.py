"""Tests for the FastAPI endpoints."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from plantguide.api.app import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "species_count" in data
        assert "version" in data


class TestIdentify:
    def test_identify_with_tags(self):
        """Identify a plant using descriptive tags."""
        response = client.post(
            "/identify",
            data={"tags": "large, green, leaves, indoor", "top_k": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) > 0
        assert data["query_tags"] == ["large", "green", "leaves", "indoor"]
        assert "model" in data

    def test_identify_with_tags_and_care(self):
        """Identify returns care card for top match when with_care=True."""
        response = client.post(
            "/identify",
            data={"tags": "monstera, split, leaves, tropical", "top_k": 1, "with_care": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["top_care"] is not None
        assert "watering" in data["top_care"]

    def test_identify_without_tags_or_file_returns_400(self):
        """Missing both file and tags returns 400."""
        response = client.post("/identify", data={})
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_identify_with_photo(self):
        """Identify from a sample photo file."""
        # Find a sample photo
        sample_dir = Path(__file__).parents[2] / "data" / "samples" / "photos"
        photos = list(sample_dir.glob("*"))
        if not photos:
            pytest.skip("No sample photos found")

        photo_path = photos[0]
        with open(photo_path, "rb") as f:
            response = client.post(
                "/identify",
                files={"file": (photo_path.name, f, "image/jpeg")},
                data={"top_k": 2},
            )
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) > 0
        assert "source" in data


class TestSpeciesCare:
    def test_get_care_for_existing_species(self):
        """Get care card for a known species."""
        response = client.get("/species/monstera_deliciosa/care")
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["species_id"] == "monstera_deliciosa"
        assert data["care"] is not None
        assert "watering" in data["care"]

    def test_get_care_for_nonexistent_species(self):
        """Non-existent species returns 404."""
        response = client.get("/species/nonexistent_plant_xyz/care")
        assert response.status_code == 404


class TestListSpecies:
    def test_list_species_returns_catalog(self):
        """GET /species returns all species in catalog."""
        response = client.get("/species")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Each entry has basic fields
        for entry in data:
            assert "species_id" in entry
            assert "common_name" in entry
            assert "scientific_name" in entry