"""Train tag weights for WeightedTagIdentifier from labeled samples.

Uses a TF-IDF-inspired approach:
- Term frequency (TF): how often a tag appears in samples of a given species.
- Inverse document frequency (IDF): how rare/unique a tag is across all species.

Tags that are both frequent in the target species and rare across all species
get higher weight, making them more discriminative.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from plantguide.config import RUNS_DIR, WEIGHTS_DIR
from plantguide.data.loader import list_sample_files, load_sample, load_species_catalog
from plantguide.models.toy import _norm


def train_weighted() -> dict[str, Any]:
    """Train tag weights from labeled samples and save to WEIGHTS_DIR.

    Returns a report dict with weights path, history, and coverage stats.
    """
    samples = list_sample_files()
    if not samples:
        msg = "No labeled samples found under data/samples/"
        raise FileNotFoundError(msg)

    catalog = load_species_catalog()
    species_ids = {_norm(s.get("id", "")) for s in catalog}

    # ------------------------------------------------------------------
    # 1. Build tag -> species frequency matrix from samples
    # ------------------------------------------------------------------
    tag_counts: dict[str, Counter[str]] = defaultdict(Counter)
    species_tag_presence: Counter[str] = Counter()

    # Count from catalog entries
    for species in catalog:
        for t in species.get("tags") or []:
            nt = _norm(t)
            species_tag_presence[nt] += 1

    # Count from labeled samples
    labeled_count = 0
    for path in samples:
        sample = load_sample(path)
        expected = sample.get("expected_species")
        if not expected:
            continue
        sid = _norm(expected)
        if sid not in species_ids:
            continue
        labeled_count += 1
        for t in sample.get("tags") or []:
            nt = _norm(t)
            tag_counts[sid][nt] += 1
            species_tag_presence[nt] += 1

    if labeled_count == 0:
        msg = "No labeled samples with valid expected_species found"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # 2. Compute TF-IDF weights per species
    # ------------------------------------------------------------------
    n_species = max(len(species_ids), 1)

    weights: dict[str, dict[str, float]] = {}
    for species in catalog:
        sid = _norm(species.get("id", ""))
        sp_weights: dict[str, float] = {}
        all_tags = {_norm(t) for t in (species.get("tags") or [])}

        for tag in all_tags:
            tf = tag_counts.get(sid, Counter()).get(tag, 0) + 1  # +1 smoothing
            n_with_tag = species_tag_presence.get(tag, 0) + 1  # +1 smoothing
            idf = math.log((n_species + 1) / n_with_tag)
            sp_weights[tag] = round(tf * idf, 4)

        # Also include tags from samples not in catalog entry
        for tag, tf_val in (tag_counts.get(sid) or Counter()).items():
            if tag not in sp_weights:
                n_with_tag = species_tag_presence.get(tag, 0) + 1
                idf = math.log((n_species + 1) / n_with_tag)
                sp_weights[tag] = round((tf_val + 1) * idf, 4)

        if sp_weights:
            weights[sid] = sp_weights

    # ------------------------------------------------------------------
    # 3. Save weights
    # ------------------------------------------------------------------
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    weights_path = WEIGHTS_DIR / "weighted_tag_weights.json"
    payload = {
        "weights": weights,
        "metadata": {
            "model": "WeightedTagIdentifier",
            "n_species": len(species_ids),
            "n_labeled_samples": labeled_count,
            "n_species_with_weights": len(weights),
        },
    }
    weights_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------
    # 4. Eval: compute top-1 hit rate on the training set
    # ------------------------------------------------------------------
    from plantguide.models.weighted import WeightedTagIdentifier

    ident = WeightedTagIdentifier(catalog=catalog)
    ident.load_weights(weights_path)

    hits = 0
    total = 0
    for path in samples:
        sample = load_sample(path)
        expected = sample.get("expected_species")
        if not expected:
            continue
        sid = _norm(expected)
        if sid not in species_ids:
            continue
        total += 1
        result = ident.identify(sample.get("tags") or [], top_k=3)
        if result:
            top_id = _norm(str(result[0].get("species_id", "")))
            if top_id == sid:
                hits += 1

    top1_rate = round(hits / total, 4) if total else 0.0

    # Also compute baseline Jaccard hit rate
    from plantguide.models.toy import ToyPlantIdentifier

    toy = ToyPlantIdentifier(catalog=catalog)
    baseline_hits = 0
    for path in samples:
        sample = load_sample(path)
        expected = sample.get("expected_species")
        if not expected:
            continue
        sid = _norm(expected)
        if sid not in species_ids:
            continue
        result = toy.identify(sample.get("tags") or [], top_k=3)
        if result:
            top_id = _norm(str(result[0].get("species_id", "")))
            if top_id == sid:
                baseline_hits += 1
    baseline_rate = round(baseline_hits / total, 4) if total else 0.0

    # ------------------------------------------------------------------
    # 5. Report
    # ------------------------------------------------------------------
    report = {
        "weights_path": str(weights_path),
        "n_labeled_samples": labeled_count,
        "n_species_with_weights": len(weights),
        "top1_hit_rate_weighted": top1_rate,
        "top1_hit_rate_jaccard": baseline_rate,
        "improvement": round(top1_rate - baseline_rate, 4),
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RUNS_DIR / "weighted_train_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return report
