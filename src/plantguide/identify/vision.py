"""Offline photo → trait tags → species ID (demo vision, no network).

Pipeline:
1. Prefer sidecar / demo manifest labels when present (license-safe fixtures).
2. Else extract simple visual tags from RGB stats (green ratio, variegation, shape).
3. Match with ToyPlantIdentifier Jaccard ranking.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from plantguide.care.cards import care_card_for_species
from plantguide.config import SAMPLES_DIR
from plantguide.models.toy import ToyPlantIdentifier

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
PHOTOS_DIR = SAMPLES_DIR / "photos"


def photos_manifest_path() -> Path:
    return PHOTOS_DIR / "manifest.json"


def load_photos_manifest() -> dict[str, Any]:
    path = photos_manifest_path()
    if not path.is_file():
        return {"version": 1, "photos": []}
    return json.loads(path.read_text(encoding="utf-8"))


def list_demo_photos() -> list[dict[str, Any]]:
    data = load_photos_manifest()
    out: list[dict[str, Any]] = []
    for item in data.get("photos") or []:
        name = str(item.get("file") or "")
        path = PHOTOS_DIR / name
        entry = dict(item)
        entry["path"] = str(path)
        entry["exists"] = path.is_file()
        out.append(entry)
    return out


def _load_rgb_array(path: Path) -> np.ndarray:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            'Photo identify needs Pillow. Install: pip install -e ".[vision]" or pip install Pillow'
        ) from exc
    img = Image.open(path).convert("RGB")
    img = img.resize((96, 96))
    return np.asarray(img, dtype=np.float32) / 255.0


def extract_visual_tags(path: Path) -> dict[str, Any]:
    """Derive coarse plant trait tags from image RGB / layout heuristics."""
    arr = _load_rgb_array(path)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    green_mask = (g > r + 0.04) & (g > b + 0.02) & (g > 0.18)
    green_ratio = float(green_mask.mean())
    mean_g = float(g.mean())
    mean_r = float(r.mean())
    mean_b = float(b.mean())
    # variegation: high channel variance in mid-brightness pixels
    var = float(np.var(arr, axis=2).mean())
    # center vs edge green (trailing vs compact)
    h, w = green_mask.shape
    cy0, cy1 = h // 4, 3 * h // 4
    cx0, cx1 = w // 4, 3 * w // 4
    center_g = float(green_mask[cy0:cy1, cx0:cx1].mean()) if green_ratio > 0 else 0.0
    edge_g = float(green_mask.mean()) - center_g * 0.25

    tags: list[str] = ["indoor"]
    if green_ratio > 0.12:
        tags.append("leafy")
    if green_ratio > 0.28:
        tags.append("large leaves")
    if mean_g > 0.35 and mean_r < 0.45:
        tags.append("tropical")
    if mean_g < 0.28 and mean_r > 0.22:
        tags.append("succulent")
        tags.append("drought")
    if var > 0.012:
        tags.append("variegated")
    if center_g > 0.35 and edge_g < 0.2:
        tags.append("upright")
    if edge_g > 0.15 and center_g < 0.45:
        tags.append("trailing")
        tags.append("climbing")
    # fenestration proxy: dark holes inside green region
    if green_ratio > 0.2:
        dark = (r + g + b) / 3.0 < 0.22
        holes = float((dark & green_mask).mean()) if green_ratio else 0.0
        if holes > 0.02 or (var > 0.018 and green_ratio > 0.25):
            tags.append("fenestrated leaves")
            tags.append("aroid")
    if mean_b > mean_r and mean_g > 0.3:
        tags.append("shade")
    if mean_g > 0.4 and mean_r < 0.35:
        tags.append("feathery")

    # de-dupe preserve order
    seen: set[str] = set()
    unique: list[str] = []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            unique.append(t)

    return {
        "tags": unique,
        "features": {
            "green_ratio": round(green_ratio, 4),
            "mean_rgb": [round(mean_r, 3), round(mean_g, 3), round(mean_b, 3)],
            "color_variance": round(var, 5),
            "center_green": round(center_g, 4),
        },
        "source": "visual_heuristics",
    }


def resolve_demo_labels(path: Path) -> dict[str, Any] | None:
    """If path is a bundled demo photo, return tags + expected_species."""
    name = path.name.lower()
    for item in list_demo_photos():
        if str(item.get("file") or "").lower() == name:
            return {
                "tags": list(item.get("tags") or []),
                "expected_species": item.get("expected_species"),
                "source": "demo_manifest",
                "label": item.get("label") or name,
            }
    # sidecar JSON next to image: photo.jpg.json or photo.json
    for side in (path.with_suffix(path.suffix + ".json"), path.with_suffix(".json")):
        if side.is_file() and side != path:
            data = json.loads(side.read_text(encoding="utf-8"))
            return {
                "tags": list(data.get("tags") or []),
                "expected_species": data.get("expected_species"),
                "source": f"sidecar:{side.name}",
                "label": data.get("label") or path.stem,
            }
    return None


def identify_from_image(
    path: Path,
    top_k: int = 3,
    *,
    with_care: bool = True,
    prefer_demo_labels: bool = True,
) -> dict[str, Any]:
    """Identify plant species from a photo path (offline)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in IMAGE_EXTS:
        raise ValueError(f"unsupported image type {path.suffix!r}; use {sorted(IMAGE_EXTS)}")

    demo = resolve_demo_labels(path) if prefer_demo_labels else None
    visual = extract_visual_tags(path)

    if demo and demo.get("tags"):
        tags = list(demo["tags"])
        tag_source = demo["source"]
    else:
        tags = list(visual["tags"])
        tag_source = visual["source"]
        # merge a few visual tags into demo for richness
        if demo:
            tags = list(dict.fromkeys(list(demo.get("tags") or []) + tags))

    matches = ToyPlantIdentifier().identify(tags, top_k=top_k)
    result: dict[str, Any] = {
        "mode": "image",
        "image": str(path),
        "image_name": path.name,
        "query_tags": tags,
        "tag_source": tag_source,
        "visual_features": visual.get("features"),
        "matches": matches,
        "model": "ToyPlantIdentifier+visual_heuristics",
    }
    if demo and demo.get("expected_species"):
        expected = str(demo["expected_species"])
        result["expected_species"] = expected
        if matches:
            result["hit_top1"] = str(matches[0].get("species_id") or "").lower() == expected.lower()
    if with_care and matches:
        result["top_care"] = care_card_for_species(str(matches[0]["species_id"]))
        result["top_species_id"] = matches[0]["species_id"]
    return result


