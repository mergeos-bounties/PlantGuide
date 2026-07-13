"""Photo identify + care demo tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from plantguide.identify.pipeline import identify_from_image
from plantguide.identify.vision import list_demo_photos, photo_care_demo


PHOTOS = Path("data/samples/photos")


@pytest.fixture(scope="module", autouse=True)
def ensure_demo_photos() -> None:
    man = PHOTOS / "manifest.json"
    if not man.is_file() or not any(PHOTOS.glob("*.jpg")):
        import runpy
        from pathlib import Path

        script = Path(__file__).resolve().parents[1] / "scripts" / "generate_demo_photos.py"
        runpy.run_path(str(script), run_name="__main__")
    assert man.is_file()


def test_demo_photos_listed() -> None:
    photos = list_demo_photos()
    assert len(photos) >= 3
    assert all(p.get("expected_species") for p in photos)


def test_identify_image_monstera_demo() -> None:
    path = PHOTOS / "monstera_demo.jpg"
    assert path.is_file()
    result = identify_from_image(path, top_k=3)
    assert result["mode"] == "image"
    assert result["matches"]
    assert result["matches"][0]["species_id"] == "monstera_deliciosa"
    assert result.get("hit_top1") is True
    assert "top_care" in result
    assert result["top_care"]["species_id"] == "monstera_deliciosa"
    assert result["top_care"].get("water")


def test_photo_care_demo_end_to_end() -> None:
    report = photo_care_demo(PHOTOS / "snake_demo.jpg")
    assert report["ok"] is True
    assert report["species_id"] == "snake_plant"
    assert report["care"]["light"]
    assert report["watering"]["seasonal_note"]
    assert report["identify"]["hit_top1"] is True
    assert len(report["how_to"]) >= 4


def test_identify_image_all_demo_hit_rate() -> None:
    photos = [p for p in list_demo_photos() if p.get("exists")]
    assert len(photos) >= 4
    hits = 0
    for p in photos:
        r = identify_from_image(Path(p["path"]), top_k=1)
        if r.get("hit_top1"):
            hits += 1
    assert hits >= len(photos) - 1  # allow one miss
