# Torch Baseline — Species ID from Trait Tags

A lightweight PyTorch MLP baseline for species identification using trait tags.

## Overview

The `TorchBaselineClassifier` is a CPU-only, 2-layer MLP that maps a multi-hot
vector of trait tags (e.g. `tropical`, `fenestrated leaves`, `climbing`) to a
species classification. It is trained on the species catalog's tag data,
making it a **learning-based alternative** to the Jaccard-similarity-based
`ToyPlantIdentifier`.

## Usage

### Install torch

```bash
pip install -e ".[torch]"
# or
pip install torch
```

### Train

```bash
python -m plantguide.train.torch_train --epochs 50 --lr 0.01
```

Output is saved to `data/runs/torch_baseline_model.pt` by default.

Options:
| Flag | Default | Description |
|------|---------|-------------|
| `--epochs` | 50 | Number of training epochs |
| `--lr` | 0.01 | Learning rate |
| `--hidden-size` | 128 | Hidden layer dimension |
| `--save-path` | `data/runs/torch_baseline_model.pt` | Output path |

### Infer

```bash
python -m plantguide.identify.torch_infer --tags "tropical,fenestrated leaves,climbing"
```

Options:
| Flag | Default | Description |
|------|---------|-------------|
| `--tags` | (required) | Comma-separated trait tags |
| `--top-k` | 3 | Number of top predictions |
| `--model-path` | `data/runs/torch_baseline_model.pt` | Model checkpoint path |

### Python API

```python
from plantguide.models.torch_baseline import train_baseline, predict

# Train
result = train_baseline(epochs=50, lr=0.01)
print(f"Final loss: {result['final_loss']}")

# Predict
predictions = predict(["tropical", "fenestrated leaves", "climbing"], top_k=3)
for p in predictions:
    print(f"{p['common_name']} ({p['species_id']}): {p['score']:.2%}")
```

## Architecture

```
Input (vocab_size) → Linear(128) → BatchNorm → ReLU → Dropout(0.3) → Linear(num_classes) → Logits
```

- **Input**: Multi-hot vector of trait tags (vocabulary built from all species)
- **Hidden**: 128 units with batch norm, ReLU activation, and 30% dropout
- **Output**: Raw logits over species classes (softmax applied during inference)

## License

This code is part of PlantGuide (MIT). Training data comes from the bundled
species catalog (see `data/species/`). No external datasets are used.

## Notes

- **CPU-only**: No GPU required. All tests run on CPU.
- **Optional dependency**: If torch is not installed, all `predict()` calls
  return an empty list. Tests skip gracefully.
- **Synthetic features**: The model is trained on tag vectors, not real images.
  This is a baseline for the Photo ID bounty; production-level vision models
  would use actual photo data.
- **Training is deterministic**: The vocabulary is sorted for determinism.
  Results may vary slightly between torch versions.