from typing import Dict, Any, Optional, List
from symptom_matcher import SymptomMatcher

def show_care_details(
    plant_id: str,
    care_schedule: Dict[str, Any],
    symptom_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Renders plant care show details with optional symptom diagnosis matching.

    Backward-compatible entry point for displaying plant care instructions.
    """
    care_details = {
        "plant_id": plant_id,
        "care_schedule": care_schedule,
        "diagnosis": None
    }

    if symptom_tags:
        matcher = SymptomMatcher()
        care_details["diagnosis"] = matcher.match_symptoms(symptom_tags)

    return care_details