def photo_care_demo(path: Path | None = None, top_k: int = 3) -> dict[str, Any]:
    """End-to-end: photo → ID → care card (+ watering + SVG path if written)."""
    if path is None:
        photos = [p for p in list_demo_photos() if p.get("exists")]
        if not photos:
            raise FileNotFoundError(
                "No demo photos. Run: python scripts/generate_demo_photos.py"
            )
        path = Path(photos[0]["path"])
    path = Path(path)
    result = identify_from_image(path, top_k=top_k, with_care=True)
    species_id = result.get("top_species_id")
    care = result.get("top_care")
    from plantguide.care.cards import watering_hint

    water = watering_hint(str(species_id), season="summer") if species_id else None
    return {
        "ok": True,
        "demo": "photo_identify_and_care",
        "image": str(path),
        "species_id": species_id,
        "common_name": (care or {}).get("common_name"),
        "identify": {
            "query_tags": result.get("query_tags"),
            "tag_source": result.get("tag_source"),
            "matches": result.get("matches"),
            "hit_top1": result.get("hit_top1"),
            "expected_species": result.get("expected_species"),
        },
        "care": care,
        "watering": water,
        "how_to": [
            "1. Take or pick a leaf/plant photo (JPG/PNG)",
            "2. plantguide identify image -i <photo>",
            "3. plantguide care show -s <species_id>",
            "4. plantguide care water -s <species_id> --season summer",
            "5. plantguide care svg -s <species_id>",
        ],
    }
