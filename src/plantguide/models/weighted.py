"""Weighted-tag plant identifier — trainable ranking beyond Jaccard.

Adds a ``WeightedPlantIdentifier`` that learns per-tag importance from
labeled samples and produces a weighted overlap score. Falls back to
Jaccard when no weights are configured (toy-compatible).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from plantguide.config import RUNS_DIR
from plantguide.data.loader import load_species_catalog, list_sample_files, load_sample


class WeightedPlantIdentifier:
    """Plant identifier with learnable tag weights.

    Extends the Jaccard-based ``ToyPlantIdentifier`` with per-tag
    importance learned from labeled sample data. Higher-weight tags
    contribute more to the final score.

    Usage::

        model = WeightedPlantIdentifier()
        model.train(epochs=5)
        model.save_weights("runs/tag_weights.json")
        results = model.identify(["green leaves", "red flowers"])
    """

    def __init__(self, catalog: list[dict] | None = None):
        self.catalog = catalog if catalog is not None else load_species_catalog()
        self._tag_weights: dict[str, float] = {}
        self._trained = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, epochs: int = 5) -> dict:
        """Learn per-tag weights from labeled samples.

        Uses TF-IDF-inspired weighting: tags that appear frequently
        across many species get lower weights (common/ambiguous);
        tags specific to one species get higher weights (diagnostic).

        Args:
            epochs: Number of passes over training data (weight smoothing).

        Returns:
            Training report dict with ``history``, ``tag_count``,
            ``final_top_weights``.
        """
        samples = list_sample_files()
        labeled: list[dict] = []
        for path in samples:
            sample = load_sample(path)
            if sample.get("expected_species"):
                labeled.append(sample)

        if not labeled:
            return {"error": "no labeled samples found", "history": []}

        # Build tag→species frequency map
        tag_species_count: Counter = Counter()
        species_tag_sets: list[set[str]] = []
        for sample in labeled:
            tags = {_norm(t) for t in (sample.get("tags") or []) if t}
            species_tag_sets.append(tags)
            for tag in tags:
                tag_species_count[tag] += 1

        total_labeled = len(labeled)

        # TF-IDF style: high weight = tag appears in few species
        history = []
        for epoch in range(1, max(1, epochs) + 1):
            weights: dict[str, float] = {}
            for tag, count in tag_species_count.items():
                # IDF-like: log(total / doc_freq)
                idf = max(0.1, __import__("math").log((total_labeled + 1) / (count + 1)))
                weights[tag] = round(idf, 4)

            # Evaluate top-1 hit rate
            hits = 0
            for sample in labeled:
                expected = str(sample.get("expected_species", "")).lower()
                result = self.identify(
                    sample.get("tags") or [],
                    top_k=3,
                    weights=weights,
                )
                if result and str(result[0].get("species_id", "")).lower() == expected:
                    hits += 1

            acc = round(hits / total_labeled, 4) if total_labeled else 0.0
            history.append(
                {
                    "epoch": epoch,
                    "top1_hit_rate": acc,
                    "n_labeled": total_labeled,
                    "n_tags_weighted": len(weights),
                }
            )

            # Smooth: average weights across epochs
            if epoch == 1:
                self._tag_weights = dict(weights)
            else:
                alpha = 1.0 / epoch
                for tag, w in weights.items():
                    prev = self._tag_weights.get(tag, w)
                    self._tag_weights[tag] = round(alpha * w + (1 - alpha) * prev, 4)

        self._trained = True

        # Save report
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = RUNS_DIR / "weighted_train_report.json"
        top_weights = dict(
            sorted(self._tag_weights.items(), key=lambda x: x[1], reverse=True)[:20]
        )
        report = {
            "model": "WeightedPlantIdentifier",
            "epochs": epochs,
            "history": history,
            "tag_count": len(self._tag_weights),
            "top_weights": top_weights,
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return {"report_path": str(report_path), **report}

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def save_weights(self, path: str | Path) -> dict:
        """Save tag weights to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": "WeightedPlantIdentifier",
            "tag_weights": self._tag_weights,
            "trained": self._trained,
            "tag_count": len(self._tag_weights),
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return {"path": str(path), "tag_count": len(self._tag_weights), "ok": True}

    def load_weights(self, path: str | Path) -> dict:
        """Load tag weights from a JSON file."""
        path = Path(path)
        if not path.exists():
            return {"ok": False, "error": f"weights file not found: {path}"}
        data = json.loads(path.read_text(encoding="utf-8"))
        self._tag_weights = data.get("tag_weights", {})
        self._trained = data.get("trained", bool(self._tag_weights))
        return {
            "ok": True,
            "path": str(path),
            "tag_count": len(self._tag_weights),
            "trained": self._trained,
        }

    @property
    def tag_weights(self) -> dict[str, float]:
        """Read-only access to current tag weights."""
        return dict(self._tag_weights)

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    def identify(
        self,
        tags: list[str],
        top_k: int = 3,
        weights: dict[str, float] | None = None,
    ) -> list[dict]:
        """Rank species by weighted tag overlap.

        Score = sum(weight(tag) for tag in matched) / sum(weight(tag) for tag in union)
        Falls back to Jaccard when no weights are available.

        Args:
            tags: Observed trait tags from the query.
            top_k: Max results to return.
            weights: Optional override weights (uses trained weights if None).

        Returns:
            Ranked list of species dicts with ``score``, ``confidence``,
            ``tag_overlap``, and ``explanation``.
        """
        active_weights = weights if weights is not None else self._tag_weights
        observed = {_norm(t) for t in tags if str(t).strip()}
        if not observed:
            return []

        ranked: list[dict] = []
        for species in self.catalog:
            species_tags = {_norm(t) for t in (species.get("tags") or []) if t}
            inter = observed & species_tags
            union = observed | species_tags

            if active_weights:
                # Weighted score: sum of matched weights / sum of union weights
                matched_weight = sum(
                    active_weights.get(t, 0.5) for t in inter
                )
                union_weight = sum(
                    active_weights.get(t, 0.5) for t in union
                )
                score = matched_weight / max(union_weight, 0.001)
            else:
                # Jaccard fallback
                score = len(inter) / max(len(union), 1)

            matched = sorted(inter)
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
                        matched, species_only, query_only, score, active_weights,
                    ),
                }
            )

        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[: max(1, top_k)]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _norm(value: str) -> str:
    return str(value).strip().lower().replace("_", " ")


def _build_explanation(
    name: str,
    matched: list[str],
    species_only: list[str],
    query_only: list[str],
    score: float,
    weights: dict[str, float] | None = None,
) -> str:
    parts: list[str] = []
    if matched:
        parts.append(f"Matched {len(matched)} tag(s): {', '.join(matched[:8])}")
        if weights:
            top_match = max(matched, key=lambda t: weights.get(t, 0.5))
            parts.append(f"Top weighted tag: '{top_match}' (w={weights.get(top_match, 0.5):.3f})")
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
    model_name = "Weighted" if weights else "Jaccard"
    parts.append(f"{model_name} score: {score:.4f}")
    return "; ".join(parts)
