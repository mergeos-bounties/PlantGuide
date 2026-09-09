"""Pydantic schema validation for species and sample JSON files."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class CareCard(BaseModel):
    """Required care fields for a species."""

    summary: str = Field(..., min_length=5)
    light: str = Field(..., min_length=3)
    water: str = Field(..., min_length=3)
    soil: str = Field(..., min_length=3)
    humidity: str = Field(..., min_length=1)
    temperature_c: str | dict | int | float = Field(...)
    fertilizer: str = Field(..., min_length=3)
    toxicity: str | list[str] | None = Field(default=None)
    common_issues: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)

    @field_validator("common_issues", "tips", mode="before")
    @classmethod
    def must_be_list(cls, v: Any) -> list:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        raise ValueError("must be a list or null")

    model_config = {"extra": "allow"}


class SpeciesRecord(BaseModel):
    """Schema for a species JSON file in data/species/."""

    id: str = Field(..., min_length=1, pattern=r"^[a-z0-9_]+$")
    common_name: str = Field(..., min_length=1)
    scientific_name: str | None = None
    tags: list[str] = Field(..., min_length=1)
    care: CareCard

    @field_validator("tags", mode="before")
    @classmethod
    def tags_nonempty_strings(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
        cleaned = [str(t).strip() for t in v if str(t).strip()]
        if not cleaned:
            raise ValueError("tags must contain at least one non-empty string")
        return cleaned

    @model_validator(mode="after")
    def tags_minimum_five(self) -> "SpeciesRecord":
        if len(self.tags) < 5:
            raise ValueError(f"species must have at least 5 tags, got {len(self.tags)}")
        return self

    model_config = {"extra": "allow"}


class SampleRecord(BaseModel):
    """Schema for observation sample JSON files in data/samples/."""

    id: str | None = None
    tags: list[str] = Field(..., min_length=1)
    expected_species: str | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def tags_nonempty_strings(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
        cleaned = [str(t).strip() for t in v if str(t).strip()]
        if not cleaned:
            raise ValueError("tags must contain at least one non-empty string")
        return cleaned

    model_config = {"extra": "allow"}


def validate_species(data: dict) -> SpeciesRecord:
    """Validate a species dict and return a SpeciesRecord, raising ValidationError on failure."""
    return SpeciesRecord.model_validate(data)


def validate_sample(data: dict) -> SampleRecord:
    """Validate a sample dict and return a SampleRecord, raising ValidationError on failure."""
    return SampleRecord.model_validate(data)
