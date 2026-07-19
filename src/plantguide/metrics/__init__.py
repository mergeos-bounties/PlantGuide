"""
Metrics: top-k accuracy and confusion between similar species.

Provides evaluation of the identification pipeline against the sample
dataset, reporting top-1 / top-3 / top-5 accuracy, per-species hit rates,
and a confusion matrix for similar species.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from plantguide.data.loader import list_sample_files, load_sample
from plantguide.identify.pipeline import identify_from_tags


def _load_all_samples(
    sample_dir: str | Path = "data/samples",
) -> list[dict]:
    """Load all sample observation files with expected species."""
    results = []
    for f in sorted(list_sample_files(Path(sample_dir))):
        try:
            sample = load_sample(f)
        except (FileNotFoundError, ValueError, KeyError):
            continue
        if sample.get("expected_species"):
            results.append(sample)
    return results


def run_topk_accuracy(
    sample_dir: str | Path = "data/samples",
    top_ks: tuple[int, ...] = (1, 3, 5),
) -> dict[str, Any]:
    """
    Evaluate top-k accuracy across all samples.

    Returns:
    - top_1_acc, top_3_acc, top_5_acc
    - per_species_accuracy
    - total_samples, total_correct (by k)
    - confusion_summary
    """
    samples = _load_all_samples(sample_dir)

    correct = {k: 0 for k in top_ks}
    total = len(samples)
    per_species: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    confusion: list[dict[str, Any]] = []

    for sample in samples:
        expected = sample["expected_species"]
        tags = sample.get("tags", [])
        if not tags:
            continue

        result = identify_from_tags(tags, top_k=max(top_ks), with_care=False)
        matches = result.get("matches", [])
        top_ids = [str(m.get("species_id", "")).lower() for m in matches]

        per_species[expected]["total"] += 1

        for k in top_ks:
            if top_ids and top_ids[0] == expected.lower():
                correct[k] += 1
                if k == 1:
                    per_species[expected]["correct"] += 1
            elif k > 1 and len(top_ids) >= k and expected.lower() in top_ids[:k]:
                correct[k] += 1

        # Confusion: if top-1 is wrong, log it
        if top_ids and top_ids[0] != expected.lower():
            confusion.append({
                "sample_id": sample.get("id"),
                "expected": expected,
                "predicted": top_ids[0] if top_ids else None,
                "predicted_name": matches[0].get("common_name", "") if matches else "",
                "score": matches[0].get("score", 0) if matches else 0,
            })

    accuracy = {f"top_{k}_acc": round(correct[k] / total, 4) if total else 0 for k in top_ks}
    accuracy["total_samples"] = total
    accuracy["total_correct"] = {f"top_{k}": correct[k] for k in top_ks}
    accuracy["per_species"] = dict(per_species)
    accuracy["confusion_count"] = len(confusion)
    accuracy["confusion_examples"] = sorted(
        confusion, key=lambda x: x["score"], reverse=True
    )[:20]

    return accuracy


def run_confusion_matrix(
    sample_dir: str | Path = "data/samples",
) -> dict[str, Any]:
    """Build a confusion matrix of expected vs predicted species."""
    samples = _load_all_samples(sample_dir)

    matrix: dict[str, Counter] = defaultdict(Counter)
    row_labels: set[str] = set()

    for sample in samples:
        expected = sample["expected_species"]
        tags = sample.get("tags", [])
        if not tags:
            continue

        result = identify_from_tags(tags, top_k=3, with_care=False)
        matches = result.get("matches", [])
        predicted = str(matches[0].get("species_id", "")).lower() if matches else "unknown"

        row_labels.add(expected)
        matrix[expected][predicted] += 1

    rows = []
    for expected in sorted(row_labels):
        row = {"expected": expected}
        total = sum(matrix[expected].values())
        row["total"] = total
        row["self_hit"] = matrix[expected].get(expected, 0)
        row["top_confusions"] = [
            {"predicted": p, "count": c}
            for p, c in matrix[expected].most_common(5)
            if p != expected
        ]
        row["self_rate"] = round(row["self_hit"] / total, 3) if total else 0
        rows.append(row)

    return {
        "matrix_rows": rows,
        "total_species": len(rows),
        "overall_top1": round(
            sum(r["self_hit"] for r in rows)
            / max(sum(r["total"] for r in rows), 1),
            4,
        ),
    }


def print_accuracy_report(accuracy: dict[str, Any]) -> str:
    """Format accuracy report as a readable string."""
    lines = ["=" * 60, "  Top-K Accuracy Report", "=" * 60, ""]
    lines.append(f"  Total samples: {accuracy['total_samples']}")
    for k in [1, 3, 5]:
        top_k = f"top_{k}"
        if top_k in accuracy:
            lines.append(
                f"  Top-{k} accuracy: {accuracy[top_k + '_acc']:.2%}"
                f" ({accuracy['total_correct'][top_k]}/{accuracy['total_samples']})"
            )
    lines.append("")
    lines.append(f"  Confusion cases: {accuracy['confusion_count']}")
    lines.append("")

    if accuracy.get("confusion_examples"):
        lines.append("  Top confusion examples:")
        for ex in accuracy["confusion_examples"][:10]:
            lines.append(
                f"    {ex['sample_id']}: expected={ex['expected']}, "
                f"predicted={ex['predicted']} ({ex['predicted_name']}) @ score {ex['score']:.3f}"
            )

    return "\n".join(lines)


def print_confusion_report(confusion: dict[str, Any]) -> str:
    """Format confusion matrix as readable string."""
    lines = ["=" * 60, "  Confusion Matrix", "=" * 60, ""]
    lines.append(f"  Overall top-1 rate: {confusion['overall_top1']:.2%}")
    lines.append(f"  Species evaluated: {confusion['total_species']}")
    lines.append("")
    lines.append("  Per-species self-hit rates:")
    for row in confusion["matrix_rows"]:
        lines.append(
            f"    {row['expected']:35s} "
            f"self={row['self_hit']}/{row['total']} "
            f"({row['self_rate']:.0%})"
        )
        if row["top_confusions"]:
            confs = ", ".join(
                f"{c['predicted']}({c['count']})"
                for c in row["top_confusions"][:3]
            )
            lines.append(f"    {'':35s} confusions: {confs}")
    return "\n".join(lines)
