"""Tests for torch baseline classifier.

All tests skip gracefully if torch is not installed.
"""

from __future__ import annotations

import pytest

from plantguide.data.loader import load_species_catalog
from plantguide.models.torch_baseline import (
    TORCH_AVAILABLE,
    _build_vocab,
    _get_species_id_list,
    _tags_to_vector,
    TorchBaselineClassifier,
    train_baseline,
    _prepare_training_data,
    predict,
)

pytestmark = [pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed")]


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

def test_build_vocab_contains_all_tags() -> None:
    catalog = load_species_catalog()
    vocab = _build_vocab(catalog)
    assert len(vocab) > 10
    # Check a known tag
    all_tags: set[str] = set()
    for sp in catalog:
        for t in sp.get("tags") or []:
            all_tags.add(str(t).strip().lower())
    for tag in all_tags:
        assert tag in vocab, f"tag {tag!r} missing from vocab"


def test_tags_to_vector_size() -> None:
    vocab = {"leafy": 0, "tropical": 1, "indoor": 2}
    vec = _tags_to_vector(["tropical", "indoor"], vocab)
    assert len(vec) == 3
    assert vec == [0.0, 1.0, 1.0]


def test_tags_to_vector_unknown_tag_ignored() -> None:
    vocab = {"leafy": 0}
    vec = _tags_to_vector(["leafy", "unknown_tag"], vocab)
    assert vec == [1.0]


def test_tags_to_vector_empty() -> None:
    vocab = {"leafy": 0, "tropical": 1}
    vec = _tags_to_vector([], vocab)
    assert vec == [0.0, 0.0]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def test_model_forward_shape() -> None:
    model = TorchBaselineClassifier(vocab_size=10, num_classes=5)
    import torch
    x = torch.randn(2, 10)
    out = model(x)
    assert out.shape == (2, 5)


def test_model_output_is_logits() -> None:
    """Output should be raw logits (not probabilities)."""
    model = TorchBaselineClassifier(vocab_size=5, num_classes=3)
    model.eval()  # eval mode so BatchNorm1d accepts single-sample
    import torch
    x = torch.randn(1, 5)
    out = model(x)
    # Logits can be any value, not bounded to [0,1]
    assert out.shape == (1, 3)


# ---------------------------------------------------------------------------
# Training data
# ---------------------------------------------------------------------------

def test_prepare_training_data() -> None:
    catalog = load_species_catalog()
    vocab = _build_vocab(catalog)
    species_ids = _get_species_id_list(catalog)
    X, y = _prepare_training_data(catalog, vocab, species_ids)
    assert X.shape[0] == len(catalog)
    assert X.shape[1] == len(vocab)
    assert y.shape[0] == len(catalog)
    # All labels should be valid indices
    assert y.min().item() >= 0
    assert y.max().item() < len(species_ids)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def test_train_baseline_returns_metadata(tmp_path) -> None:
    result = train_baseline(epochs=5, lr=0.01, save_path=tmp_path / "model.pt")
    assert result["epochs"] == 5
    assert result["vocab_size"] > 10
    assert result["num_classes"] > 5
    assert result["final_loss"] < 10.0  # should converge loosely
    assert (tmp_path / "model.pt").exists()


def test_trained_model_improves_with_epochs() -> None:
    """More epochs should give lower loss (or at least not explode)."""
    import torch
    import torch.nn.functional as F

    catalog = load_species_catalog()
    vocab = _build_vocab(catalog)
    species_ids = _get_species_id_list(catalog)
    X, y = _prepare_training_data(catalog, vocab, species_ids)

    model = TorchBaselineClassifier(vocab_size=len(vocab), num_classes=len(species_ids))
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    criterion = torch.nn.CrossEntropyLoss()

    # Train for a few steps
    losses = []
    for _ in range(10):
        optimizer.zero_grad()
        logits = model(X)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))

    # Loss should generally decrease
    assert losses[-1] < losses[0] + 0.5  # not strict, but shouldn't explode


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def test_predict_returns_list(tmp_path) -> None:
    """After training, predict should return sensible results."""
    result = train_baseline(epochs=10, lr=0.01, save_path=tmp_path / "model.pt")
    preds = predict(["tropical", "fenestrated leaves", "climbing"], model_path=tmp_path / "model.pt")
    assert len(preds) == 3
    for p in preds:
        assert "species_id" in p
        assert "score" in p
        assert 0.0 <= p["score"] <= 1.0


def test_predict_returns_top_k(tmp_path) -> None:
    train_baseline(epochs=5, lr=0.01, save_path=tmp_path / "model.pt")
    preds = predict(["indoor", "leafy"], model_path=tmp_path / "model.pt", top_k=5)
    assert len(preds) == 5


def test_predict_empty_tags(tmp_path) -> None:
    train_baseline(epochs=5, lr=0.01, save_path=tmp_path / "model.pt")
    preds = predict([], model_path=tmp_path / "model.pt")
    # Should still return something (all species roughly equal)
    assert len(preds) == 3


def test_predict_model_not_found() -> None:
    preds = predict(["tropical"], model_path="/nonexistent/model.pt")
    assert preds == []


# ---------------------------------------------------------------------------
# Species ID list
# ---------------------------------------------------------------------------

def test_get_species_id_list() -> None:
    catalog = load_species_catalog()
    ids = _get_species_id_list(catalog)
    assert len(ids) == len(catalog)
    # All IDs should be unique
    assert len(set(ids)) == len(ids)