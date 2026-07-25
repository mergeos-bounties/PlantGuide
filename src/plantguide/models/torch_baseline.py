"""PyTorch classification baseline for species ID from trait tags.

Architecture: 2-layer MLP with batch norm + dropout.
- Input: multi-hot tag vector (vocabulary size N)
- Hidden: 128 → ReLU → BN → Dropout(0.3)
- Output: softmax over species classes

CPU-only; no GPU dependency. Tests skip gracefully if torch is absent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from plantguide.config import RUNS_DIR
from plantguide.data.loader import load_species_catalog

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]
    nn = None
    F = None


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

def _build_vocab(catalog: list[dict] | None = None) -> dict[str, int]:
    """Collect all unique tags across the species catalog -> {tag: idx}."""
    if catalog is None:
        catalog = load_species_catalog()
    seen: set[str] = set()
    for sp in catalog:
        for t in sp.get("tags") or []:
            seen.add(str(t).strip().lower())
    # sort for determinism
    return {tag: i for i, tag in enumerate(sorted(seen))}


def _tags_to_vector(tags: list[str], vocab: dict[str, int]) -> list[float]:
    """Convert a list of tags to a multi-hot float vector."""
    vector = [0.0] * len(vocab)
    for t in tags:
        key = str(t).strip().lower()
        idx = vocab.get(key)
        if idx is not None:
            vector[idx] = 1.0
    return vector


def _get_species_id_list(catalog: list[dict]) -> list[str]:
    return [str(sp.get("id", f"unknown_{i}")) for i, sp in enumerate(catalog)]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class TorchBaselineClassifier(nn.Module):
    """2-layer MLP for species classification from tag vectors."""

    def __init__(self, vocab_size: int, num_classes: int, hidden_size: int = 128):
        super().__init__()
        self.fc1 = nn.Linear(vocab_size, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------

def _prepare_training_data(
    catalog: list[dict],
    vocab: dict[str, int],
    species_ids: list[str],
) -> tuple[torch.Tensor, torch.Tensor]:
    """Build feature matrix X (N, vocab_size) and label tensor y (N,)."""
    X_list: list[list[float]] = []
    y_list: list[int] = []
    for sp in catalog:
        sid = str(sp.get("id", ""))
        if sid not in species_ids:
            continue
        tags = sp.get("tags") or []
        vec = _tags_to_vector(tags, vocab)
        X_list.append(vec)
        y_list.append(species_ids.index(sid))
    return torch.tensor(X_list, dtype=torch.float32), torch.tensor(y_list, dtype=torch.long)


def _check_ready() -> None:
    if not TORCH_AVAILABLE:
        raise ImportError(
            "torch is not installed. Install: pip install -e \".[torch]\" or pip install torch"
        )


def train_baseline(
    epochs: int = 50,
    lr: float = 0.01,
    hidden_size: int = 128,
    save_path: str | Path | None = None,
) -> dict[str, Any]:
    """Train the TorchBaselineClassifier on the species catalog.

    Parameters
    ----------
    epochs : int
        Number of training epochs (default 50).
    lr : float
        Learning rate (default 0.01).
    hidden_size : int
        Hidden layer dimension (default 128).
    save_path : str or Path or None
        Where to save model checkpoint. Defaults to
        ``RUNS_DIR / torch_baseline_model.pt``.

    Returns
    -------
    dict with keys: model_path, vocab_size, num_classes, epochs, final_loss.
    """
    _check_ready()
    catalog = load_species_catalog()
    vocab = _build_vocab(catalog)
    species_ids = _get_species_id_list(catalog)

    X, y = _prepare_training_data(catalog, vocab, species_ids)
    num_classes = len(species_ids)

    model = TorchBaselineClassifier(
        vocab_size=len(vocab),
        num_classes=num_classes,
        hidden_size=hidden_size,
    )
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    final_loss = 0.0
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        logits = model(X)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        final_loss = float(loss.item())

    # Save
    if save_path is None:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        save_path = RUNS_DIR / "torch_baseline_model.pt"

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "vocab": vocab,
        "species_ids": species_ids,
        "model_state_dict": model.state_dict(),
        "vocab_size": len(vocab),
        "num_classes": num_classes,
        "hidden_size": hidden_size,
    }
    torch.save(checkpoint, str(save_path))

    return {
        "model_path": str(save_path),
        "vocab_size": len(vocab),
        "num_classes": num_classes,
        "epochs": epochs,
        "final_loss": round(final_loss, 6),
    }


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict(
    tags: list[str],
    model_path: str | Path = "data/runs/torch_baseline_model.pt",
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Predict species from a list of trait tags.

    Parameters
    ----------
    tags : list[str]
        Trait tags describing the plant.
    model_path : str or Path
        Path to the saved model checkpoint.
    top_k : int
        Number of top predictions to return (default 3).

    Returns
    -------
    list of dict with keys: species_id, score, species_name (if known).
    Returns empty list if torch is unavailable or model file missing.
    """
    if not TORCH_AVAILABLE:
        return []

    model_path = Path(model_path)
    if not model_path.is_file():
        return []

    try:
        checkpoint = torch.load(str(model_path), map_location="cpu")
    except Exception:  # pragma: no cover
        return []

    vocab: dict[str, int] = checkpoint["vocab"]
    species_ids: list[str] = checkpoint["species_ids"]
    hidden_size: int = checkpoint.get("hidden_size", 128)

    vec = _tags_to_vector(tags, vocab)
    x = torch.tensor([vec], dtype=torch.float32)

    model = TorchBaselineClassifier(
        vocab_size=len(vocab),
        num_classes=len(species_ids),
        hidden_size=hidden_size,
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1).squeeze(0)

    top_indices = torch.topk(probs, min(top_k, len(species_ids))).indices.tolist()

    # Load catalog for human-readable names
    catalog = load_species_catalog()
    name_map: dict[str, str] = {}
    for sp in catalog:
        sid = str(sp.get("id", ""))
        name_map[sid] = sp.get("common_name", sid)

    results: list[dict[str, Any]] = []
    for idx in top_indices:
        sid = species_ids[idx]
        results.append({
            "species_id": sid,
            "common_name": name_map.get(sid, sid),
            "score": round(float(probs[idx].item()), 4),
        })
    return results