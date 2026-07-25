"""Torch baseline training script.

Usage:
    python -m plantguide.train.torch_train --epochs 50 --lr 0.01
"""

from __future__ import annotations

import argparse
import json

from plantguide.config import RUNS_DIR
from plantguide.models.torch_baseline import train_baseline


def main() -> None:
    parser = argparse.ArgumentParser(description="Train TorchBaselineClassifier")
    parser.add_argument(
        "--epochs", type=int, default=50, help="Number of training epochs"
    )
    parser.add_argument(
        "--lr", type=float, default=0.01, help="Learning rate"
    )
    parser.add_argument(
        "--hidden-size", type=int, default=128, help="Hidden layer dimension"
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default=str(RUNS_DIR / "torch_baseline_model.pt"),
        help="Model checkpoint output path",
    )
    args = parser.parse_args()

    result = train_baseline(
        epochs=args.epochs,
        lr=args.lr,
        hidden_size=args.hidden_size,
        save_path=args.save_path,
    )

    print(json.dumps(result, indent=2))
    print(f"\nModel saved to: {result['model_path']}")


if __name__ == "__main__":
    main()