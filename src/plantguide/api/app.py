"""FastAPI app for PlantGuide: plant identification and care guidance."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from plantguide.care.cards import care_card_for_species
from plantguide.data.loader import list_species_files, load_species
from plantguide.identify.pipeline import identify_from_image, identify_from_tags

app = FastAPI(
    title="PlantGuide API",
    description="Identify plants from photos/tags and retrieve species care guidance.",
    version="0.1.0",
)


# ── Request / Response models ──────────────────────────────────────────

class IdentifyTagsRequest(BaseModel):
    """Identify a plant from descriptive tags."""
    tags: list[str]
    top_k: int = 3
    with_care: bool = True


class IdentifyResponse(BaseModel):
    """Identification result with top matches and optional care card."""
    query_tags: list[str] = []
    matches: list[dict[str, Any]] = []
    model: str = ""
    top_care: dict[str, Any] | None = None
    top_species_id: str | None = None
    source: str | None = None


class CareCardResponse(BaseModel):
    """Care guidance for a species."""
    species_id: str
    care: dict[str, Any] | None = None
    found: bool = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    species_count: int = 0
    version: str = ""


# ── Routes ─────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        species_count=len(list_species_files()),
        version="0.2.51",
    )


@app.post("/identify", response_model=IdentifyResponse, tags=["identify"])
async def identify(
    file: UploadFile | None = File(None, description="Plant photo (JPEG/PNG)"),
    tags: str | None = Form(None, description="Comma-separated descriptive tags"),
    top_k: int = Form(3, ge=1, le=20, description="Number of top matches to return"),
    with_care: bool = Form(True, description="Include care card for top match"),
) -> IdentifyResponse:
    """
    Identify a plant from a photo or descriptive tags.

    Provide either a photo file or comma-separated tags (or both).
    Returns the top-k matching species with optional care guidance.
    """
    tag_list: list[str] = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    if file and file.filename:
        # Identify from image
        contents = await file.read()
        temp_path = Path("/tmp") / f"plantguide_{file.filename}"
        temp_path.write_bytes(contents)
        try:
            result = identify_from_image(temp_path, top_k=top_k, with_care=with_care)
        finally:
            temp_path.unlink(missing_ok=True)
        return IdentifyResponse(**result)
    elif tag_list:
        # Identify from tags
        result = identify_from_tags(tag_list, top_k=top_k, with_care=with_care)
        return IdentifyResponse(**result)
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either a photo file (file) or descriptive tags (tags).",
        )


@app.get("/species/{species_id}/care", response_model=CareCardResponse, tags=["care"])
async def get_species_care(species_id: str) -> CareCardResponse:
    """
    Get care guidance for a specific species.

    The `species_id` should match a species file in the catalog
    (e.g. `monstera_deliciosa`, `aloe_vera`).
    """
    card = care_card_for_species(species_id)
    if card is None or card.get("species_id") is None:
        # Check if species exists in catalog
        all_species = list_species_files()
        ids = [p.stem for p in all_species]
        raise HTTPException(
            status_code=404,
            detail=f"Species '{species_id}' not found. Available species: {len(ids)} in catalog.",
        )
    return CareCardResponse(
        species_id=species_id,
        care=card,
        found=True,
    )


@app.get("/species", tags=["species"])
async def list_species() -> list[dict[str, Any]]:
    """List all species in the catalog with basic info."""
    result = []
    for path in list_species_files():
        sp = load_species(path)
        result.append({
            "species_id": path.stem,
            "common_name": sp.get("common_name", ""),
            "scientific_name": sp.get("scientific_name", ""),
            "tags": (sp.get("tags") or [])[:5],
        })
    return sorted(result, key=lambda x: x["species_id"])