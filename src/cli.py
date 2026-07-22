import argparse
import json
from pathlib import Path
from typing import List, Optional

from plantguide.filters import filter_pet_safe_plants
from plantguide.identify import identify_plant
from plantguide.care import get_care_instructions

def demo_photo(args: argparse.Namespace) -> None:
    """Run the full demo pipeline: identify plant from photo and show care instructions."""
    # ... existing code ...

def identify_image(args: argparse.Namespace) -> None:
    """Identify a plant from an image file."""
    # ... existing code ...

def show_care(args: argparse.Namespace) -> None:
    """Show care instructions for a specific plant species."""
    # ... existing code ...

def water_care(args: argparse.Namespace) -> None:
    """Show watering instructions for a specific plant species."""
    # ... existing code ...

def list_demo_photos(args: argparse.Namespace) -> None:
    """List all demo plant photos."""
    # ... existing code ...

def list_pet_safe_plants(args: argparse.Namespace) -> None:
    """List all pet-safe plants in the catalog."""
    pet_safe_plants = filter_pet_safe_plants()
    for plant in pet_safe_plants:
        print(f"{plant['common_name']} ({plant['scientific_name']}) - Toxicity: {plant['toxicity']}")

def main() -> None:
    parser = argparse.ArgumentParser(description="PlantGuide CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ... existing subparsers ...

    # Add new subparser for pet-safe plants
    pet_safe_parser = subparsers.add_parser("pet-safe", help="List pet-safe plants")
    pet_safe_parser.set_defaults(func=list_pet_safe_plants)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()