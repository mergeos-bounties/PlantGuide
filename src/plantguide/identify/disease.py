"""Simple disease / symptom tag matcher against species common issues."""

from __future__ import annotations

from plantguide.data.loader import list_species_files, load_species


# symptom keyword → normalized issue labels
SYMPTOM_MAP: dict[str, list[str]] = {
    "yellow": ["yellow leaves", "chlorosis", "yellowing"],
    "yellowing": ["yellow leaves", "chlorosis"],
    "brown": ["brown tips", "leaf scorch", "browning"],
    "spots": ["leaf spots", "fungal spots"],
    "soft": ["root rot", "soft leaves", "mushy"],
    "rot": ["root rot", "stem rot"],
    "droop": ["wilting", "drooping"],
    "wilt": ["wilting", "underwatering"],
    "crispy": ["underwatering", "low humidity", "brown tips"],
    "mold": ["powdery mildew", "fungal"],
    "mildew": ["powdery mildew"],
    "bugs": ["pests", "spider mites", "mealybugs"],
    "mites": ["spider mites", "pests"],
    "leggy": ["leggy growth", "insufficient light"],
}


def match_diseases(symptoms: str | list[str], top_k: int = 5) -> dict:
    """Rank species by overlap of symptoms with care.common_issues + tags."""
    if isinstance(symptoms, str):
        raw = [s.strip().lower() for s in symptoms.replace(";", ",").split(",") if s.strip()]
        # also split spaces for free text
        if len(raw) == 1 and " " in raw[0]:
            raw = raw[0].split()
    else:
        raw = [str(s).strip().lower() for s in symptoms if str(s).strip()]

    expanded: set[str] = set()
    for s in raw:
        expanded.add(s)
        for key, vals in SYMPTOM_MAP.items():
            if key in s or s in key:
                expanded.update(vals)

    ranked: list[dict] = []
    for path in list_species_files():
        sp = load_species(path)
        issues = [str(x).lower() for x in (sp.get("care") or {}).get("common_issues") or []]
        tags = [str(t).lower() for t in (sp.get("tags") or [])]
        hay = " ".join(issues + tags)
        hits = sorted({e for e in expanded if e in hay or any(e in i for i in issues)})
        if not hits and not issues:
            continue
        score = len(hits) / max(1, len(expanded))
        if score <= 0 and not hits:
            continue
        ranked.append(
            {
                "species_id": sp.get("id"),
                "common_name": sp.get("common_name"),
                "score": round(score, 3),
                "matched": hits,
                "common_issues": (sp.get("care") or {}).get("common_issues") or [],
            }
        )
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return {
        "query": raw,
        "expanded": sorted(expanded),
        "matches": ranked[: max(1, top_k)],
        "model": "DiseaseTagMatcher",
    }
