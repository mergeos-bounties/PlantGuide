import json
from pathlib import Path
from typing import List, Dict, Any

def load_species_data() -> List[Dict[str, Any]]:
    """Load all species data from JSON files."""
    species_dir = Path(__file__).parent.parent / "data" / "species"
    species_data = []

    for species_file in species_dir.glob("*.json"):
        with open(species_file, "r") as f:
            species_data.append(json.load(f))

    return species_data

def filter_pet_safe_plants() -> List[Dict[str, Any]]:
    """Filter and return only pet-safe plants."""
    species_data = load_species_data()
    pet_safe_plants = []

    for plant in species_data:
        if "toxicity" in plant and plant["toxicity"] == "none":
            pet_safe_plants.append(plant)

    return pet_safe_plants