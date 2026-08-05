# Contributing to PlantGuide

Welcome! PlantGuide identifies plants from photos (or trait tags) and returns care cards. Contributions are rewarded through [MergeOS bounties](https://github.com/mergeos-bounties/mergeos).

## Getting started

```bash
git clone https://github.com/mergeos-bounties/PlantGuide.git
cd PlantGuide
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

Verify everything works:

```bash
pytest -q
plantguide version
plantguide demo photo
```

## Project layout

```
src/plantguide/
  identify/   # photo/tags/sample identification
  care/       # care cards, watering, SVG export
  data/       # species catalog loader
  collection/ # user plant collection tracker
  integrations/ # SDK, app reports
  train/      # toy calibration
  api/        # FastAPI (optional extra)
data/
  species/    # catalog JSON packs
  samples/    # observation fixtures
  samples/photos/  # demo plant JPGs
tests/        # pytest suite
```

## Finding something to work on

Browse [open bounties](https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Abounty). Look for `good first issue` labels — those are quick wins (25–50 MRG) and great for first-time contributors.

## Bounty workflow

1. **Star** the [PlantGuide repo](https://github.com/mergeos-bounties/PlantGuide) and [MergeOS](https://github.com/mergeos-bounties/mergeos)
2. **Claim** by commenting `I claim this bounty` on the issue
3. **Also claim** on [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to your issue
4. **Fork** the repo and create a branch
5. **Implement** the feature or fix
6. **Test** with `pytest -q`
7. **Open a PR** to `master` with `Fixes #<issue-number>` in the description
8. Maintainer reviews → merge → MRG credit on the MergeOS ledger

## Code style

- Python 3.11+, `ruff` formatted (line length 100)
- Type hints encouraged
- `typer` for CLI, `rich` for output tables, `pydantic` for data models
- Keep features optional with extras (`torch`, `vision`, `api`); see `pyproject.toml`

Run linting:

```bash
ruff check src tests
ruff format src tests
```

## Testing

Tests use `pytest` and live under `tests/`. Run:

```bash
pytest -q
pytest --cov=src
```

## MergeOS bounties

- Reward scale: **25 / 50 / 100 / 200 MRG** — check issue label
- All work lands on `mergeos-bounties/PlantGuide`
- See [docs/BOUNTY.md](docs/BOUNTY.md) for policy details
- Questions? Comment on your issue or the MergeOS discussion board