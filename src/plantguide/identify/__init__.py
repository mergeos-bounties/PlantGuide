"""Plant identification: photo, tags, sample JSON, and disease matching."""
from plantguide.identify.vision import (
    extract_all_visual_tags,
    extract_edge_tags,
    extract_visual_tags,
    identify_from_image,
    photo_care_demo,
)
from plantguide.identify.pipeline import identify_from_sample, identify_from_tags
from plantguide.identify.disease import match_diseases

__all__ = [
    "identify_from_image",
    "identify_from_tags",
    "identify_from_sample",
    "extract_visual_tags",
    "extract_edge_tags",
    "extract_all_visual_tags",
    "photo_care_demo",
    "match_diseases",
]
