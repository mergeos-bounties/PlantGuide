# PlantGuide

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**PlantGuide** identifies plants from traits/tags and serves **species care cards** (water, light, soil, humidity) as JSON for gardening apps.

**Product:** [mergeos-bounties/PlantGuide](https://github.com/mergeos-bounties/PlantGuide)

---

## Table of contents

- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [Species catalog](#species-catalog)
- [Diagrams](#diagrams)
- [Repository layout](#repository-layout)
- [Development](#development)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)

---

## Highlights

| Mode | Description |
| --- | --- |
| **Identify by tags** | Comma-separated traits → ranked species matches |
| **Identify sample** | Observation JSON fixtures → ranked IDs |
| **Care cards** | Per-species watering, light, soil, humidity, tips |
| **Watering hints** | Seasonal watering guidance |
| **Toy train** | Calibration report under `data/runs/` |

---

## Screenshots

| Species | Identify | Care |
| :---: | :---: | :---: |
| ![Species](docs/screenshots/demo-species.png) | ![Identify](docs/screenshots/demo-identify.png) | ![Care](docs/screenshots/demo-care.png) |
| *Catalog list* | *Tag matching* | *Monstera care card* |

---

## Quick start

```powershell
cd PlantGuide
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

plantguide version
plantguide species list
plantguide identify tags -t "variegated,trailing,indoor" -k 3
plantguide care show -s monstera_deliciosa
plantguide care water -s monstera_deliciosa --season summer
```

---

## CLI reference

| Command | Purpose |
| --- | --- |
| `plantguide version` | Version + species count |
| `plantguide species list` | Full catalog table |
| `plantguide identify tags -t …` | Rank species by tags |
| `plantguide identify sample -f …` | Identify from observation file |
| `plantguide care show -s <id>` | Care card JSON |
| `plantguide care water -s <id>` | Watering hint |
| `plantguide train toy` | Toy calibration |

---

## Species catalog

Species JSON under `data/species/` (examples):

| ID | Common name (examples) |
| --- | --- |
| `monstera_deliciosa` | Monstera |
| `pothos_golden` | Golden pothos |
| `snake_plant` | Snake plant |
| `zz_plant` | ZZ plant |
| `aloe_vera` | Aloe |
| … | See `plantguide species list` |

Observation fixtures: `data/samples/obs_*.json`.

---

## Diagrams

System architecture and workflow — full width. Open the HTML files for **dark/light theme** and export (PNG/SVG).

### Architecture

[Open interactive diagram](docs/diagrams/architecture.html)

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="PlantGuide architecture" width="100%" />
</p>

### Workflow

[Open interactive diagram](docs/diagrams/workflow.html)

<p align="center">
  <img src="docs/diagrams/workflow.svg" alt="PlantGuide workflow" width="100%" />
</p>

*Generated with [archify](https://github.com/tt-a1i).*

---

## Repository layout

```text
src/plantguide/
  cli.py
  identify/pipeline.py
  care/cards.py
  data/loader.py
  train/toy_train.py
data/species/
data/samples/
docs/screenshots/
docs/diagrams/
```

---

## Development

```powershell
pytest -q
ruff check src tests
plantguide species list
```

---

## MergeOS bounties

High demand: **species photo packs** (≥2 original photos + evidence).  
Star → claim → PR **master** → MRG **25–200**.

---

## Tiếng Việt

**PlantGuide** nhận diện cây theo tag và thẻ chăm sóc (tưới, sáng, đất).

```powershell
plantguide identify tags -t "indoor,trailing" -k 3
```

---

## License

MIT · MergeOS / ThanhTrucSolutions
