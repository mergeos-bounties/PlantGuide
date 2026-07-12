from __future__ import annotations

from pathlib import Path

from plantguide.care.cards import care_card_for_species
from plantguide.identify.pipeline import identify_from_sample, identify_from_tags


def assess_for_app(tags: str | list[str], *, top_k: int = 3) -> dict:
    """Stable JSON contract for plant-care apps."""
    payload = identify_from_tags(tags, top_k=top_k, with_care=True)
    payload["integration_version"] = "plantguide.sdk.v1"
    payload["ready_for_ui"] = True
    return payload


def care_for_app(species_id: str) -> dict:
    card = care_card_for_species(species_id)
    card["integration_version"] = "plantguide.sdk.v1"
    return card


def care_report_from_sample(sample: Path, *, top_k: int = 3) -> dict:
    """Build the app demo care-report contract from a bundled observation sample."""
    result = identify_from_sample(sample, top_k=top_k)
    # Portable path form for JSON contracts (Windows must not emit backslashes).
    source = Path(sample).as_posix()
    return _care_report(
        result,
        evidence_source=source,
        evidence_source_type="sample_fixture",
    )


def care_report_from_tags(tags: str | list[str], *, top_k: int = 3) -> dict:
    """Build the app demo care-report contract from inline app tags."""
    result = identify_from_tags(tags, top_k=top_k, with_care=True)
    return _care_report(
        result,
        evidence_source="inline_tags",
        evidence_source_type="inline_tags",
    )


def _care_report(result: dict, *, evidence_source: str, evidence_source_type: str) -> dict:
    matches = list(result.get("matches") or [])
    top_match = matches[0] if matches else None
    care_card = result.get("top_care")
    top_species_id = top_match.get("species_id") if top_match else None

    return {
        "report_type": "plantguide.app.care_report.v1",
        "integration_version": "plantguide.sdk.v1",
        "ready_for_ui": bool(top_species_id and care_card),
        "sample_id": result.get("sample_id"),
        "source": result.get("source"),
        "query_tags": result.get("query_tags") or [],
        "expected_species": result.get("expected_species"),
        "hit_top1": result.get("hit_top1"),
        "top_species_id": top_species_id,
        "top_match": top_match,
        "matches": matches,
        "care_card": care_card,
        "license_safe_evidence": {
            "source": evidence_source,
            "source_type": evidence_source_type,
            "external_assets": [],
        },
    }
