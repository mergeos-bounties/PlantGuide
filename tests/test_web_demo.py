import pytest
from src.web_demo import app, load_plant_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_load_plant_data():
    data = load_plant_data()
    assert isinstance(data, dict)
    assert len(data) > 0

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Plant Identification & Care Guide' in response.data

def test_plant_data_route(client):
    response = client.get('/api/plant_data')
    assert response.status_code == 200
    assert response.is_json

def test_care_info_route(client):
    # Test with a known species
    response = client.get('/api/care_info/monstera_deliciosa')
    assert response.status_code == 200
    assert response.is_json

    # Test with unknown species
    response = client.get('/api/care_info/unknown_species')
    assert response.status_code == 404