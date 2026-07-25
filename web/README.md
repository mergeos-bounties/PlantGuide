# PlantGuide Web Demo: tag picker + care card UI

A lightweight web interface for PlantGuide's plant identification and care card system.

## Quick start

```bash
# Install PlantGuide dependencies (if not already installed)
pip install -e ".[api]"

# From the project root, start the web server
cd web && python3 server.py
```

Open **http://127.0.0.1:8765** in your browser.

## Features

### 🏷️ Tag picker
Select one or more plant traits (e.g., "tropical", "climbing", "indoor", "large leaves") and click **Identify** to find matching plants.

### 📋 Results
- **Match score** — Jaccard similarity percentage
- **Tag overlap** — which tags matched (✓) and which species-specific tags exist
- **Care card** — the top match shows a full care guide with light, water, soil, humidity, temperature, fertilizer, toxicity, common issues, and tips

### API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tags` | GET | All available trait tags |
| `/api/species` | GET | Full species catalog |
| `/api/species/{id}/care` | GET | Care card for a species |
| `/api/species/{id}/water?season=summer` | GET | Watering hint by season |
| `/api/identify` | POST | Identify from tags (body: `{"tags": [...], "top_k": 5}`) |

## How it works

The server is built on Python's standard library `http.server` — no additional dependencies required beyond PlantGuide itself. The frontend is a single HTML page with vanilla JavaScript.

## Screenshots

![Tag picker with selected traits](screenshots/tag-picker.png)
![Care card results](screenshots/care-card.png)