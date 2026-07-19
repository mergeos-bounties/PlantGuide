"""Eval module for PlantGuide identifier: top-k accuracy and confusion metrics.

Part of bounty #21 — Metrics: top-k accuracy, confusion between similar species.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plantguide.data.loader import list_sample_files, load_sample, get_species_by_id
from plantguide.identify.pipeline import identify_from_tags


def hit_at_k(
    sample_paths: list[Path] | None = None,
    k: int = 3,
    label_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Compute hit@k across labeled samples.

    Args:
        sample_paths: Sample files to evaluate. Defaults to all.
        k: Top-k to check for a hit.
        label_overrides: Manual expected_species overrides by sample id.

    Returns:
        Dict with hits, total, hit_rate, and per-sample results.
    """
    if sample_paths is None:
        sample_paths = list_sample_files()

    hits = 0
    total = 0
    details: list[dict[str, Any]] = []
    expected_list: list[str] = []
    predicted_list: list[str] = []

    for path in sample_paths:
        sample = load_sample(path)
        sample_id = sample.get("id", path.stem)
        expected = label_overrides.get(sample_id) if label_overrides else None
        if expected is None:
            expected = sample.get("expected_species")
        if not expected:
            continue

        result = identify_from_tags(sample.get("tags", []), top_k=k)
        matches = result.get("matches", [])

        total += 1
        expected_list.append(str(expected).lower())

        top_k_ids = [str(m.get("species_id", "")).lower() for m in matches]
        is_hit = str(expected).lower() in top_k_ids
        predicted_list.append(top_k_ids[0] if top_k_ids else "")

        if is_hit:
            hits += 1

        details.append({
            "sample_id": sample_id,
            "expected": expected,
            "top_k_ids": top_k_ids,
            "hit": is_hit,
            "scores": [m.get("score", 0) for m in matches],
        })

    return {
        "k": k,
        "hits": hits,
        "total": total,
        "hit_rate": round(hits / total, 4) if total else 0.0,
        "details": details,
    }


def confusion_matrix(
    sample_paths: list[Path] | None = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Build a confusion matrix of expected vs predicted species.

    Args:
        sample_paths: Sample files to evaluate.
        top_n: Limit confusion display to the N most common species.

    Returns:
        Dict with confusion entries, a list-of-lists matrix, and species labels.
    """
    if sample_paths is None:
        sample_paths = list_sample_files()

    expected_list: list[str] = []
    predicted_list: list[str] = []

    for path in sample_paths:
        sample = load_sample(path)
        expected = sample.get("expected_species")
        if not expected:
            continue

        result = identify_from_tags(sample.get("tags", []), top_k=1)
        matches = result.get("matches", [])
        predicted = str(matches[0]["species_id"]).lower() if matches else ""
        expected_list.append(str(expected).lower())
        predicted_list.append(predicted)

    # Count co-occurrences
    confusion: dict[tuple[str, str], int] = {}
    for exp, pred in zip(expected_list, predicted_list):
        key = (exp, pred)
        confusion[key] = confusion.get(key, 0) + 1

    # Identify top species by total occurrence
    species_counts: dict[str, int] = {}
    for exp, pred in zip(expected_list, predicted_list):
        species_counts[exp] = species_counts.get(exp, 0) + 1
        if pred:
            species_counts[pred] = species_counts.get(pred, 0) + 1

    sorted_species = sorted(species_counts, key=species_counts.get, reverse=True)
    top_species = sorted_species[:top_n]

    # Build matrix (list of lists)
    matrix: list[list[int]] = [[0] * len(top_species) for _ in range(len(top_species))]
    for (exp, pred), count in confusion.items():
        if exp in top_species and pred in top_species:
            i = top_species.index(exp)
            j = top_species.index(pred)
            matrix[i][j] = count

    # Build entry list
    entries = [
        {"expected": exp, "predicted": pred, "count": count}
        for (exp, pred), count in sorted(confusion.items(), key=lambda x: -x[1])
    ]

    return {
        "total_samples": len(expected_list),
        "correct": sum(1 for e, p in zip(expected_list, predicted_list) if e == p),
        "accuracy": round(sum(1 for e, p in zip(expected_list, predicted_list) if e == p) / max(len(expected_list), 1), 4),
        "entries": entries,
        "species_labels": top_species,
        "matrix": matrix,
    }


def eval_report(
    sample_paths: list[Path] | None = None,
    k_values: list[int] | None = None,
    output_path: str | Path | None = None,
) -> str:
    """Generate a human-readable evaluation report.

    Args:
        sample_paths: Sample files to evaluate.
        k_values: List of k values for hit@k.
        output_path: If provided, write report to this file.

    Returns:
        Report string.
    """
    if sample_paths is None:
        sample_paths = list_sample_files()
    if k_values is None:
        k_values = [1, 3, 5]

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("PlantGuide Identification Evaluation Report")
    lines.append("=" * 60)
    lines.append(f"Total samples: {len(sample_paths)}")
    lines.append("")

    # Hit@k metrics
    lines.append("--- Hit@k ---")
    for k in k_values:
        result = hit_at_k(sample_paths, k=k)
        lines.append(f"  hit@{k}: {result['hits']}/{result['total']} = {result['hit_rate']:.2%}")
    lines.append("")

    # Confusion
    cm = confusion_matrix(sample_paths)
    lines.append(f"--- Confusion (overall accuracy: {cm['accuracy']:.2%}) ---")
    lines.append(f"  Correct: {cm['correct']}/{cm['total_samples']}")
    lines.append("")

    top_confusions = [e for e in cm["entries"] if e["expected"] != e["predicted"]]
    if top_confusions:
        lines.append("  Top confusions:")
        for entry in top_confusions[:10]:
            lines.append(f"    expected={entry['expected']:40s} predicted={entry['predicted']:40s} count={entry['count']}")

    report = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")

    return report
