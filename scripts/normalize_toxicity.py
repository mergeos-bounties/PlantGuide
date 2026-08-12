"""Normalize toxicity fields across data/species/*.json.

Rules:
- Top-level `toxicity` must be a list of normalized tokens.
- Allowed tokens: pet_safe, toxic_to_pets, toxic_to_horses, edible, toxic_to_humans
- If top-level is a string like "Non-toxic" -> ["pet_safe"]
- If missing, infer from care.toxicity text (lowercased):
   - contains "non-toxic" / "non toxic" / "pet-safe" / "pet safe" -> pet_safe
   - contains "edible" or "culinary" -> pet_safe + edible
   - contains "toxic" -> toxic_to_pets
   - heavymatch for horses
   - "unknown" -> []
- Adds educational disclaimer prefix if toxicity text lacks disclaimer.
"""
from __future__ import annotations
import json
from pathlib import Path

SPECIES_DIR = Path("data/species")

DISCLAIMER = "Educational only — not veterinary/medical advice. Verify with a vet."

def infer_tokens(care_toxicity: str, top) -> list[str]:
    t = (care_toxicity or "").lower()
    # already normalized list: return as-is lowercased
    if isinstance(top, list) and all(isinstance(x, str) for x in top):
        # normalize existing tokens
        norm = [x.strip().lower().replace("-", "_").replace(" ", "_") for x in top if x.strip()]
        # filter allowed
        allowed = {"pet_safe", "toxic_to_pets", "toxic_to_horses", "edible", "toxic_to_humans"}
        return [x for x in norm if x in allowed] or norm

    # string top-level indicates legacy non-toxic
    if isinstance(top, str):
        s = top.strip().lower()
        if "non" in s and "toxic" in s:
            return ["pet_safe"]
        if "non-toxic to pets" in s:
            return ["pet_safe"]
        if s in ("", "unknown"):
            s = ""
        # fallback infer from care text below
    # infer from care text
    if not t:
        return []
    # check non-toxic first (contains toxic substring)
    if "non-toxic" in t or "non toxic" in t or "non_toxic" in t:
        tokens = ["pet_safe"]
        if "edible" in t or "culinary" in t:
            tokens.append("edible")
        return tokens
    if "pet-safe" in t or "pet safe" in t or "pet_safe" in t:
        return ["pet_safe"]
    if "toxic" in t or "irritat" in t or "calcium oxalate" in t or "buxine" in t or "solanine" in t:
        tokens = ["toxic_to_pets"]
        if "horse" in t:
            tokens.append("toxic_to_horses")
        if "human" in t and "non-toxic" not in t:
            tokens.append("toxic_to_humans")
        return tokens
    if "edible" in t or "culinary" in t or "safe for consumption" in t:
        return ["pet_safe", "edible"]
    if "spines can injure" in t or "sharp spines" in t:
        return ["pet_safe"]
        tokens = ["toxic_to_pets"]
        if "horse" in t:
            tokens.append("toxic_to_horses")
        if "human" in t and "non-toxic" not in t:
            tokens.append("toxic_to_humans")
        return tokens
    return []

def normalize_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    top = data.get("toxicity", None)
    care = data.get("care") or {}
    care_tox = care.get("toxicity", "")
    inferred = infer_tokens(care_tox, top)
    # Special: if top was string "Non-toxic" with empty care, treat as pet_safe
    if isinstance(top, str) and not care_tox:
        low = top.lower()
        if "non-toxic" in low or "non toxic" in low:
            inferred = ["pet_safe"]
        elif low.strip() in ("", "unknown"):
            inferred = []
        else:
            # generic string with toxic hint
            if "toxic" in low and "non" not in low:
                inferred = ["toxic_to_pets"]
    # If file already had correct list and care text aligns, keep it
    # For missing top but care text toxicity says non-toxic, inferred will be pet_safe correctly
    # Edge: if inferred empty and care has no toxicity but file is known safe ornamental, default to []
    # Don't force pet_safe on files with no care text at all (like areca minimal JSON)
    # Those string "Non-toxic" files should become pet_safe
    if isinstance(top, str) and inferred == []:
        # legacy string header without care block - preserve string meaning
        if top.lower().strip() in ("non-toxic", "non toxic", "non-toxic to pets"):
            inferred = ["pet_safe"]
    changed = False
    if data.get("toxicity") != inferred:
        data["toxicity"] = inferred
        changed = True
    # ensure care.disclaimer or note? Add disclaimer field if toxicity present and not already there
    if inferred and "disclaimer" not in data and "disclaimer" not in care:
        # add to care block as educational note
        if isinstance(care, dict):
            # append disclaimer to care.tips or keep separate field
            data.setdefault("care", {})["disclaimer"] = DISCLAIMER
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed

if __name__ == "__main__":
    changed = 0
    for p in sorted(SPECIES_DIR.glob("*.json")):
        if normalize_file(p):
            changed += 1
            print(f"normalized {p.name} -> {json.loads(p.read_text())['toxicity']}")
    print(f"Done. Changed {changed} files.")
