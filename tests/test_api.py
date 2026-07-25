"""Tests for PlantGuide FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from plantguide.api.main import app

client = TestClient(app)


def test_health():
    """Health check returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_species_not_found():
    """Species endpoint returns stub response for any ID."""
    response = client.get("/species/rose")
    assert response.status_code == 200
    data = response.json()
    assert data["species_id"] == "rose"
