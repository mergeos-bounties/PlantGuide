"""Tests for PlantGuide eval module (bounty #21)."""

from __future__ import annotations

from pathlib import Path
import json

from plantguide.data.loader import list_sample_files, list_species_files
from plantguide.eval import hit_at_k, confusion_matrix, eval_report

HERE = Path(__file__).parent


def test_hit_at_k_default() -> None:
    """hit@k should run on all samples and return valid structure."""
    result = hit_at_k(k=3)
    assert result["k"] == 3
    assert result["total"] > 0
    assert 0 <= result["hit_rate"] <= 1.0
    assert len(result["details"]) == result["total"]


def test_hit_at_k_increasing() -> None:
    """hit@1 <= hit@3 <= hit@5."""
    h1 = hit_at_k(k=1)["hit_rate"]
    h3 = hit_at_k(k=3)["hit_rate"]
    h5 = hit_at_k(k=5)["hit_rate"]
    assert h1 <= h3 <= h5


def test_confusion_matrix_structure() -> None:
    """Confusion matrix returns expected keys."""
    cm = confusion_matrix()
    assert "total_samples" in cm
    assert "correct" in cm
    assert "accuracy" in cm
    assert "entries" in cm
    assert "species_labels" in cm
    assert "matrix" in cm
    assert cm["total_samples"] > 0
    assert len(cm["species_labels"]) > 0


def test_confusion_matrix_symmetry() -> None:
    """Confusion matrix rows and cols should match species_labels length."""
    cm = confusion_matrix(top_n=10)
    labels = cm["species_labels"]
    mat = cm["matrix"]
    assert len(mat) == len(labels)
    assert all(len(row) == len(labels) for row in mat)


def test_eval_report_string() -> None:
    """eval_report should produce a non-empty string."""
    report = eval_report(k_values=[1, 3])
    assert isinstance(report, str)
    assert len(report) > 100
    assert "Hit@k" in report
    assert "Confusion" in report


def test_eval_report_correctness() -> None:
    """eval_report accuracy should match manual calculation."""
    report = eval_report(k_values=[1])
    h1 = hit_at_k(k=1)
    expected_rate = f"{h1['hit_rate']:.2%}"
    assert expected_rate in report
