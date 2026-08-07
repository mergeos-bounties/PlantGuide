# PlantGuide Web Demo

Tag picker + care card UI — a lightweight static web app for exploring
PlantGuide's species catalog.

## Quick start

Open `web/index.html` in any browser, or serve locally:

```bash
python3 -m http.server 8080 --directory web
# then open http://localhost:8080
```

## Features

- **Tag picker** — browse and filter 244 unique plant traits (tropical,
  succulent, indoor, climbing, etc.). Search tags by keyword and select
  multiple to narrow results.
- **Species grid** — cards show common name, scientific name, summary, and
  matching tags. Sorted by match score when tags are active.
- **Care card modal** — click any species to view full care details: light,
  water, soil, humidity, temperature, fertilizer, toxicity, common issues,
  and pro tips.

## Data

Species data is loaded from `data/species.min.json`, generated from
`data/species/*.json` in the repository root. The catalog contains
111 plant species with structured care information.

To regenerate:

```bash
cd .. && python3 scripts/build_web_data.py
```

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main page with tag picker and results grid |
| `app.js` | Tag filtering, species matching, care card modal |
| `style.css` | Responsive styles with PlantGuide green theme |
| `data/species.min.json` | Compiled species + tags (auto-generated) |
| `README.md` | This file |

## Screenshots

See the PR description for screenshots of the tag picker and care card.
