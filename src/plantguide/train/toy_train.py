from __future__ import annotations

import json

from plantguide.config import RUNS_DIR
from plantguide.data.loader import list_sample_files, load_sample
from plantguide.identify.pipeline import identify_from_sample


def train_toy(epochs: int = 3) -> dict:
    """Evaluate top-1 hit-rate on labeled trait samples each epoch."""
    samples = list_sample_files()
    if not samples:
        raise FileNotFoundError("no samples under data/samples")

    history = []
    for epoch in range(1, max(1, epochs) + 1):
        labeled = 0
        hits = 0
        for path in samples:
            sample = load_sample(path)
            if not sample.get("expected_species"):
                continue
            labeled += 1
            result = identify_from_sample(path, top_k=3)
            if result.get("hit_top1"):
                hits += 1
        acc = (hits / labeled) if labeled else 0.0
        history.append(
            {
                "epoch": epoch,
                "top1_hit_rate": round(acc, 4),
                "n_labeled": labeled,
                "n_samples": len(samples),
            }
        )

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RUNS_DIR / "toy_train_report.json"
    report = {
        "model": "ToyPlantIdentifier",
        "epochs": epochs,
        "history": history,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {"report_path": str(report_path), **report}
