"""Tests for toxicity filter."""

import json
from pathlib import Path
from plantguide.toxicity_filter import filter_by_toxicity

def test_filter_pet_safe(tmp_path):
    species = [
        {"common_name": "Safe Plant", "care": {"toxicity": "Non-toxic"}},
        {"common_name": "Toxic Plant", "care": {"toxicity": "Toxic to cats"}}
    ]
    for i, s in enumerate(species):
        (tmp_path / f'species_{i}.json').write_text(json.dumps(s))
    
    result = filter_by_toxicity(tmp_path, pet_safe=True)
    assert len(result) == 1
    assert result[0]['common_name'] == 'Safe Plant'
