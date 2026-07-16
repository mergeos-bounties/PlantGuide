"""Tests for the care calendar planner."""

from __future__ import annotations

import json

import pytest

from plantguide.care.planner import (
    _parse_fertilizer,
    _parse_repot,
    export_ics,
    export_json,
    generate_calendar,
)


def test_parse_fertilizer_monthly():
    """Monthly fertilizer → all months in season."""
    # Monthly in growing season (Mar–Oct)
    assert _parse_fertilizer("Monthly in growing season") == list(range(3, 11))
    # Monthly in spring/summer (Mar–Aug)
    assert _parse_fertilizer("Monthly in spring/summer") == list(range(3, 9))
    # Monthly year-round (default)
    assert _parse_fertilizer("Monthly") == list(range(1, 13))


def test_parse_fertilizer_weekly():
    """Weekly or every-N-weeks → spread across season."""
    # Every 2 weeks in growing season → roughly every other week
    fert = _parse_fertilizer("Bi-weekly feed in growing season")
    assert 3 in fert  # March
    assert 5 in fert  # May
    assert 7 in fert  # July
    assert 9 in fert  # September
    assert len(fert) >= 6  # ~8 months / 2 ≈ 4, but we get more due to overlapping

    # Weekly in growing season
    fert_weekly = _parse_fertilizer("Weekly feed in growing season")
    assert len(fert_weekly) >= 6  # Should be 8 months


def test_parse_fertilizer_rare():
    """Rare / none → minimal fertilizing."""
    assert _parse_fertilizer("Rarely; once in spring") == [4]  # April
    assert _parse_fertilizer("None") == [4]  # Default to spring
    assert _parse_fertilizer("") == [4]  # Default to spring


def test_parse_repot():
    """Repot parsing: annual in spring by default."""
    rp = _parse_repot("Annual repotting in spring recommended")
    assert rp["recommended"] is True
    assert rp["months"] == [3, 4, 5]
    assert rp["every_years"] == 1

    # Every 2 years
    rp2 = _parse_repot("Repot every 2 years in spring")
    assert rp2["every_years"] == 2

    # No repot needed
    assert _parse_repot("None")["recommended"] is False


def test_generate_calendar_fertilize_only():
    """Generate calendar with fertilizer events."""
    species = [
        {
            "id": "aloe_vera",
            "common_name": "Aloe Vera",
            "care": {"fertilizer": "Rarely; half-strength in spring"},
        },
        {
            "id": "basil_sweet",
            "common_name": "Basil",
            "care": {"fertilizer": "Light nitrogen feed every 2-3 weeks"},
        },
    ]

    events = generate_calendar(species, year=2026)
    fert_events = [e for e in events if e["event_type"] == "fertilize"]

    # Aloe: should have 1 fertilize event (spring)
    aloe_fe = [e for e in fert_events if e["species_id"] == "aloe_vera"]
    assert len(aloe_fe) == 1
    assert aloe_fe[0]["date"].startswith("2026-04")  # April

    # Basil: should have multiple feeds (every 2-3 weeks)
    basil_fe = [e for e in fert_events if e["species_id"] == "basil_sweet"]
    assert len(basil_fe) >= 6  # ~20-26 weeks / 2-3 weeks ≈ 9-13


def test_generate_calendar_with_repot():
    """Calendar should include repot events when requested."""
    species = [
        {
            "id": "snake_plant",
            "common_name": "Snake Plant",
            "care": {
                "fertilizer": "Light feed 2–3× per year in warm months",
                "repot": "Every 2 years in spring",
            },
        }
    ]

    events = generate_calendar(species, year=2026, include_repot=True)
    fert = [e for e in events if e["event_type"] == "fertilize"]
    repot = [e for e in events if e["event_type"] == "repot"]

    assert len(fert) >= 2  # 2-3 times per year
    assert len(repot) >= 1  # at least one repot suggestion
    assert all(e["date"].startswith("2026-03") or e["date"].startswith("2026-04") or e["date"].startswith("2026-05") for e in repot)


def test_export_json(tmp_path):
    """JSON export writes valid JSON array."""
    events = [
        {
            "date": "2026-04-01",
            "species_id": "aloe_vera",
            "common_name": "Aloe Vera",
            "event_type": "fertilize",
            "notes": "Rarely; half-strength in spring",
        }
    ]
    out = tmp_path / "calendar.json"
    export_json(events, out)
    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert data[0]["date"] == "2026-04-01"


def test_export_ics(tmp_path):
    """ICS export produces valid VCALENDAR."""
    events = [
        {
            "date": "2026-05-15",
            "species_id": "basil",
            "common_name": "Basil",
            "event_type": "fertilize",
            "notes": "Feed every 2 weeks",
        }
    ]
    out = tmp_path / "calendar.ics"
    export_ics(events, out)
    text = out.read_text()
    assert "BEGIN:VCALENDAR" in text
    assert "END:VCALENDAR" in text
    assert "BEGIN:VEVENT" in text
    assert "SUMMARY:[PlantGuide] Fertilize: Basil" in text
    assert "DTSTART;VALUE=DATE:20260515" in text