"""Build consolidated species data for the web demo."""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "species")
DST = os.path.join(ROOT, "web", "data")

os.makedirs(DST, exist_ok=True)

species = []
all_tags = set()

for fpath in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    with open(fpath, encoding="utf-8") as f:
        data = json.load(f)
    if all(k in data for k in ("id", "common_name", "tags", "care")):
        species.append(data)
        for t in data["tags"]:
            all_tags.add(t.lower().strip())

out = {"species": species, "tags": sorted(all_tags)}

with open(os.path.join(DST, "species.min.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"), ensure_ascii=False)

print(f"Wrote {len(species)} species, {len(all_tags)} tags")
