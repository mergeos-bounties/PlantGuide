from __future__ import annotations

from plantguide.integrations.sdk import assess_for_app, care_for_app


def test_sdk_assess() -> None:
    result = assess_for_app("succulent,thick leaves,drought")
    assert result["integration_version"] == "plantguide.sdk.v1"
    assert result["ready_for_ui"] is True


def test_sdk_care() -> None:
    card = care_for_app("pothos_golden")
    assert card["species_id"] == "pothos_golden"
