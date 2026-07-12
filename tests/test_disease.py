from plantguide.identify.disease import match_diseases
from plantguide.care.export_svg import care_card_svg


def test_disease_matcher_finds_rot() -> None:
    r = match_diseases("rot,yellow", top_k=5)
    assert r["matches"]
    assert r["model"] == "DiseaseTagMatcher"


def test_care_svg_snake() -> None:
    svg = care_card_svg("snake_plant")
    assert "svg" in svg
    assert "Snake" in svg or "snake" in svg.lower()
