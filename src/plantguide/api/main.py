"""PlantGuide FastAPI application."""

from fastapi import FastAPI

app = FastAPI(
    title="PlantGuide API",
    description="Plant identification and species care endpoints.",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/species/{species_id}")
async def get_species(species_id: str) -> dict:
    """Get species information by ID."""
    return {
        "species_id": species_id,
        "message": "Species endpoint stub - see PlantGuide SDK for full implementation.",
    }
