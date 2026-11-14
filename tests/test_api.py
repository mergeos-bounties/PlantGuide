import pytest
from fastapi.testclient import TestClient
from src.plantguide.api.main import app
import io

client = TestClient(app)

def test_identify_endpoint():
    """Test the POST /identify endpoint with a mock image."""
    file_content = b"fake-image-binary-content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/identify",
        files={"file": ("test_plant.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "match" in data
    assert "confidence" in data

def test_get_care_success():
    """Test GET /species/{id}/care with an existing species (aloe_vera)."""
    # Using aloe_vera as it is confirmed in the repository file list
    response = client.get("/species/aloe_vera/care")
    
    assert response.status_code == 200
    data = response.json()
    # Check for common care card fields
    assert "common_name" in data or "species" in data
    assert isinstance(data, dict)

def test_get_care_not_found():
    """Test GET /species/{id}/care with a non-existent species."""
    response = client.get("/species/non_existent_plant/care")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Care guide for species 'non_existent_plant' not found."

def test_api_docs_accessible():
    """Ensure Swagger UI is available."""
    response = client.get("/docs")
    assert response.status_code == 200
