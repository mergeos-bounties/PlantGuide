"""
Enhanced tag-based ranking model beyond simple Jaccard.

Provides weighted scoring using tag importance factors:
- Rare/specific tags are weighted higher
- Category matches (e.g., light, water, soil) get bonus
- Partial overlapping (e.g. "low light" vs "medium light") is supported
"""

from __future__ import annotations

import re
import math
from collections import Counter
from typing import Any

# ── Tag importance heuristics ─────────────────────────────────────────

SPECIFIC_TAG_PATTERNS = [
    r"\b(specific|rare|unique|distinctive|unusual)\b",
    r"\b(variegat|fenestrat|carnivor|epiphyt)\w*",
    r"\bbonsai\b",
    r"\b(calathea|maranta|alocasia|begonia|philodendron|pilea)\b",
]

COMMON_TAGS = {
    "indoor", "outdoor", "easy care", "beginner", "pet friendly",
    "air purifying", "tropical", "ornamental", "green", "colorful",
    "small", "medium", "large", "fast growing", "slow growing",
    "flowering", "non-flowering", "trailing", "upright", "climbing",
}

CATEGORY_PREFIXES = {
    "light": {"low", "medium", "bright", "direct", "indirect"},
    "water": {"low", "moderate", "high", "drought", "frequent"},
    "soil": {"well", "moist", "dry", "sandy", "loamy", "clay"},
    "humidity": {"low", "moderate", "high"},
}


def _compute_tag_weight(tag: str, *, tag_freq: Counter | None = None) -> float:
    """Compute importance weight for a single tag."""
    tag_lower = tag.lower().strip()

    # Very common/easy tags get lower weight
    if tag_lower in COMMON_TAGS:
        return 0.6

    # Tags matching specific patterns get higher weight
    for pat in SPECIFIC_TAG_PATTERNS:
        if re.search(pat, tag_lower):
            return 1.4

    # Any tag with a specific species name, color name, or numeric gets boost
    if any(c.isdigit() for c in tag):
        return 1.3

    # Category tags (light, water, humidity, soil) get moderate weight
    for cat, prefixes in CATEGORY_PREFIXES.items():
        for p in prefixes:
            if tag_lower.startswith(p) or p in tag_lower.split():
                return 1.0

    # Default
    return 1.0


def _compute_tag_frequency(all_species_tags: list[list[str]]) -> Counter:
    """Build a frequency map of all tags across the catalog to weight rare tags higher."""
    freq: Counter = Counter()
    for tags in all_species_tags:
        freq.update(t.lower().strip() for t in tags)
    return freq


def _compute_tag_frequency_from_catalog(catalog: list[dict]) -> Counter:
    """Extract tag frequency from the species catalog."""
    return _compute_tag_frequency(
        [s.get("tags", []) for s in catalog]
    )


def _category_overlap(query_tags: list[str], species_tags: list[str]) -> float:
    """Detect if query tags and species tags share category prefixes."""
    query_cats: set[str] = set()
    species_cats: set[str] = set()
    for t in query_tags:
        for cat, prefixes in CATEGORY_PREFIXES.items():
            for p in prefixes:
                if t.lower().startswith(p) or p in t.lower().split():
                    query_cats.add(cat)
    for t in species_tags:
        for cat, prefixes in CATEGORY_PREFIXES.items():
            for p in prefixes:
                if t.lower().startswith(p) or p in t.lower().split():
                    species_cats.add(cat)

    overlap = len(query_cats & species_cats)
    total = len(query_cats | species_cats)
    return overlap / total if total > 0 else 0.0


def compute_weighted_scores(
    query_tags: list[str],
    catalog: list[dict],
    tag_freq: Counter | None = None,
    alpha: float = 0.6,       # Jaccard weight
    beta: float = 0.3,        # category bonus weight
    gamma: float = 0.1,       # IDF boost
) -> list[dict[str, Any]]:
    """
    Compute weighted match scores between query tags and each species.

    Returns list of dicts: species_id, score, matched_tags, species_only_tags,
                           query_only_tags, explanation
    """
    if tag_freq is None:
        tag_freq = _compute_tag_frequency_from_catalog(catalog)

    query_lower = [t.lower().strip() for t in query_tags if t.strip()]
    total_tags = sum(tag_freq.values()) or 1
    n_species = len(catalog) or 1

    results = []
    for species in catalog:
        species_tags = [t for t in species.get("tags", [])]
        species_lower = [t.lower().strip() for t in species_tags if t.strip()]

        matched = []
        species_only = []
        query_only = []

        for sq in query_lower:
            if any(sq == st or _fuzzy_match(sq, st) for st in species_lower):
                matched.append(sq)
            else:
                query_only.append(sq)

        for st in species_lower:
            if not any(st == sq or _fuzzy_match(sq, st) for sq in query_lower):
                species_only.append(st)

        # Weighted Jaccard
        intersection_weight = sum(
            _compute_tag_weight(t, tag_freq=tag_freq) for t in matched
        )
        union_weight = (
            sum(_compute_tag_weight(t, tag_freq=tag_freq) for t in query_lower)
            + sum(_compute_tag_weight(t, tag_freq=tag_freq) for t in species_only)
        )
        jaccard = intersection_weight / union_weight if union_weight > 0 else 0.0

        # Category overlap bonus
        cat_bonus = _category_overlap(query_lower, species_lower) * beta

        # IDF boost: reward matching uncommon tags
        idf_boost = 0.0
        for t in matched:
            freq = tag_freq.get(t, 1)
            idf = math.log((n_species - freq + 0.5) / (freq + 0.5) + 1.0)
            idf_boost += gamma * idf / max(len(matched), 1)

        score = min(1.0, alpha * jaccard + cat_bonus + idf_boost)

        # Build explanation
        parts = []
        if matched:
            parts.append(f"matched {len(matched)} tag(s)")
        if query_only:
            parts.append(f"unmatched query tags: {', '.join(query_only[:3])}")
        if cat_bonus > 0.05:
            parts.append(f"care-category overlap: +{cat_bonus:.2f}")
        explanation = "; ".join(parts) if parts else "no match"

        results.append({
            "species_id": species.get("id", ""),
            "common_name": species.get("common_name", ""),
            "scientific_name": species.get("scientific_name", ""),
            "score": round(score, 4),
            "matched_tags": matched,
            "species_only_tags": species_only,
            "query_only_tags": query_only,
            "explanation": explanation,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def _fuzzy_match(query_tag: str, species_tag: str) -> bool:
    """
    Check for partial/soft tag matches.
    Examples: "low light" ~ "low" or "bright indirect light" ~ "indirect"
    """
    q_words = set(query_tag.split())
    s_words = set(species_tag.split())
    return len(q_words & s_words) >= min(len(q_words), len(s_words), 1)
