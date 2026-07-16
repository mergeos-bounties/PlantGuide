# PlantGuide

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-0E8A16.svg)](pyproject.toml)
[![Photo ID](https://img.shields.io/badge/demo-photo%20identify-22c55e.svg)](data/samples/photos/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**PlantGuide** identifies plants from a **photo** (or trait tags) and returns a full **care card** — light, water, soil, humidity, tips — as JSON for gardening apps. Photo ID ships as an **offline demo** (synthetic plant images + visual heuristics + catalog match); vision models can replace the toy ranker via bounties.

**Product:** [mergeos-bounties/PlantGuide](https://github.com/mergeos-bounties/PlantGuide)

---

## Table of contents

- [Photo demo (identify + care)](#photo-demo-identify--care)
- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [How photo ID works](#how-photo-id-works)
- [App care report](#app-care-report)
- [Species catalog](#species-catalog)
- [Diagrams](#diagrams)
- [Repository layout](#repository-layout)
- [Development](#development)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)

---

## Photo demo (identify + care)

End-to-end offline path: **plant photo → species match → care + watering + SVG care card**.

```powershell
pip install -e ".[dev]"

# List bundled demo plant photos
plantguide demo photos

# Full demo (default photo = monstera)
plantguide demo photo
plantguide demo photo -i data/samples/photos/snake_demo.jpg --out data/out/snake-photo-demo.json

# Identify only
plantguide identify image -i data/samples/photos/monstera_demo.jpg -k 3

# Care for the matched species
plantguide care show -s monstera_deliciosa
plantguide care water -s monstera_deliciosa --season summer
plantguide care svg -s monstera_deliciosa
```

Example output (abridged):

```text
PlantGuide photo demo
  image:   data/samples/photos/monstera_demo.jpg
  species: Monstera (monstera_deliciosa)
  hit@1:   True
  light:   Bright indirect; avoid harsh midday sun
  water:   Water when top 2-3 cm of soil is dry
  soil:    Chunky aroid mix (bark + perlite + peat/coco)
  tip:     Provide a moss pole for climbing
SVG care card  data/out/monstera_deliciosa-care.svg
```

Bundled demo photos (license-safe synthetic leaves):

| File | Expected species |
| --- | --- |
| `data/samples/photos/monstera_demo.jpg` | `monstera_deliciosa` |
| `data/samples/photos/snake_demo.jpg` | `snake_plant` |
| `data/samples/photos/pothos_demo.jpg` | `pothos_golden` |
| `data/samples/photos/aloe_demo.jpg` | `aloe_vera` |
| `data/samples/photos/peace_demo.jpg` | `peace_lily` |
| `data/samples/photos/pilea_demo.jpg` | `pilea_peperomioides` |

Regenerate photos:

```powershell
python scripts/generate_demo_photos.py
```

Your own photo (JPG/PNG):

```powershell
plantguide identify image -i path\to\leaf.jpg
plantguide care show -s <species_id_from_match>
```

---

## Highlights

| Mode | Description |
| --- | --- |
| **Photo identify** | `identify image` — photo → tags → ranked species + care |
| **Photo + care demo** | `demo photo` — full pipeline + watering note + SVG |
| **Identify by tags** | Comma-separated traits → ranked species |
| **Identify sample** | Observation JSON fixtures → ranked IDs |
| **Care cards** | Light, water, soil, humidity, tips, toxicity |
| **Watering hints** | Seasonal watering guidance |
| **Collection** | Track plants + watering due dates |
| **Toy train** | Calibration report under `data/runs/` |

---

## Screenshots

| Species | Identify | Care |
| :---: | :---: | :---: |
| ![Species](docs/screenshots/demo-species.png) | ![Identify](docs/screenshots/demo-identify.png) | ![Care](docs/screenshots/demo-care.png) |
| *Catalog list* | *Tag / sample match* | *Monstera care card* |

---

## Quick start

```powershell
cd PlantGuide
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

plantguide version
plantguide species list

# Photo → ID → care (main demo)
plantguide demo photo -i data/samples/photos/monstera_demo.jpg

# Tags / care
plantguide identify tags -t "variegated,trailing,indoor" -k 3
plantguide care show -s monstera_deliciosa
plantguide care water -s monstera_deliciosa --season summer
plantguide app demo --sample data/samples/obs_monstera.json --out data/out/e2e-monstera-care-report.json
```

---

## CLI reference

| Command | Purpose |
| --- | --- |
| `plantguide version` | Version + species count + demo photo count |
| `plantguide demo photo [-i photo]` | **Photo → ID → care** end-to-end |
| `plantguide demo photos` | List bundled demo plant images |
| `plantguide identify image -i <file>` | Identify from photo (+ care card) |
| `plantguide identify tags -t …` | Rank species by tags |
| `plantguide identify sample -f …` | Identify from observation JSON |
| `plantguide care show -s <id>` | Care card JSON |
| `plantguide care water -s <id>` | Seasonal watering hint |
| `plantguide care svg -s <id>` | SVG care card file |
| `plantguide species list` | Full catalog table |
| `plantguide collection add/list/due` | User plant collection |
| `plantguide app demo --sample …` | App-ready ID + care report |
| `plantguide train toy` | Toy calibration |

---

## How photo ID works

```text
Photo (JPG/PNG)
    │
    ├─► Demo manifest / sidecar tags (fixtures)     ─┐
    │                                                 ├─► ToyPlantIdentifier (Jaccard on tags)
    └─► Visual heuristics (green ratio, variegation)─┘
                                                      │
                                                      ▼
                                              Ranked species + care card
```

- **Offline** — no network, no paid vision API.
- **Fixtures** under `data/samples/photos/` guarantee stable demos for docs/CI.
- **Any image** still runs heuristics → tags → catalog match (accuracy is demo-grade).
- Real ML vision models are a natural bounty upgrade (`vision` / torch extras reserved).

---

## App care report

Generate one JSON report that an app demo can embed:

```powershell
plantguide app demo --sample data/samples/obs_monstera.json --out data/out/e2e-monstera-care-report.json
plantguide demo photo -i data/samples/photos/monstera_demo.jpg --out data/out/photo-demo-report.json
```

Reports include `query_tags` / image path, ranked `matches`, `care` card, and (for photo demo) `watering` + optional `care_svg`.

---

## Species catalog

JSON packs under `data/species/` (Monstera, snake plant, pothos, aloe, peace lily, ferns, herbs, …).  
Each has `tags` + structured `care` fields used by identify + care commands.

```powershell
plantguide species list
```

---

## Diagrams

[Architecture (HTML)](docs/diagrams/architecture.html) · [Workflow (HTML)](docs/diagrams/workflow.html)

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="PlantGuide architecture" width="100%" />
</p>

*Generated with [archify](https://github.com/tt-a1i).*

---

## Repository layout

```text
src/plantguide/
  identify/   # tags, sample JSON, vision photo path
  care/       # care cards, watering, SVG export
  data/       # loaders
  collection/ # user plants
  integrations/
data/
  species/              # catalog JSON
  samples/              # obs_*.json
  samples/photos/       # demo plant JPGs + manifest.json
  out/                  # SVG / reports
scripts/generate_demo_photos.py
```

---

## Development

```powershell
pip install -e ".[dev]"
python scripts/generate_demo_photos.py
ruff check src tests
pytest -q
plantguide demo photo
```

---

## MergeOS bounties

Star → claim issue → PR to **master** → MRG **25–200**.  
Photo/vision upgrades, more species packs, and real image models welcome.  
See [mergeos](https://github.com/mergeos-bounties/mergeos), [docs/BOUNTY.md](docs/BOUNTY.md), and [Species Photo Evidence Requirements](docs/species-photo-evidence.md).

---

## License

[MIT](LICENSE)
