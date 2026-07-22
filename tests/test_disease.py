from plantguide.care.export_svg import care_card_svg
from plantguide.identify.disease import match_diseases


def test_disease_matcher_suggests_issue_and_remedies() -> None:
    result = match_diseases("yellow spots, sticky leaves", top_k=3)

    assert result["model"] == "DiseaseTagMatcher"
    assert result["matches"][0]["issue_id"] == "scale_insects"
    assert result["matches"][0]["matched_symptoms"] == ["yellow spots", "sticky leaves"]
    assert result["matches"][0]["remedies"]
    assert "Educational guidance only" in result["disclaimer"]


def test_disease_matcher_accepts_list_and_limits_results() -> None:
    result = match_diseases([" YELLOW   SPOTS ", "sticky leaves"], top_k=1)

    assert result["query"] == ["yellow spots", "sticky leaves"]
    assert len(result["matches"]) == 1


def test_disease_matcher_unknown_symptom_is_safe() -> None:
    result = match_diseases("silver triangles")

    assert result["matches"] == []
    assert "qualified horticulture professional" in result["disclaimer"]


def test_care_svg_snake() -> None:
    svg = care_card_svg("snake_plant")
    assert "svg" in svg
    assert "Snake" in svg or "snake" in svg.lower()
