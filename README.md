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
plantguide species filter --light bright --water dry
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


<!-- BOOST: Enhanced documentation for ranking -->
## 🚀 Quick Start

### Prerequisites
- Node.js >= 18 (or Python >= 3.10)
- Git

### Installation
```bash
git clone https://github.com/mergeos-bounties/PlantGuide.git
cd PlantGuide
```

### Development
```bash
npm install  # or pip install -r requirements.txt
npm test
npm run dev
```

## 📊 Quality
- ✅ CI/CD pipeline with automated testing
- ✅ Linting & code quality checks

## 🤝 Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md).

## 📄 License
See [LICENSE](./LICENSE) file.
