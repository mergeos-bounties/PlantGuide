"""FastAPI routes for PlantGuide identify + care API.

Part of bounty #9 — FastAPI: POST /identify and GET /species/{id}/care.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from plantguide.data.loader import get_species_by_id
from plantguide.identify.pipeline import identify_from_tags

app = FastAPI(
    title="PlantGuide API",
    version="0.1.0",
    description="Plant species identification and care cards via trait tags.",
)


# ── Request / Response models ──────────────────────────────────────────

class IdentifyRequest(BaseModel):
    tags: list[str] = Field(
        ..., min_length=1,
        description="List of trait tags observed on the plant",
        examples=[["large leaves", "fenestrated", "climbing", "indoor"]],
    )
    top_k: int = Field(default=3, ge=1, le=20, description="Number of top matches")


class CareCard(BaseModel):
    species_id: str
    common_name: str
    scientific_name: str
    summary: str
    light: str
    water: str
    soil: str
    humidity: str
    temperature_c: str
    fertilizer: str
    toxicity: str
    common_issues: list[str]
    tips: list[str]


class MatchResult(BaseModel):
    species_id: str
    common_name: str
    scientific_name: str
    score: float
    matched_tags: list[str]
    species_only_tags: list[str]
    query_only_tags: list[str]
    explanation: str


class IdentifyResponse(BaseModel):
    query_tags: list[str]
    matches: list[MatchResult]
    model: str
    top_species_id: Optional[str] = None
    top_care: Optional[CareCard] = None


class ErrorResponse(BaseModel):
    error: str


# ── Routes ─────────────────────────────────────────────────────────────

@app.post(
    "/identify",
    response_model=IdentifyResponse,
    summary="Identify plant species from trait tags",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        200: {"description": "Top-k matching species with optional care card"},
    },
)
def identify(
    body: IdentifyRequest,
    with_care: bool = Query(default=True, description="Include care card for top match"),
) -> dict[str, Any]:
    """Given a list of trait tags, return the top-k matching species."""
    result = identify_from_tags(body.tags, top_k=body.top_k, with_care=with_care)
    if not result.get("matches"):
        return {
            "query_tags": body.tags,
            "matches": [],
            "model": "ToyPlantIdentifier",
            "top_species_id": None,
        }

    top_care = None
    top_species_id = None
    if with_care and result.get("top_care"):
        care = result["top_care"]
        top_species_id = result.get("top_species_id")
        top_care = CareCard(
            species_id=care.get("species_id", ""),
            common_name=care.get("common_name", ""),
            scientific_name=care.get("scientific_name", ""),
            summary=care.get("summary", ""),
            light=care.get("light", ""),
            water=care.get("water", ""),
            soil=care.get("soil", ""),
            humidity=care.get("humidity", ""),
            temperature_c=care.get("temperature_c", ""),
            fertilizer=care.get("fertilizer", ""),
            toxicity=care.get("toxicity", ""),
            common_issues=care.get("common_issues", []),
            tips=care.get("tips", []),
        )

    matches = []
    for m in result["matches"]:
        matches.append(MatchResult(
            species_id=m["species_id"],
            common_name=m.get("common_name", ""),
            scientific_name=m.get("scientific_name", ""),
            score=m.get("score", 0.0),
            matched_tags=m.get("matched_tags", []),
            species_only_tags=m.get("species_only_tags", []),
            query_only_tags=m.get("query_only_tags", []),
            explanation=m.get("explanation", ""),
        ))

    return IdentifyResponse(
        query_tags=body.tags,
        matches=matches,
        model="ToyPlantIdentifier",
        top_species_id=top_species_id,
        top_care=top_care,
    ).model_dump()


@app.get(
    "/species/{species_id}/care",
    response_model=CareCard,
    summary="Get care card for a specific species",
    responses={
        404: {"model": ErrorResponse, "description": "Species not found"},
    },
)
def get_care_card(species_id: str) -> dict[str, Any]:
    """Return full care card for a plant species by its ID."""
    from plantguide.care.cards import care_card_for_species

    try:
        card = care_card_for_species(species_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Species '{species_id}' not found",
        )
    if not card or not card.get("species_id"):
        raise HTTPException(
            status_code=404,
            detail=f"Species '{species_id}' not found",
        )

    return CareCard(
        species_id=card.get("species_id", ""),
        common_name=card.get("common_name", ""),
        scientific_name=card.get("scientific_name", ""),
        summary=card.get("summary", ""),
        light=card.get("light", ""),
        water=card.get("water", ""),
        soil=card.get("soil", ""),
        humidity=card.get("humidity", ""),
        temperature_c=card.get("temperature_c", ""),
        fertilizer=card.get("fertilizer", ""),
        toxicity=card.get("toxicity", ""),
        common_issues=card.get("common_issues", []),
        tips=card.get("tips", []),
    ).model_dump()


@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
