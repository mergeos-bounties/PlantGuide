"""Tests for metrics and accuracy (#21)."""

from __future__ import annotations

from plantguide.metrics import run_topk_accuracy, run_confusion_matrix
from plantguide.metrics import print_accuracy_report, print_confusion_report


def test_topk_accuracy_runs() -> None:
    """Run across all samples, verify keys present."""
    result = run_topk_accuracy()
    assert result["total_samples"] > 0
    assert "top_1_acc" in result
    assert "top_3_acc" in result
    assert "confusion_count" in result
    assert result["top_1_acc"] >= 0
    assert result["top_1_acc"] <= 1.0


def test_accuracy_includes_per_species() -> None:
    result = run_topk_accuracy()
    assert "per_species" in result
    assert len(result["per_species"]) > 0
    # Check a known species
    for sp, data in result["per_species"].items():
        assert data["total"] >= 1
        assert "correct" in data


def test_confusion_matrix_runs() -> None:
    result = run_confusion_matrix()
    assert result["total_species"] > 0
    assert "matrix_rows" in result
    assert result["overall_top1"] >= 0


def test_confusion_matrix_has_rows() -> None:
    result = run_confusion_matrix()
    for row in result["matrix_rows"]:
        assert "expected" in row
        assert "self_hit" in row
        assert "total" in row
        assert "self_rate" in row


def test_print_accuracy_report() -> None:
    result = run_topk_accuracy()
    report = print_accuracy_report(result)
    assert "Top-K Accuracy Report" in report
    assert "Total samples" in report
    assert f"{result['total_samples']}" in report


def test_print_confusion_report() -> None:
    result = run_confusion_matrix()
    report = print_confusion_report(result)
    assert "Confusion Matrix" in report
    assert "Overall top-1 rate" in report


def test_accuracy_improves_with_k() -> None:
    """Top-5 should be >= Top-1."""
    result = run_topk_accuracy()
    assert result["top_5_acc"] >= result["top_1_acc"]


def test_confusion_examples_limited() -> None:
    result = run_topk_accuracy()
    assert len(result.get("confusion_examples", [])) <= 20
