"""Care calendar planner: generate fertilize + repot schedules for a species collection.

Produces monthly calendar events suitable for JSON or ICS export.
Supports scheduling based on the fertilizer and repot fields in each species' care card.
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any


# ── Fertilizer frequency parser ──────────────────────────────────────────────


def _parse_fertilizer(text: str) -> list[int]:
    """Return list of month numbers (1-12) when fertilizing is recommended.

    Handles common patterns found in species care data:
      - "Monthly in growing season" / "Monthly in spring/summer"
      - "Light monthly feed in growing season" / "Balanced feed every 3-4 weeks"
      - "Rarely; half-strength in spring"
      - "Sparse; spring only" / "Light feed in spring only"
      - "None to minimal" / "Dilute feed 2-3 times per year"
      - "Light nitrogen feed every 2-3 weeks"
    """
    text = text.strip().lower()
    if not text or text == "none" or text.startswith("none") or text.startswith("rarely"):
        # Rarely / none → fertilize once in spring
        return [4]

    # Check for "never" or "minimal"
    if "never" in text or "minimal" in text:
        return []

    # Identify growing-season window
    if "growing season" in text or "warm months" in text:
        start, end = 3, 10  # Mar – Oct
    elif "spring/summer" in text or "spring–summer" in text or "spring and summer" in text:
        start, end = 3, 8  # Mar – Aug
    elif "spring/fall" in text or "spring and fall" in text:
        start, end = 3, 10  # Mar – May, Sep – Oct
    elif "spring" in text and "summer" not in text:
        start, end = 3, 5  # Mar – May
    elif "summer" in text and "spring" not in text:
        start, end = 6, 8  # Jun – Aug
    else:
        # Default: year-round
        start, end = 1, 12

    # Determine frequency
    freq_days = 30  # default monthly

    # Check for "every N weeks" / "every N-M weeks"
    m = re.search(r"every\s+(\d+)\s*[-–]?\s*(\d+)?\s*(weeks|week|w)", text, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        m2_val = int(m.group(2)) if m.group(2) else n
        freq_days = max(n, m2_val) * 7  # use upper bound of range
        # Build months from day-based frequency
        months = []
        day_in_year = date(2026, start, 1)
        end_date = date(2026, end, 28)
        while day_in_year <= end_date:
            months.append(day_in_year.month)
            day_in_year += timedelta(days=freq_days)
        # Deduplicate and ensure we have at least some months
        return sorted(set(months))

    # "2-3 times per year" in growing season - distribute evenly
    m2 = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*(?:times?|[xX×])\s*(?:per|a)?\s*(?:year|season)", text, re.IGNORECASE)
    if m2:
        count_low = int(m2.group(1))
        count_high = int(m2.group(2))
        count = max(count_low, count_high)  # use higher bound for more frequent
        span = end - start + 1
        if count >= span:
            return list(range(start, end + 1))
        step = max(1, span // count)
        return list(range(start, end + 1, step))

    # "Monthly" / every month
    if "monthly" in text or "every month" in text:
        return list(range(start, end + 1))

    # "Weekly" in growing season - treat as frequent (every week)
    if "weekly" in text:
        # Weekly in growing season: approximately every month
        return list(range(start, end + 1))

    # "Rarely" or "None" - default to spring
    if "rarely" in text or text.strip() in ("none", ""):
        return [4]  # April

    # Default: once in mid-season
    mid = (start + end) // 2
    return [mid]


def _parse_repot(text: str) -> dict[str, Any]:
    """Parse a repot note into a structured schedule hint."""
    text = text.strip().lower()
    if not text or text in ("none", "never", "n/a", "not needed"):
        return {"recommended": False, "months": [], "note": text}

    # Default: repot annually in spring
    result: dict[str, Any] = {"recommended": True, "months": [3, 4, 5], "note": text}

    if "every" in text:
        m = re.search(r"every\s+(\d+)\s*(?:year|yr)", text)
        if m:
            result["every_years"] = int(m.group(1))
        else:
            result["every_years"] = 1
    else:
        result["every_years"] = 1

    # Season hints
    if "spring" in text and "summer" not in text and "fall" not in text:
        result["months"] = [3, 4, 5]
    elif "summer" in text:
        result["months"] = [6, 7, 8]
    elif "fall" in text or "autumn" in text:
        result["months"] = [9, 10, 11]
    elif "winter" in text:
        result["months"] = [12, 1, 2]

    return result


# ── Calendar generation ──────────────────────────────────────────────────────


def _fertilizer_months(species: dict[str, Any]) -> list[int]:
    """Return months (1-12) when this species should be fertilized."""
    care = species.get("care", {})
    fert_text = str(care.get("fertilizer", ""))
    return _parse_fertilizer(fert_text)


def generate_calendar(
    species_list: list[dict[str, Any]],
    year: int = 2026,
    include_repot: bool = True,
) -> list[dict[str, Any]]:
    """Generate a full calendar of care events (fertilize + repot) for a list of species.

    Returns a list of event dicts with keys:
        date, species_id, common_name, event_type, notes
    """
    events: list[dict[str, Any]] = []

    for species in species_list:
        sid = species.get("id", "unknown")
        common = species.get("common_name", sid)
        care = species.get("care", {})

        # ── Fertilize events ──
        fert_note = str(care.get("fertilizer", ""))
        for month in _fertilizer_months(species):
            # Schedule for the 1st of each recommended month
            event_date = date(year, month, 1)
            events.append({
                "date": event_date.isoformat(),
                "species_id": sid,
                "common_name": common,
                "event_type": "fertilize",
                "notes": fert_note,
            })

        # ── Repot events ──
        if include_repot:
            repot_note = str(care.get("repot", "Annual repotting in spring recommended"))
            repot_info = _parse_repot(repot_note)
            if repot_info["recommended"]:
                for month in repot_info["months"]:
                    event_date = date(year, month, 1)
                    events.append({
                        "date": event_date.isoformat(),
                        "species_id": sid,
                        "common_name": common,
                        "event_type": "repot",
                        "notes": repot_note,
                    })

    # Sort by date then species
    events.sort(key=lambda e: (e["date"], e["species_id"], e["event_type"]))
    return events


def export_json(events: list[dict[str, Any]], path: Path) -> None:
    """Write calendar events as a JSON array."""
    path.write_text(
        json.dumps(events, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def export_ics(events: list[dict[str, Any]], path: Path) -> None:
    """Write calendar events in iCalendar (.ics) format.

    Produces a basic VCALENDAR with VEVENT entries so the calendar
    can be imported into Google Calendar, Apple Calendar, etc.
    """
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PlantGuide//CarePlanner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, event in enumerate(events, 1):
        dt = event["date"].replace("-", "")  # YYYYMMDD
        uid = f"plantguide-{event['species_id']}-{event['event_type']}-{i}@plantguide"
        summary = f"[PlantGuide] {event['event_type'].title()}: {event['common_name']}"
        desc = event.get("notes", "")

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART;VALUE=DATE:{dt}",
            f"DTEND;VALUE=DATE:{dt}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


# ── Convenience: calendar for a whole catalog ────────────────────────────────


def generate_catalog_calendar(year: int = 2026) -> list[dict[str, Any]]:
    """Generate a care calendar for all species in the catalog."""
    from plantguide.data.loader import load_species_catalog
    return generate_calendar(load_species_catalog(), year=year)