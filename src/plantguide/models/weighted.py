"""WeightedTagIdentifier: trainable tag weights beyond Jaccard similarity.

Extends ToyPlantIdentifier with per-species tag weights learned from
labeled samples. When no weights are loaded, falls back to the original
Jaccard-based scoring (toy fallback).
"""

from __future__ import annotations

import json
from pathlib import Path

from plantguide.data.loader import load_species_catalog
from plantguide.models.toy import (
    ToyPlantIdentifier,
    _build_explanation,
    _norm,
)


class WeightedTagIdentifier(ToyPlantIdentifier):
    """Offline plant identifier with trainable tag weights.

    Weights are learned from labeled samples via TF-IDF-like scoring:
    tags that appear frequently in a specific species but rarely elsewhere
    get higher weight, making them more discriminative.

    When no weights are loaded (or weights dict is empty), falls back
    to the parent Jaccard-based scoring.
    """

    def __init__(
        self,
        catalog: list[dict] | None = None,
        weights_path: str | Path | None = None,
    ):
        super().__init__(catalog)
        self.weights: dict[str, dict[str, float]] = {}
        """Mapping species_id -> {tag: weight}."""
        self._fallback = True
        self._weights_source: str | None = None

        if weights_path is not None:
            self.load_weights(weights_path)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_weights(self, path: str | Path) -> bool:
        """Load pre-trained weights from a JSON file.

        Returns True if weights were loaded, False if the file doesn't
        exist or is empty (falls back to Jaccard).
        """
        p = Path(path)
        if not p.exists():
            self._fallback = True
            self.weights = {}
            self._weights_source = None
            return False

        blob = json.loads(p.read_text(encoding="utf-8"))
        raw: dict[str, dict[str, float]] = blob.get("weights", {})
        # Normalise species IDs and tag keys (underscores → spaces)
        self.weights = {
            _norm(k): {_norm(tk): tv for tk, tv in tv_map.items()}
            for k, tv_map in raw.items()
        }
        self._fallback = not bool(self.weights)
        self._weights_source = str(p)
        return not self._fallback

    def save_weights(self, path: str | Path) -> str:
        """Persist current weights to a JSON file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "weights": self.weights,
            "source": self._weights_source or "trained",
        }
        p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return str(p)

    # ------------------------------------------------------------------
    # Weighted scoring
    # ------------------------------------------------------------------

    def identify(self, tags: list[str], top_k: int = 3) -> list[dict]:
        if self._fallback:
            return super().identify(tags, top_k=top_k)

        observed = {_norm(t) for t in tags if str(t).strip()}
        if not observed:
            return []

        ranked: list[dict] = []
        for species in self.catalog:
            sid = _norm(species.get("id", ""))
            species_tags = {_norm(t) for t in (species.get("tags") or []) if t}
            # Weights are indexed by normalised species ID
            species_weights = self.weights.get(sid, {})

            matched = sorted(observed & species_tags)
            species_only = sorted(species_tags - observed)
            query_only = sorted(observed - species_tags)

            if species_weights and matched:
                # Weighted scoring: sum of weights of matching tags
                # divided by total weight of all tags in this species
                weight_sum = sum(species_weights.get(t, 1.0) for t in matched)
                total_weight = sum(
                    species_weights.get(t, 1.0) for t in species_tags
                ) or 1.0
                score = weight_sum / total_weight
            else:
                # Fall back to plain Jaccard for this species
                inter = len(matched)
                union = len(observed | species_tags) or 1
                score = inter / union

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
                        matched,
                        species_only,
                        query_only,
                        score,
                    ),
                }
            )
        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[: max(1, top_k)]


# ------------------------------------------------------------------
# Convenience factory
# ------------------------------------------------------------------

def create_identifier(
    weights_path: str | Path | None = None,
    catalog: list[dict] | None = None,
) -> WeightedTagIdentifier:
    """Build a WeightedTagIdentifier, optionally loading pre-trained weights."""
    ident = WeightedTagIdentifier(catalog=catalog)
    if weights_path is not None:
        ident.load_weights(weights_path)
    return ident