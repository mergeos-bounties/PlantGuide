"""FastAPI surface for PlantGuide - POST /identify and GET /species/{id}/care (#9)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile

from plantguide import __version__
from plantguide.care.cards import care_card_for_species, watering_hint
from plantguide.data.loader import get_species_by_id, load_species_catalog
from plantguide.identify.pipeline import identify_from_tags
from plantguide.identify.vision import extract_visual_tags, identify_from_image

app = FastAPI(
    title="PlantGuide API",
    version=__version__,
    description="Photo/tag plant identification + species care guidance.",
)

TEMP_UPLOAD_DIR = Path("data/uploads")


@app.get("/api/health")
def health() -> dict[str, Any]:
    catalog = load_species_catalog()
    return {"ok": True, "service": "plantguide", "version": __version__, "species_count": len(catalog)}


@app.post("/api/identify")
async def api_identify(
    tags: str | None = Form(None),
    image: UploadFile | None = File(None),
    top_k: int = Query(3, ge=1, le=20),
) -> dict[str, Any]:
    if tags and image:
        raise HTTPException(400, "Provide either tags or image, not both.")
    if not tags and not image:
        raise HTTPException(400, "Provide tags (form field) or image (file upload).")

    if tags:
        try:
            return identify_from_tags(tags, top_k=top_k)
        except Exception as exc:
            raise HTTPException(500, str(exc)) from exc

    if image is None:
        raise HTTPException(400, "No image file provided.")

    ct = (image.content_type or "").lower()
    if ct not in {"image/jpeg", "image/png", "image/webp", "image/bmp"}:
        raise HTTPException(400, f"Unsupported type: {ct}")

    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe = Path(image.filename or "upload.jpg").name
    tmp = TEMP_UPLOAD_DIR / f"upload_{safe}"
    try:
        tmp.write_bytes(await image.read())
    except Exception as exc:
        raise HTTPException(500, f"Save failed: {exc}") from exc

    try:
        result = identify_from_image(tmp, top_k=top_k, with_care=True)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
    return result


@app.get("/api/species/{species_id}/care")
def api_species_care(species_id: str, season: str | None = Query(None)) -> dict[str, Any]:
    try:
        card = care_card_for_species(species_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    result: dict[str, Any] = {"species_id": species_id, "care": card}
    if season:
        try:
            result["watering"] = watering_hint(species_id, season=season)
        except KeyError:
            result["watering"] = {"error": f"season={season} unavailable"}
    return result


@app.get("/api/species")
def api_species_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    catalog = load_species_catalog()
    total = len(catalog)
    page = catalog[offset:offset + limit]
    return {
        "total": total, "offset": offset, "limit": limit, "count": len(page),
        "species": [
            {"id": s.get("id"), "common_name": s.get("common_name"),
             "scientific_name": s.get("scientific_name"),
             "tags": s.get("tags", []), "toxicity": s.get("toxicity", [])}
            for s in page
        ],
    }


@app.get("/api/species/search")
def api_species_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(15, ge=1, le=100),
) -> dict[str, Any]:
    query = q.strip().lower()
    hits: list[dict[str, Any]] = []
    for sp in load_species_catalog():
        blob = " ".join(
            [str(sp.get(k) or "") for k in ("id", "common_name", "scientific_name")]
            + (sp.get("tags") or [])
        ).lower()
        if query in blob:
            hits.append({
                "id": sp.get("id"), "common_name": sp.get("common_name"),
                "scientific_name": sp.get("scientific_name"), "tags": sp.get("tags", []),
            })
        if len(hits) >= limit:
            break
    return {"query": q, "count": len(hits), "results": hits}


@app.get("/api/species/{species_id}")
def api_species_get(species_id: str) -> dict[str, Any]:
    sp = get_species_by_id(species_id)
    if sp is None:
        raise HTTPException(404, f"Unknown species: {species_id!r}")
    return sp


@app.post("/api/vision/extract")
async def api_vision_extract(image: UploadFile = File(...)) -> dict[str, Any]:
    ct = (image.content_type or "").lower()
    if ct not in {"image/jpeg", "image/png", "image/webp", "image/bmp"}:
        raise HTTPException(400, f"Unsupported type: {ct}")

    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe = Path(image.filename or "leaf.jpg").name
    tmp = TEMP_UPLOAD_DIR / f"viz_{safe}"
    try:
        tmp.write_bytes(await image.read())
    except Exception as exc:
        raise HTTPException(500, f"Save failed: {exc}") from exc

    try:
        result = extract_visual_tags(tmp)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass

    return {
        "ok": True, "image": image.filename,
        "tags": result.get("tags", []),
        "features": result.get("features", {}),
        "source": result.get("source", "visual_heuristics"),
    }
