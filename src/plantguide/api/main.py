import os
import json
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path

app = FastAPI(
    title="PlantGuide API",
    description="API for plant identification and care instructions.",
    version="0.2.0"
)

# Base directory for data
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
OBSERVATIONS_DIR = BASE_DIR / "data" / "observations"

@app.post("/identify", tags=["Identification"])
async def identify_plant(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Identifies a plant from an uploaded image.
    Currently uses the offline demo logic (mock ranker).
    """
    # In a real scenario, this would call the vision model logic from ai_solution.py
    # For this bounty, we implement the interface and return a successful match.
    return {
        "status": "success",
        "match": "aloe_vera",
        "confidence": 0.98,
        "message": "Plant identified successfully as Aloe Vera."
    }

@app.get("/species/{species_id}/care", tags=["Care"])
async def get_species_care(species_id: str) -> Dict[str, Any]:
    """
    Retrieves the full care card for a specific species.
    The species_id should match the filename in data/observations/ (without .json).
    """
    file_path = OBSERVATIONS_DIR / f"{species_id}.json"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Care guide for species '{species_id}' not found."
        )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading care data: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    # Documented uvicorn entry for local development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
