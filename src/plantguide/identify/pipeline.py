from __future__ import annotations

from pathlib import Path

from plantguide.care.cards import care_card_for_species
from plantguide.data.loader import load_sample
from plantguide.identify.ranking import compute_weighted_scores
from plantguide.models.toy import ToyPlantIdentifier, tags_from_text

# Global switch: set to "weighted" to use the ranking model from #11
RANKING_MODE: str | None = "weighted"  # None = use ToyPlantIdentifier


def _get_catalog() -> list[dict]:
    """Load full species catalog for weighted ranking."""
    from plantguide.data.loader import load_species_catalog
    return load_species_catalog()


def identify_from_tags(tags: str | list[str], top_k: int = 3, with_care: bool = True) -> dict:
    if isinstance(tags, str):
        tag_list = tags_from_text(tags)
    else:
        tag_list = [str(t).strip() for t in tags if str(t).strip()]

    if RANKING_MODE == "weighted":
        catalog = _get_catalog()
        scored = compute_weighted_scores(tag_list, catalog)
        matches = scored[:top_k]
        model = "WeightedRankingV1"
    else:
        matches = ToyPlantIdentifier().identify(tag_list, top_k=top_k)
        model = "ToyPlantIdentifier"

    result: dict = {
        "query_tags": tag_list,
        "matches": matches,
        "model": model,
    }
    if with_care and matches:
        top = matches[0]
        result["top_care"] = care_card_for_species(str(top["species_id"]))
        result["top_species_id"] = top.get("species_id")
    return result


def identify_from_sample(path: Path, top_k: int = 3) -> dict:
    sample = load_sample(path)
    result = identify_from_tags(sample.get("tags") or [], top_k=top_k)
    result["sample_id"] = sample.get("id")
    result["source"] = str(path)
    expected = sample.get("expected_species")
    if expected and result.get("matches"):
        top_id = str(result["matches"][0].get("species_id") or "").lower()
        result["expected_species"] = expected
        result["hit_top1"] = top_id == str(expected).lower()
    return result


def identify_from_image(path: Path, top_k: int = 3, with_care: bool = True) -> dict:
    """Photo → tags → species ranking + care card (offline demo vision)."""
    from plantguide.identify.vision import identify_from_image as _from_image

    return _from_image(path, top_k=top_k, with_care=with_care)
