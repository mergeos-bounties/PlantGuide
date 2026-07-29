import json
import os
from typing import Dict, List, Optional, Any

DISCLAIMER_TEXT = (
    "DISCLAIMER: Symptom matching recommendations are for informational purposes only. "
    "Always confirm diagnosis before applying chemical treatments, and consult a local "
    "botanist or agricultural extension office for severe infestations."
)

class SymptomMatcher:
    def __init__(self, fixtures_path: Optional[str] = None):
        """
        Initialize the symptom matcher with database fixtures.
        """
        if fixtures_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            fixtures_path = os.path.join(base_dir, "fixtures", "diseases_pests.json")

        self.issues = self._load_fixtures(fixtures_path)

    def _load_fixtures(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fixture file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize_tag(self, tag: str) -> str:
        return tag.strip().lower() if tag else ""

    def match_symptoms(
        self,
        symptom_tags: Optional[List[str]],
        min_score: float = 0.1,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Matches user input symptom tags against issue database.

        Returns matching issues ordered by confidence along with remedies & disclaimers.
        """
        if not symptom_tags:
            return {
                "matched_issues": [],
                "disclaimer": DISCLAIMER_TEXT,
                "input_tags": []
            }

        cleaned_input_tags = list({
            self.normalize_tag(t) for t in symptom_tags if t and isinstance(t, str) and self.normalize_tag(t)
        })

        if not cleaned_input_tags:
            return {
                "matched_issues": [],
                "disclaimer": DISCLAIMER_TEXT,
                "input_tags": []
            }

        input_set = set(cleaned_input_tags)
        results = []

        for issue in self.issues:
            issue_tags = [self.normalize_tag(t) for t in issue.get("tags", [])]
            issue_set = set(issue_tags)

            intersection = input_set.intersection(issue_set)
            if not intersection:
                continue

            # Jaccard index + recall score calculation
            jaccard = len(intersection) / len(input_set.union(issue_set))
            recall = len(intersection) / len(input_set)
            score = round((0.6 * recall) + (0.4 * jaccard), 2)

            if score >= min_score:
                results.append({
                    "id": issue["id"],
                    "name": issue["name"],
                    "category": issue["category"],
                    "confidence_score": score,
                    "matched_symptoms": list(intersection),
                    "remedies": issue.get("remedies", [])
                })

        # Sort by confidence score descending
        results.sort(key=lambda x: x["confidence_score"], reverse=True)

        return {
            "matched_issues": results[:limit],
            "disclaimer": DISCLAIMER_TEXT,
            "input_tags": cleaned_input_tags
        }
