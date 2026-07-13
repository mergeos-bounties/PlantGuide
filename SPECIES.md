# Species Catalog

> Complete overview of plant species supported by **PlantGuide**.

**Total species:** 19  
**Source:** `data/species/*.json`

---

## Quick reference

| ID | Common name | Scientific name | Light | Water | Humidity | Temp (°C) |
| --- | --- | --- | --- | --- | --- | --- |
| `aloe_vera` | Aloe Vera | *Aloe vera* | Bright indirect | Let soil dry between waterings | Low | 13–27 |
| `basil_sweet` | Sweet Basil | *Ocimum basilicum* | Full sun | Keep moist | Average | 18–30 |
| `bird_of_paradise` | Bird of Paradise | *Strelitzia reginae* | Bright indirect | Water when top 2-3 cm dry | Medium to high | 18–27 |
| `boston_fern` | Boston Fern | *Nephrolepis exaltata* | Indirect to moderate | Keep evenly moist | High | 16–24 |
| `calathea_orbifolia` | Calathea Orbifolia | *Goeppertia orbifolia* | Indirect / filtered | Keep moist, use distilled | High | 18–26 |
| `chinese_evergreen` | Chinese Evergreen | *Aglaonema commutatum* | Low to medium | Water when top soil dries | Average to medium | 18–27 |
| `english_ivy` | English Ivy | *Hedera helix* | Bright indirect | Water when top 2-3 cm dry | Medium to high | 15–24 |
| `fiddle_leaf_fig` | Fiddle Leaf Fig | *Ficus lyrata* | Bright indirect | Water when top 3-5 cm dry | Average to high | 18–29 |
| `jade_plant` | Jade Plant | *Crassula ovata* | Bright indirect | Water sparingly; let dry | Low | 15–24 |
| `lavender` | Lavender | *Lavandula angustifolia* | Full sun | Let dry between waterings | Low | 5–30 |
| `mint_spearmint` | Spearmint | *Mentha spicata* | Partial sun to shade | Keep evenly moist | Average to high | 10–28 |
| `monstera_deliciosa` | Monstera | *Monstera deliciosa* | Bright indirect | Water when top 2-3 cm dry | 50%+ preferred | 18–29 |
| `peace_lily` | Peace Lily | *Spathiphyllum wallisii* | Low to bright indirect | Water when drooping or dry | Medium-high | 18–27 |
| `pothos_golden` | Golden Pothos | *Epipremnum aureum* | Low to bright indirect | Water when top 2-3 cm dry | Average | 18–30 |
| `rosemary` | Rosemary | *Salvia rosmarinus* | Full sun | Let dry between waterings | Low to average | 10–30 |
| `rubber_plant` | Rubber Plant | *Ficus elastica* | Bright indirect | Water when top 3-4 cm dry | Average to medium | 16–27 |
| `snake_plant` | Snake Plant | *Dracaena trifasciata* | Low to bright indirect | Water every 2-4 weeks | Low to average | 15–30 |
| `spider_plant` | Spider Plant | *Chlorophytum comosum* | Indirect to moderate | Water when top 2-3 cm dry | Average | 15–27 |
| `zz_plant` | ZZ Plant | *Zamioculcas zamiifolia* | Low to bright indirect | Water monthly; very drought tolerant | Low to average | 16–30 |

---

## Usage

### List all species (CLI)

```powershell
plantguide species list
```

### Search by tags

```powershell
plantguide identify tags -t "tropical,indoor,climbing" -k 3
```

### View care card

```powershell
plantguide care show -s monstera_deliciosa
```

### Watering hints

```powershell
plantguide care water -s snake_plant --season summer
```

---

## Data format

Each species is defined in a JSON file under `data/species/`:

```json
{
  "id": "monstera_deliciosa",
  "common_name": "Monstera",
  "scientific_name": "Monstera deliciosa",
  "tags": ["tropical", "fenestrated leaves", "climbing", "indoor"],
  "care": {
    "summary": "Iconic tropical aroid with split leaves; bright indirect light.",
    "light": "Bright indirect; avoid harsh midday sun",
    "water": "Water when top 2-3 cm of soil is dry",
    "soil": "Chunky aroid mix (bark + perlite + peat/coco)",
    "humidity": "50%+ preferred",
    "temperature_c": "18-29",
    "fertilizer": "Balanced liquid monthly in spring/summer",
    "toxicity": "Toxic to pets if chewed",
    "common_issues": ["Yellow leaves from overwatering"]
  }
}
```

---

## See also

- [README](README.md) — full project overview
- [CLI reference](README.md#cli-reference)
- [App care report](README.md#app-care-report)
