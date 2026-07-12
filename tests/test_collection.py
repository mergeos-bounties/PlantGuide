from __future__ import annotations

import importlib

import pytest

from plantguide.collection import add_plant, due_soon, list_plants, water_plant


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Point the collection store at a temp dir so tests don't touch real data."""
    monkeypatch.setenv("PLANTGUIDE_COLLECTION_DIR", str(tmp_path))
    # Reload store module so it picks up the env override for _collection_dir.
    import plantguide.collection.store as store

    importlib.reload(store)
    yield
    importlib.reload(store)


def test_add_plant_basic():
    rec = add_plant("aloe_vera", 14)
    assert rec["id"] == "PlantGuide#1"
    assert rec["species"] == "aloe_vera"
    assert rec["water_every_days"] == 14
    assert "last_watered" in rec


def test_add_plant_sequential_ids():
    a = add_plant("aloe_vera", 14)
    b = add_plant("pothos_golden", 7)
    assert a["id"] == "PlantGuide#1"
    assert b["id"] == "PlantGuide#2"


def test_add_plant_invalid_interval():
    with pytest.raises(ValueError):
        add_plant("aloe_vera", 0)


def test_add_plant_with_nickname_and_note():
    rec = add_plant("monstera_deliciosa", 10, nickname="Monsty", note="bright corner")
    assert rec["nickname"] == "Monsty"
    assert rec["note"] == "bright corner"


def test_list_plants_persists():
    add_plant("aloe_vera", 14)
    add_plant("zz_plant", 21)
    plants = list_plants()
    assert len(plants) == 2
    ids = {p["id"] for p in plants}
    assert ids == {"PlantGuide#1", "PlantGuide#2"}


def test_water_plant_updates_last_watered():
    rec = add_plant("aloe_vera", 14, last_watered="2026-07-01")
    updated = water_plant(rec["id"], on_date="2026-07-10")
    assert updated["last_watered"] == "2026-07-10"


def test_water_plant_unknown_id():
    with pytest.raises(KeyError):
        water_plant("PlantGuide#999")


def test_due_soon_finds_overdue_and_upcoming():
    add_plant("aloe_vera", 14, last_watered="2026-07-01")  # due 07-15
    add_plant("zz_plant", 21, last_watered="2026-07-12")   # due 08-02
    due = due_soon(within_days=3, as_of="2026-07-14")
    assert len(due) == 1
    assert due[0]["id"] == "PlantGuide#1"
    assert due[0]["days_left"] == 1


def test_due_soon_empty_when_none_due():
    add_plant("zz_plant", 21, last_watered="2026-07-12")  # due far out
    assert due_soon(within_days=3, as_of="2026-07-14") == []


def test_due_soon_sorted():
    add_plant("a", 7, last_watered="2026-07-01")   # due 07-08
    add_plant("b", 7, last_watered="2026-07-02")   # due 07-09
    due = due_soon(within_days=10, as_of="2026-07-07")
    assert [d["id"] for d in due] == ["PlantGuide#1", "PlantGuide#2"]
