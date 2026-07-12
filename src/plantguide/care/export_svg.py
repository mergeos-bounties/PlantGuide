"""Export a simple SVG care card for a species."""

from __future__ import annotations

from html import escape
from pathlib import Path

from plantguide.care.cards import care_card_for_species


def care_card_svg(species_id: str) -> str:
    card = care_card_for_species(species_id)
    title = escape(str(card.get("common_name") or species_id))
    sci = escape(str(card.get("scientific_name") or ""))
    summary = escape(str(card.get("summary") or ""))
    rows = [
        ("Light", card.get("light")),
        ("Water", card.get("water")),
        ("Soil", card.get("soil")),
        ("Humidity", card.get("humidity")),
        ("Temp °C", card.get("temperature_c")),
    ]
    y = 110
    body = ""
    for label, val in rows:
        body += (
            f'<text x="28" y="{y}" font-size="14" fill="#64748b">{escape(str(label))}</text>'
            f'<text x="120" y="{y}" font-size="14" fill="#0f172a">{escape(str(val or "—"))}</text>'
        )
        y += 28
    tips = card.get("tips") or []
    tip = escape(str(tips[0])) if tips else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420" height="320" viewBox="0 0 420 320">
  <rect width="420" height="320" rx="18" fill="#f8fafc"/>
  <rect x="0" y="0" width="420" height="72" rx="18" fill="#16a34a"/>
  <rect x="0" y="40" width="420" height="32" fill="#16a34a"/>
  <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="22" font-weight="700" fill="#fff">{title}</text>
  <text x="24" y="60" font-family="Segoe UI, sans-serif" font-size="12" fill="#dcfce7">{sci}</text>
  <text x="24" y="96" font-family="Segoe UI, sans-serif" font-size="13" fill="#334155">{summary[:90]}</text>
  {body}
  <text x="28" y="290" font-family="Segoe UI, sans-serif" font-size="12" fill="#15803d">Tip: {tip[:70]}</text>
  <text x="300" y="310" font-size="10" fill="#94a3b8">PlantGuide</text>
</svg>
"""


def write_care_svg(species_id: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(care_card_svg(species_id), encoding="utf-8")
    return out_path
