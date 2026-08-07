"""FastAPI routes for the PlantGuide REST API.

Mounted at ``/`` under ``plantguide.api.app``.  Start with::

    uvicorn plantguide.api.routes:app --reload

Or via the CLI entry-point::

    plantguide serve

Endpoints
---------
``POST /identify``
    Submit plant observation tags or a sample-id and receive species matches.
``GET /species/{species_id}/care``
    Return the full offline care card for a species.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from plantguide.care.cards import care_card_for_species
from plantguide.identify.pipeline import identify_from_tags

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class IdentifyRequest(BaseModel):
    """Payload for ``POST /identify``."""

    tags: list[str] = Field(
        default_factory=list,
        description="List of observation tags (e.g. ['green', 'trailing', 'indoor'])",
        examples=[["green", "trailing", "indoor"]],
    )
    top_k: int = Field(default=3, ge=1, le=20, description="Number of top matches to return")


class MatchItem(BaseModel):
    """A single species match returned by the identifier."""

    species_id: str
    common_name: str
    scientific_name: str
    score: float
    tag_overlap: list[str] = Field(default_factory=list)


class IdentifyResponse(BaseModel):
    """Response for ``POST /identify``."""

    query_tags: list[str]
    matches: list[MatchItem]
    model: str


class CareCard(BaseModel):
    """Per-species care guidance."""

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
    common_issues: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    """Standard error response."""

    detail: str


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PlantGuide API",
    description="Plant identification and species care guidance",
    version="0.2.51",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/identify", response_model=IdentifyResponse, responses={400: {"model": ErrorDetail}})
async def identify(request: IdentifyRequest) -> dict[str, Any]:
    """Identify plant species from a list of observation tags.

    Returns ranked matches with scores and shared-tag overlap.
    """
    if not request.tags:
        raise HTTPException(status_code=400, detail="At least one tag is required")
    raw = identify_from_tags(request.tags, top_k=request.top_k, with_care=False)
    matches: list[dict[str, Any]] = []
    for m in raw.get("matches", [])[: request.top_k]:
        matches.append(
            MatchItem(
                species_id=str(m.get("species_id", "")),
                common_name=str(m.get("common_name", "")),
                scientific_name=str(m.get("scientific_name", "")),
                score=round(float(m.get("score", 0.0)), 4),
                tag_overlap=sorted(str(t) for t in (m.get("tag_overlap") or [])),
            ).model_dump()
        )
    return IdentifyResponse(
        query_tags=request.tags,
        matches=matches,
        model=raw.get("model", "ToyPlantIdentifier"),
    ).model_dump()


@app.get(
    "/species/{species_id}/care",
    response_model=CareCard,
    responses={404: {"model": ErrorDetail}},
)
async def species_care(species_id: str) -> dict[str, Any]:
    """Return the offline care card for a catalog species."""
    try:
        card = care_card_for_species(species_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown species: {species_id!r}")
    return CareCard(
        species_id=str(card.get("species_id", "")),
        common_name=str(card.get("common_name", "")),
        scientific_name=str(card.get("scientific_name", "")),
        summary=str(card.get("summary", "")),
        light=str(card.get("light", "")),
        water=str(card.get("water", "")),
        soil=str(card.get("soil", "")),
        humidity=str(card.get("humidity", "")),
        temperature_c=str(card.get("temperature_c", "")),
        fertilizer=str(card.get("fertilizer", "")),
        toxicity=str(card.get("toxicity", "")),
        common_issues=list(card.get("common_issues") or []),
        tips=list(card.get("tips") or []),
    ).model_dump()
