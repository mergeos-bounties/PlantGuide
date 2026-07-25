"""Torch baseline inference via CLI.

Usage:
    python -m plantguide.identify.torch_infer --tags "tropical,fenestrated leaves,climbing"
"""

from __future__ import annotations

import argparse
import json

from plantguide.models.torch_baseline import TORCH_AVAILABLE, predict


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify species using TorchBaselineClassifier"
    )
    parser.add_argument(
        "--tags",
        type=str,
        required=True,
        help="Comma-separated trait tags (e.g. 'tropical,fenestrated leaves,climbing')",
    )
    parser.add_argument(
        "--top-k", type=int, default=3, help="Number of top predictions (default 3)"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="data/runs/torch_baseline_model.pt",
        help="Path to model checkpoint",
    )
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    results = predict(tags, top_k=args.top_k, model_path=args.model_path)

    if not results:
        if not TORCH_AVAILABLE:
            print('{"error": "torch not available; install with: pip install -e .[torch]"}')
        else:
            print(f'{{"error": "model not found at {args.model_path}; train first with: python -m plantguide.train.torch_train"}}')
        return

    print(json.dumps({"query_tags": tags, "predictions": results, "model": "TorchBaselineClassifier"}, indent=2))


if __name__ == "__main__":
    main()