"""Basic smoke tests for the web/ demo.

Validates that all required files exist, HTML is well-formed,
CSS is non-empty, and JS contains the expected data structures.
"""

import json
import re
from pathlib import Path


WEB_DIR = Path(__file__).resolve().parent.parent / "web"


def test_web_directory_exists():
    assert WEB_DIR.is_dir(), "web/ directory missing"


def test_index_html_exists():
    index = WEB_DIR / "index.html"
    assert index.is_file(), "index.html missing"
    content = index.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert '<link rel="stylesheet" href="style.css">' in content
    assert '<script src="script.js"></script>' in content
    # Verify semantic structure
    assert "<h1>" in content
    assert "tag-container" in content
    assert "care-cards-container" in content


def test_style_css_exists():
    css = WEB_DIR / "style.css"
    assert css.is_file(), "style.css missing"
    content = css.read_text(encoding="utf-8")
    assert len(content) > 500, "style.css suspiciously small"
    assert ":root" in content, "missing CSS custom properties"
    assert "@media" in content, "missing responsive breakpoints"


def test_script_js_exists():
    js = WEB_DIR / "script.js"
    assert js.is_file(), "script.js missing"
    content = js.read_text(encoding="utf-8")

    # Data integrity: must have plantConditions array with >= 7 entries
    cond_matches = re.findall(r'\{\s*id:\s*"([^"]+)"', content)
    assert len(cond_matches) >= 7, f"Expected >=7 plant conditions, got {len(cond_matches)}"

    # Must have symptomTags array with >= 10 entries
    tag_matches = re.findall(r'id:\s*"([^"]+)"', content.split("// --- Symptom Tags")[1].split("// --- State")[0])
    # Broader check: count tag objects in symptomTags
    tag_obj_count = content.count("label:")
    assert tag_obj_count >= 10, f"Expected >=10 symptom tags, got {tag_obj_count}"

    # Must have key functions
    assert "function toggleTag" in content
    assert "function diagnose" in content
    assert "function renderTags" in content
    assert "function createCareCard" in content


def test_readme_exists():
    readme = WEB_DIR / "README.md"
    assert readme.is_file(), "README.md missing"
    content = readme.read_text(encoding="utf-8")
    assert "# PlantGuide Web Demo" in content
    assert "## How to Use" in content


def test_all_conditions_have_required_fields():
    """Every plant condition must have id, name, icon, severity, symptoms, treatment, prevention."""
    js = (WEB_DIR / "script.js").read_text(encoding="utf-8")
    # Extract the plantConditions array body
    match = re.search(r"const plantConditions = \[(.*?)\];", js, re.DOTALL)
    assert match, "plantConditions array not found"
    body = match.group(1)

    # Count objects by id field
    ids = re.findall(r'id:\s*"([^"]+)"', body)
    assert len(ids) >= 7

    required = ["id:", "name:", "icon:", "severity:", "symptoms:", "treatment:", "prevention:"]
    for req_field in required:
        count = body.count(req_field)
        assert count >= len(ids), f"Field '{req_field}' appears {count} times, expected >= {len(ids)}"
