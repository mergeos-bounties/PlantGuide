#!/usr/bin/env python3
"""Generate web/data.js from species JSON files."""
import json, glob, os

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
species_dir = os.path.join(script_dir, 'data', 'species')
web_dir = os.path.join(script_dir, 'web')

species = []
for f in sorted(glob.glob(os.path.join(species_dir, '*.json'))):
    with open(f) as fh:
        species.append(json.load(fh))

all_tags = set()
for s in species:
    for t in s.get('tags', []):
        all_tags.add(t.lower())

tag_categories = {
    'Light': ['low light', 'low light tolerant', 'low-light', 'bright indirect', 'indirect light', 'bright light', 'full sun', 'full sun tolerant', 'shade', 'shade-tolerant', 'high light', 'bright-indirect'],
    'Water': ['drought tolerant', 'drought', 'drought-tolerant', 'moist', 'moist soil', 'low water', 'arid', 'xeric', 'xerophyte', 'succulent', 'cactus'],
    'Indoor/Outdoor': ['indoor', 'outdoor', 'houseplant', 'bedroom', 'bathroom', 'office', 'kitchen', 'windowsill', 'terrarium', 'container plant'],
    'Style': ['trailing', 'hanging', 'climbing', 'vine', 'vining', 'bushy', 'compact', 'upright', 'tall', 'tree', 'tree-like', 'tree-form', 'rosette', 'groundcover', 'architectural'],
    'Care Level': ['easy', 'easy care', 'beginner', 'beginner friendly', 'beginner-friendly', 'hardy', 'indestructible', 'low_maintenance', 'dramatic', 'delicate', 'exotic'],
    'Type': ['tropical', 'succulent', 'fern', 'cactus', 'herb', 'edible', 'fruit', 'fruiting', 'flowering', 'aroid', 'bromeliad', 'epiphyte', 'prayer plant', 'foliage'],
    'Features': ['variegated', 'colorful', 'fragrant', 'fragrant flowers', 'air purifying', 'air-purifying', 'air purifier', 'pet-friendly', 'pet-safe', 'pet-safe-ish', 'pet-safer', 'medicinal', 'aromatic', 'statement'],
    'Leaf': ['large leaves', 'heart-shaped', 'heart shaped leaves', 'heart shaped leaf', 'small leaves', 'glossy', 'glossy leaves', 'pointed leaves', 'sword-shaped leaves', 'round leaves', 'patterned', 'patterned leaves', 'fenestrated', 'fenestrated leaves']
}

js = 'const PLANTGUIDE_DATA = ' + json.dumps({'species': species, 'tag_categories': tag_categories, 'all_tags': sorted(all_tags)}, indent=2) + ';'
with open(os.path.join(web_dir, 'data.js'), 'w') as f:
    f.write(js)

print(f'✅ Generated web/data.js with {len(species)} species and {len(all_tags)} tags')