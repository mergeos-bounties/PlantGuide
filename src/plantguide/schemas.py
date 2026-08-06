"""Pydantic schemas for PlantGuide species and observation samples.

Provides runtime validation and clear error messages for malformed catalog
or sample JSON files.
"""

from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class CareInfo(BaseModel):
    """Per-species care guidance."""

    summary: str = Field(default="", description="One-line care overview")
    light: str = Field(default="", description="Light requirement guidance")
    water: str = Field(default="", description="Watering frequency guidance")
    soil: str = Field(default="", description="Recommended soil / potting mix")
    humidity: str = Field(default="", description="Preferred humidity level")
    temperature_c: str = Field(default="", description="Temperature range (Celsius), e.g. '15-30'")
    fertilizer: str = Field(default="", description="Fertilizer schedule / strength")
    toxicity: str = Field(default="", description="Toxicity note (pets / humans)")
    common_issues: list[str] = Field(default_factory=list, description="Known pests / diseases")
    tips: list[str] = Field(default_factory=list, description="Care tips for owners")

    @field_validator("temperature_c", mode="before")
    @classmethod
    def _coerce_temp(cls, v: Any) -> str:
        """Accept dict (min/max/ideal) or string; convert dict to range string."""
        if isinstance(v, dict):
            # e.g. {"min": 15, "ideal_min": 18, "ideal_max": 26, "max": 30}
            parts = []
            if "min" in v:
                parts.append(str(v["min"]))
            if "ideal_min" in v and "ideal_max" in v:
                parts.append(f"{v['ideal_min']}-{v['ideal_max']}")
            elif "ideal" in v:
                parts.append(str(v["ideal"]))
            if "max" in v:
                parts.append(str(v["max"]))
            return "/".join(parts) if parts else json.dumps(v)
        return str(v) if v is not None else ""

    @field_validator("toxicity", mode="before")
    @classmethod
    def _coerce_toxicity(cls, v: Any) -> str:
        """Accept string or list; convert list to comma-joined string."""
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        return str(v) if v is not None else ""


class Species(BaseModel):
    """Validated species catalog entry."""

    id: str = Field(..., min_length=1, description="Unique slug, e.g. snake_plant")
    common_name: str = Field(default="", description="Human-readable name")
    scientific_name: str = Field(default="", description="Latin binomial")
    tags: list[str] = Field(default_factory=list, description="Trait / morphology tags")
    care: CareInfo = Field(default_factory=CareInfo, description="Care guidance")
    toxicity: list[str] = Field(default_factory=list, description="Toxicity flags (pet_safe, toxic_to_pets)")

    @field_validator("id")
    @classmethod
    def _id_must_be_slug(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("species id must not be empty")
        return v.strip().lower().replace(" ", "_")

    @field_validator("toxicity", mode="before")
    @classmethod
    def _coerce_toxicity_list(cls, v: Any) -> list[str]:
        """Accept string like 'Non-toxic' or 'Non-toxic to pets', convert to list of flags."""
        if isinstance(v, list):
            return [str(x) for x in v]
        s = str(v).strip() if v else ""
        if not s:
            return []
        slow = s.lower()
        flags: list[str] = []
        if "non-toxic" in slow or "nontoxic" in slow:
            flags.append("pet_safe")
        if "toxic" in slow and "non-toxic" not in slow and "nontoxic" not in slow:
            flags.append("toxic_to_pets")
        # If we can't classify, keep the original as a single flag
        if not flags:
            flags = [s]
        return flags


class ObservationSample(BaseModel):
    """Validated observation / sample JSON entry."""

    id: str = Field(default="", description="Unique sample slug, e.g. obs_monstera")
    tags: list[str] = Field(default_factory=list, description="Observed trait tags")
    expected_species: str | None = Field(default=None, description="Ground-truth species id (optional)")

    @field_validator("id")
    @classmethod
    def _id_must_be_slug(cls, v: str) -> str:
        if not v:
            return v  # optional — allow empty for legacy fixtures
        return v.strip().lower().replace(" ", "_")

    @model_validator(mode="after")
    def _ensure_id_from_tags(self) -> "ObservationSample":
        """If id is empty but sample has tags, it's still valid (legacy fixtures)."""
        return self


def validate_species(data: dict[str, Any]) -> Species:
    """Validate a species dict; raises ValidationError with clear messages."""
    return Species.model_validate(data)


def validate_sample(data: dict[str, Any]) -> ObservationSample:
    """Validate a sample dict; raises ValidationError with clear messages."""
    return ObservationSample.model_validate(data)
