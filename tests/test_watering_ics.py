"""Tests for watering ICS export."""

from plantguide.watering_ics import generate_watering_ics

def test_generate_watering_ics(tmp_path):
    collection = [
        {"name": "Monstera", "water_days": 7},
        {"name": "Snake Plant", "water_days": 14}
    ]
    output = tmp_path / 'watering.ics'
    generate_watering_ics(collection, output)
    
    content = output.read_text()
    assert 'BEGIN:VCALENDAR' in content
    assert 'Water Monstera' in content
    assert 'Water Snake Plant' in content
