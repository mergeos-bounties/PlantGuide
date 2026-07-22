"""Normalize legacy toxicity notes into a small pet-safety schema."""

from __future__ import annotations

import re
from enum import StrEnum


class ToxicityTag(StrEnum):
    """Canonical tags exposed by loaded species records."""

    PET_SAFE = "pet_safe"
    TOXIC_TO_PETS = "toxic_to_pets"
    TOXIC_TO_HORSES = "toxic_to_horses"
    EDIBLE = "edible"
    UNKNOWN = "unknown"


PET_SAFETY_TAGS = frozenset({ToxicityTag.PET_SAFE, ToxicityTag.TOXIC_TO_PETS})
VALID_TOXICITY_TAGS = frozenset(ToxicityTag)
PET_SAFETY_DISCLAIMER = (
    "Pet-safety flags are informational only, not veterinary advice. "
    "Confirm a plant's identity and safety with a veterinarian or trusted toxicology source."
)


def normalize_toxicity(value: object, *, care_note: object = None) -> list[str]:
    """Return canonical tags, deriving pet safety conservatively from legacy text.

    Existing canonical tags take precedence. Free text is marked pet-safe only when it
    explicitly mentions pets, cats, or dogs together with a non-toxic/safe claim. Any
    remaining toxic claim wins over a safe claim. Ambiguous records become ``unknown``.
    """

    if isinstance(value, (list, tuple, set)):
        raw_values = list(value)
    elif value is None:
        raw_values = []
    else:
        raw_values = [value]

    tags: list[ToxicityTag] = []
    notes: list[str] = []
    for raw in raw_values:
        text = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
        try:
            tag = ToxicityTag(text)
        except ValueError:
            notes.append(str(raw))
        else:
            if tag not in tags:
                tags.append(tag)

    if care_note:
        notes.append(str(care_note))

    if ToxicityTag.TOXIC_TO_PETS in tags:
        tags = [
            tag for tag in tags if tag not in PET_SAFETY_TAGS and tag is not ToxicityTag.UNKNOWN
        ]
        tags.insert(0, ToxicityTag.TOXIC_TO_PETS)
    elif ToxicityTag.PET_SAFE in tags:
        tags = [tag for tag in tags if tag is not ToxicityTag.UNKNOWN]
    else:
        note = " ".join(notes).casefold()
        without_non_toxic = re.sub(r"\bnon[- ]toxic\b", "", note)
        mentions_pet = bool(re.search(r"\b(pets?|cats?|dogs?)\b", note))
        claims_toxicity = "toxic" in without_non_toxic
        claims_pet_safety = mentions_pet and (
            bool(re.search(r"\bnon[- ]toxic\b", note))
            or bool(re.search(r"\bsafe\b.{0,40}\b(pets?|cats?|dogs?)\b", note))
        )

        if claims_toxicity:
            tags.insert(0, ToxicityTag.TOXIC_TO_PETS)
        elif claims_pet_safety:
            tags.insert(0, ToxicityTag.PET_SAFE)
        else:
            tags.insert(0, ToxicityTag.UNKNOWN)

    return [tag.value for tag in tags]
