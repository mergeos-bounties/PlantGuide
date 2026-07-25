from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

from plantguide.care.cards import care_card_for_species
from plantguide.identify.pipeline import identify_from_tags

app = FastAPI(
    title="PlantGuide API",
    description="Plant identification and care card API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── Request / Response models ──────────────────────────────────────────────


class IdentifyRequest(BaseModel):
    tags: list[str] = Field(..., min_length=1, description="Plant trait tags (e.g. ['succulent', 'green', 'indoor'])")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of top matches to return")

    @validator("tags")
    def tags_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one tag is required")
        return v


class IdentifyResponse(BaseModel):
    query_tags: list[str]
    matches: list[dict]
    top_care: dict | None = None
    top_species_id: str | None = None
    model: str = "ToyPlantIdentifier"


class CareCardResponse(BaseModel):
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


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


# ── Endpoints ──────────────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@app.post("/identify", response_model=IdentifyResponse, tags=["identify"])
async def identify(body: IdentifyRequest) -> IdentifyResponse:
    """Identify a plant by trait tags and return top matches with care card."""
    result = identify_from_tags(body.tags, top_k=body.top_k, with_care=True)
    return IdentifyResponse(
        query_tags=result.get("query_tags", body.tags),
        matches=result.get("matches", []),
        top_care=result.get("top_care"),
        top_species_id=result.get("top_species_id"),
        model=result.get("model", "ToyPlantIdentifier"),
    )


@app.get("/species/{species_id}/care", response_model=CareCardResponse, tags=["care"])
async def care_card(species_id: str) -> CareCardResponse:
    """Get care card for a specific species."""
    try:
        card = care_card_for_species(species_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Species not found: {species_id!r}")
    return CareCardResponse(**card)


# ── Entry point ────────────────────────────────────────────────────────────


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the PlantGuide API server.

    Usage:
        python -m plantguide.api.app
        # or: uvicorn plantguide.api.app:app --host 127.0.0.1 --port 8000
    """
    import uvicorn

    uvicorn.run("plantguide.api.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    serve()