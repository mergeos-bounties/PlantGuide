# PlantGuide Web Demo

A lightweight, standalone web application for plant symptom checking and care card generation. Built with vanilla HTML, CSS, and JavaScript — no frameworks, no build step, no dependencies.

## Features

- **Symptom Tag Picker**: Select from 12 plant symptom tags (yellowing leaves, brown spots, wilting, root rot, powdery mildew, pest damage, stunted growth, crispy edges, mushy stems, mold on soil, holes in leaves, white powder)
- **Care Card Generation**: Click "Diagnose" to match symptoms against 10 plant conditions and get detailed care cards
- **Severity Indicators**: Each condition shows severity level (low/medium/high) with color-coded badges
- **Matched Symptoms**: Symptom tags are highlighted when they match your selection
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Zero Dependencies**: Just open `index.html` in any modern browser

## Plant Conditions Covered

| Condition | Severity | Key Symptoms |
|-----------|----------|-------------|
| Powdery Mildew | Medium | White powder, leaf distortion |
| Chlorosis (Yellowing) | Medium | Yellowing, pale leaves |
| Leaf Spot Disease | Medium | Brown spots |
| Wilting / Vascular Wilt | High | Wilting, drooping, limp leaves |
| Root Rot | High | Wilting, yellowing, mushy stems |
| Pest Infestation | Medium | Holes in leaves, sticky residue, visible insects |
| Stunted Growth | Medium | Small leaves, slow growth |
| Sunscald / Leaf Burn | Low | Brown spots, scorched leaves, crispy edges |
| Nutrient Burn | Medium | Brown spots, yellowing, crispy edges, white crust |
| Overwatering / Edema | Medium | Yellowing, wilting, mushy stems, mold on soil |

## How to Use

1. Open `web/index.html` in your browser (double-click the file, or serve with any static server)
2. Click symptom tags to select them (click again to deselect)
3. Click the **Diagnose** button to see matching care cards
4. Each care card shows:
   - Disease/condition name and severity
   - All associated symptoms (matched ones highlighted in green)
   - Treatment advice
   - Prevention tips

### Quick Start with Python

```bash
cd web
python -m http.server 8080
# Open http://localhost:8080 in your browser
```

## Files

- `index.html` — Main HTML structure
- `style.css` — All styling (CSS custom properties, responsive grid layout)
- `script.js` — Tag selection logic, care card database, fuzzy matching engine
- `README.md` — This file

## Screenshots

*(Screenshots placeholder — add screenshots of the tag picker and care card display)*
