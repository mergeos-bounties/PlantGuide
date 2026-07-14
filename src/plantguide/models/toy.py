from __future__ import annotations

from plantguide.data.loader import load_species_catalog


class ToyPlantIdentifier:
    """
    Offline demo identifier: Jaccard similarity on trait tags.

    Vision / embedding models replace this via bounties.
    """

    def __init__(self, catalog: list[dict] | None = None):
        self.catalog = catalog if catalog is not None else load_species_catalog()

    def identify(self, tags: list[str], top_k: int = 3) -> list[dict]:
        observed = {_norm(t) for t in tags if str(t).strip()}
        if not observed:
            return []
        ranked: list[dict] = []
        for species in self.catalog:
            species_tags = {_norm(t) for t in (species.get("tags") or []) if t}
            inter = len(observed & species_tags)
            union = len(observed | species_tags) or 1
            score = inter / union
            matched = sorted(observed & species_tags)
            species_only = sorted(species_tags - observed)
            query_only = sorted(observed - species_tags)
            ranked.append(
                {
                    "species_id": species.get("id"),
                    "common_name": species.get("common_name"),
                    "scientific_name": species.get("scientific_name"),
                    "score": round(float(score), 4),
                    "tag_overlap": matched,
                    "matched_tags": matched,
                    "species_only_tags": species_only,
                    "query_only_tags": query_only,
                    "confidence": round(min(1.0, score * 1.15), 4),
                    "explanation": _build_explanation(
                        species.get("common_name", species.get("id", "?")),
                        matched, species_only, query_only, score
                    ),
                }
            )
        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[: max(1, top_k)]


def _norm(value: str) -> str:
    return str(value).strip().lower().replace("_", " ")


def tags_from_text(text: str) -> list[str]:
    parts = [p.strip() for p in text.replace(";", ",").split(",")]
    return [p for p in parts if p]


def _build_explanation(
    name: str,
    matched: list[str],
    species_only: list[str],
    query_only: list[str],
    score: float,
) -> str:
    """Build a human-readable explanation of why this species matched."""
    parts: list[str] = []
    if matched:
        parts.append(f"Matched {len(matched)} tag(s): {', '.join(matched[:8])}")
    else:
        parts.append("No direct tag matches")
    if species_only:
        example = species_only[:4]
        suffix = f" +{len(species_only) - 4} more" if len(species_only) > 4 else ""
        parts.append(f"Species-specific tags not in query: {', '.join(example)}{suffix}")
    if query_only:
        example = query_only[:4]
        suffix = f" +{len(query_only) - 4} more" if len(query_only) > 4 else ""
        parts.append(f"Query tags not in this species: {', '.join(example)}{suffix}")
    parts.append(f"Jaccard score: {score:.4f} ({len(matched)} shared / {len(matched) + len(species_only) + len(query_only)} total unique tags)")
    return "; ".join(parts)
