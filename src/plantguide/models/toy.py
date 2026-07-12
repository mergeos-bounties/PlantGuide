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
            ranked.append(
                {
                    "species_id": species.get("id"),
                    "common_name": species.get("common_name"),
                    "scientific_name": species.get("scientific_name"),
                    "score": round(float(score), 4),
                    "tag_overlap": sorted(observed & species_tags),
                    "confidence": round(min(1.0, score * 1.15), 4),
                }
            )
        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[: max(1, top_k)]


def _norm(value: str) -> str:
    return str(value).strip().lower().replace("_", " ")


def tags_from_text(text: str) -> list[str]:
    parts = [p.strip() for p in text.replace(";", ",").split(",")]
    return [p for p in parts if p]
