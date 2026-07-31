"""Weighted tag-based plant species ranker.

Extends the ToyPlantIdentifier Jaccard baseline with trainable tag weights
using an IDF-like (inverse document frequency) scheme: tags that appear in
fewer species are more discriminative and receive higher weight.

Optionally uses scikit-learn TfidfVectorizer when available; otherwise falls
back to a pure-Python IDF implementation with zero external dependencies.

Train / save / load workflow
----------------------------
    ranker = WeightedRanker()
    ranker.train()                     # compute tag weights from catalog
    ranker.save("weights.json")        # persist weights to disk
    ranker.load("weights.json")        # restore weights from disk
    results = ranker.identify(["tropical", "climbing"], top_k=3)

Integration with ToyPlantIdentifier
-----------------------------------
When `weights` is None (not trained / loaded), `identify()` delegates entirely
to `ToyPlantIdentifier.identify()` (pure Jaccard).  After training the
weighted score is combined with the Jaccard score for more stable ranking.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from plantguide.data.loader import load_species_catalog
from plantguide.models.toy import ToyPlantIdentifier, _norm, _build_explanation


# ---------------------------------------------------------------------------
# Optional TF-IDF via scikit-learn
# ---------------------------------------------------------------------------

def _sklearn_tfidf_available() -> bool:
    try:
        import sklearn.feature_extraction.text  # noqa: F401

        return True
    except ImportError:
        return False


def _compute_weights_sklearn(catalog: list[dict]) -> dict[str, float]:
    """Compute per-tag weights using sklearn TfidfVectorizer."""
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Build a "document" per species: space-joined normalized tags
    docs: list[str] = []
    tag_keys: list[str] = []
    for species in catalog:
        tags = [_norm(t) for t in (species.get("tags") or []) if t]
        docs.append(" ".join(tags))
        tag_keys.extend(tags)

    if not docs:
        return {}

    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w[\w\s]*\w\b", lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = vectorizer.get_feature_names_out()
    idf = vectorizer.idf_

    # Per-tag weight = mean of TF-IDF across all species (IDF component)
    weights: dict[str, float] = {}
    for idx, name in enumerate(feature_names):
        weights[name] = float(idf[idx])

    return weights


# ---------------------------------------------------------------------------
# Pure-Python IDF weighting
# ---------------------------------------------------------------------------

def _compute_weights_pure(catalog: list[dict]) -> dict[str, float]:
    """Compute per-tag IDF-like weights in pure Python.

    IDF(t) = log(1 + N / df(t))
    where N = number of species, df(t) = number of species containing tag t.
    """
    N = len(catalog)
    if N == 0:
        return {}

    # Count document frequency per normalized tag
    df: dict[str, int] = {}
    for species in catalog:
        seen: set[str] = set()
        for tag in (species.get("tags") or []):
            key = _norm(tag)
            if key and key not in seen:
                df[key] = df.get(key, 0) + 1
                seen.add(key)

    weights: dict[str, float] = {}
    for tag, count in df.items():
        # Smooth IDF: log(1 + N / df)  — tags in all species get ~log(2), rare tags get higher
        weights[tag] = math.log(1.0 + (N / count))

    return weights


# ---------------------------------------------------------------------------
# WeightedRanker
# ---------------------------------------------------------------------------


class WeightedRanker:
    """Tag-based plant species ranker with trainable weights."""

    def __init__(self, catalog: list[dict] | None = None) -> None:
        self.catalog: list[dict] = catalog if catalog is not None else load_species_catalog()
        self._toy: ToyPlantIdentifier = ToyPlantIdentifier(self.catalog)
        self.weights: dict[str, float] | None = None
        self._tfidf_available: bool = _sklearn_tfidf_available()

    # ------------------------------------------------------------------
    # Train
    # ------------------------------------------------------------------

    def train(self, use_sklearn: bool | None = None) -> dict[str, Any]:
        """Compute tag weights from the catalog.

        Parameters
        ----------
        use_sklearn:
            * None  – use sklearn TF-IDF if available, else pure-Python IDF.
            * True  – require sklearn.
            * False – force pure-Python IDF.

        Returns
        -------
        dict with keys ``method``, ``n_species``, ``n_tags``, and ``weights``.
        """
        if use_sklearn is None:
            use_sklearn = self._tfidf_available

        if use_sklearn and self._tfidf_available:
            self.weights = _compute_weights_sklearn(self.catalog)
            method = "sklearn-tfidf"
        else:
            self.weights = _compute_weights_pure(self.catalog)
            method = "pure-idf"

        return {
            "method": method,
            "n_species": len(self.catalog),
            "n_tags": len(self.weights),
            "weights": dict(sorted(self.weights.items(), key=lambda x: -x[1])[:20]),
        }

    # ------------------------------------------------------------------
    # Persist
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> Path:
        """Persist learned weights to a JSON file."""
        out = Path(path)
        payload: dict[str, Any] = {
            "model": "WeightedRanker",
            "method": "tfidf" if self._tfidf_available else "pure-idf",
            "n_species": len(self.catalog),
            "weights": self.weights or {},
        }
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return out

    def load(self, path: str | Path) -> WeightedRanker:
        """Restore weights from a previously saved JSON file.

        Returns self for chaining.
        """
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        saved_weights: dict[str, float] = payload.get("weights") or {}
        # Merge with local catalog: unknown tags get weight 0
        all_tags: set[str] = set()
        for species in self.catalog:
            for tag in species.get("tags") or []:
                key = _norm(tag)
                if key:
                    all_tags.add(key)
        self.weights = {tag: saved_weights.get(tag, 0.0) for tag in all_tags}
        return self

    # ------------------------------------------------------------------
    # Identify
    # ------------------------------------------------------------------

    def identify(self, tags: list[str], top_k: int = 3) -> list[dict]:
        """Rank species by weighted tag overlap.

        When weights are available the final score is a 60/40 blend of the
        weighted score and the original Jaccard score.  When weights are
        ``None`` (not trained) the method falls back to pure Jaccard via
        ``ToyPlantIdentifier``.
        """
        observed = {_norm(t) for t in tags if str(t).strip()}
        if not observed:
            return []

        use_weighted = self.weights is not None and len(self.weights) > 0

        ranked: list[dict] = []
        for species in self.catalog:
            species_tags = {_norm(t) for t in (species.get("tags") or []) if t}

            # Jaccard baseline
            inter = len(observed & species_tags)
            union = len(observed | species_tags) or 1
            jaccard = inter / union

            if use_weighted:
                weighted = self._score_weighted(observed, species_tags)
                # Blend: weighted dominant (0.7) + Jaccard (0.3) for stability
                score = 0.7 * weighted + 0.3 * jaccard
            else:
                score = jaccard

            matched = sorted(observed & species_tags)
            species_only = sorted(species_tags - observed)
            query_only = sorted(observed - species_tags)

            ranked.append(
                {
                    "species_id": species.get("id"),
                    "common_name": species.get("common_name"),
                    "scientific_name": species.get("scientific_name"),
                    "score": round(float(score), 4),
                    "jaccard_score": round(float(jaccard), 4),
                    "weighted_score": round(float(weighted) if use_weighted else jaccard, 4),
                    "tag_overlap": matched,
                    "matched_tags": matched,
                    "species_only_tags": species_only,
                    "query_only_tags": query_only,
                    "confidence": round(min(1.0, score * 1.15), 4),
                    "ranker": "weighted" if use_weighted else "jaccard-fallback",
                    "explanation": _build_weighted_explanation(
                        species.get("common_name", species.get("id", "?")),
                        matched,
                        species_only,
                        query_only,
                        score,
                        weighted if use_weighted else jaccard,
                        use_weighted,
                    ),
                }
            )

        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[: max(1, top_k)]

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _score_weighted(self, observed: set[str], species_tags: set[str]) -> float:
        """Compute a weighted overlap score.

        Score = sum(weight(t) for t in matched) / sum(weight(t) for t in observed ∪ species_tags)
        """
        matched = observed & species_tags
        all_tags = observed | species_tags
        if not all_tags:
            return 0.0

        w = self.weights or {}
        num = sum(w.get(t, 0.0) for t in matched)
        den = sum(w.get(t, 0.0) for t in all_tags)
        if den == 0.0:
            return 0.0
        return num / den

    def _score_jaccard(self, observed: set[str], species_tags: set[str]) -> float:
        inter = len(observed & species_tags)
        union = len(observed | species_tags) or 1
        return inter / union


# ---------------------------------------------------------------------------
# Explanation builder
# ---------------------------------------------------------------------------


def _build_weighted_explanation(
    name: str,
    matched: list[str],
    species_only: list[str],
    query_only: list[str],
    score: float,
    weighted_component: float,
    use_weighted: bool,
) -> str:
    """Human-readable explanation for weighted ranking results."""
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
    if use_weighted:
        parts.append(
            f"Weighted score: {weighted_component:.4f} | Final: {score:.4f} "
            f"({len(matched)} shared tags, weighted ranker)"
        )
    else:
        parts.append(
            f"Jaccard score: {score:.4f} "
            f"({len(matched)} shared / {len(matched) + len(species_only) + len(query_only)} total unique tags)"
        )
    return "; ".join(parts)
