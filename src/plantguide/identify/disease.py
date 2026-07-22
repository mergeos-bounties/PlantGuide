"""Offline symptom matcher for common plant health issues."""

from __future__ import annotations

import json
from pathlib import Path

from plantguide.config import data_dir


DEFAULT_RULES_PATH = data_dir() / "disease" / "symptom_rules.json"
DISCLAIMER = (
    "Educational guidance only; symptoms can have multiple causes. Isolate affected plants, "
    "follow product labels, and ask a qualified horticulture professional when damage is severe "
    "or the cause is uncertain."
)


def _normalize_symptoms(symptoms: str | list[str]) -> list[str]:
    values = symptoms.replace(";", ",").split(",") if isinstance(symptoms, str) else symptoms
    return [" ".join(str(value).strip().lower().split()) for value in values if str(value).strip()]


def _load_rules(path: Path = DEFAULT_RULES_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("issues") or [])


def _matches(query: str, symptom: str) -> bool:
    if query in symptom or symptom in query:
        return True
    query_words = set(query.split())
    symptom_words = set(symptom.split())
    return len(query_words & symptom_words) >= 2


def match_diseases(symptoms: str | list[str], top_k: int = 5) -> dict:
    """Suggest likely issues and remedies for comma-separated symptom tags."""
    query = _normalize_symptoms(symptoms)
    ranked: list[dict] = []

    for rule in _load_rules():
        known_symptoms = _normalize_symptoms(rule.get("symptoms") or [])
        matched = [
            observed
            for observed in query
            if any(_matches(observed, known) for known in known_symptoms)
        ]
        if not matched:
            continue
        ranked.append(
            {
                "issue_id": rule["id"],
                "name": rule["name"],
                "score": round(len(matched) / max(1, len(query)), 3),
                "matched_symptoms": matched,
                "likely_causes": rule["likely_causes"],
                "remedies": rule["remedies"],
                "when_to_escalate": rule["when_to_escalate"],
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["name"]))
    return {
        "query": query,
        "matches": ranked[: max(1, top_k)],
        "disclaimer": DISCLAIMER,
        "model": "DiseaseTagMatcher",
    }
