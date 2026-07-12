from __future__ import annotations

from pathlib import Path

from plantguide.train import toy_train as toy_train_mod
from plantguide.train.toy_train import train_toy


def test_train_toy(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(toy_train_mod, "RUNS_DIR", tmp_path / "runs")
    report = train_toy(epochs=2)
    assert report["history"][-1]["top1_hit_rate"] >= 0.5
    assert Path(report["report_path"]).exists()
