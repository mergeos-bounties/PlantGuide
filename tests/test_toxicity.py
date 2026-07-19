"""Tests for toxicity and pet-safety features (PlantGuide#20)."""
from __future__ import annotations

import pytest

from plantguide.data.loader import (
    _set_safety_defaults,
    get_species_by_id,
    load_species,
    load_species_catalog,
)


class TestSafetyDefaults:
    """Test _set_safety_defaults helper."""

    def test_pet_safe_true(self) -> None:
        care = {"toxicity": "Non-toxic to pets"}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is True

    def test_pet_safe_true_generally(self) -> None:
        care = {"toxicity": "Generally considered non-toxic to pets"}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is True

    def test_pet_safe_false_toxic(self) -> None:
        care = {"toxicity": "Toxic if ingested"}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is False

    def test_pet_safe_false_mildly_toxic(self) -> None:
        care = {"toxicity": "Mildly toxic to pets"}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is False

    def test_pet_safe_none_unknown(self) -> None:
        care = {"toxicity": "Unknown"}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is None

    def test_pet_safe_none_empty(self) -> None:
        care = {}
        _set_safety_defaults(care)
        assert care["is_pet_safe"] is None
        assert care["toxicity"] == "Unknown"

    def test_pet_safe_none_culinary(self) -> None:
        care = {"toxicity": "Culinary herb; generally safe when used as food"}
        _set_safety_defaults(care)
        # "generally safe" should trigger True
        assert care["is_pet_safe"] is True

    def test_pet_safe_none_edible(self) -> None:
        care = {"toxicity": "Edible for humans; not a pet food"}
        _set_safety_defaults(care)
        # "not a pet food" is a safe keyword
        assert care["is_pet_safe"] is True


class TestSpeciesLoader:
    """Test that species JSON files have is_pet_safe populated."""

    def test_all_species_have_safety(self) -> None:
        catalog = load_species_catalog()
        for sp in catalog:
            care = sp.get("care", {})
            assert "is_pet_safe" in care, f"{sp['id']} missing is_pet_safe"
            assert "toxicity" in care, f"{sp['id']} missing toxicity"

    def test_known_safe_species(self) -> None:
        # Boston Fern is known pet-safe
        sp = get_species_by_id("boston_fern")
        assert sp is not None
        assert sp["care"]["is_pet_safe"] is True

    def test_known_unsafe_species(self) -> None:
        # Snake Plant is known toxic
        sp = get_species_by_id("snake_plant")
        assert sp is not None
        assert sp["care"]["is_pet_safe"] is False


class TestCLIFilter:
    """Test CLI pet-safe filtering."""

    def test_pet_safe_filter_returns_only_safe(self, capsys: pytest.CaptureFixture[str]) -> None:
        from plantguide.cli import species_list

        species_list(pet_safe=True)
        out = capsys.readouterr().out
        # All listed species should be pet-safe
        assert "yes" in out
        # No unsafe should appear
        assert "[red]no[/red]" not in out

    def test_pet_unsafe_filter_returns_only_unsafe(self, capsys: pytest.CaptureFixture[str]) -> None:
        from plantguide.cli import species_list

        species_list(pet_safe=False)
        out = capsys.readouterr().out
        # All listed species should be unsafe
        assert "[red]no[/red]" in out
        # No safe should appear
        assert "[green]yes[/green]" not in out
