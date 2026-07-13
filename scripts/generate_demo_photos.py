"""Generate license-safe synthetic plant leaf photos for offline photo-ID demo.

Creates data/samples/photos/*.jpg + manifest.json
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "samples" / "photos"

# (filename, species_id, tags, palette, style)
SPECS = [
    (
        "monstera_demo.jpg",
        "monstera_deliciosa",
        ["tropical", "fenestrated leaves", "climbing", "indoor", "large leaves", "aroid"],
        [(34, 90, 48), (20, 60, 32), (12, 40, 22)],
        "fenestrated",
    ),
    (
        "snake_demo.jpg",
        "snake_plant",
        ["succulent", "upright", "thick leaves", "drought", "indoor", "low light"],
        [(30, 70, 45), (18, 40, 28), (200, 210, 180)],
        "upright",
    ),
    (
        "pothos_demo.jpg",
        "pothos_golden",
        # tags must overlap species catalog (Jaccard match)
        ["trailing", "variegated", "indoor", "vining", "heart shaped leaves", "easy"],
        [(50, 120, 40), (180, 190, 80), (30, 80, 30)],
        "trailing",
    ),
    (
        "aloe_demo.jpg",
        "aloe_vera",
        ["succulent", "thick leaves", "spiky", "drought", "medicinal gel"],
        [(90, 140, 70), (60, 100, 50), (200, 220, 160)],
        "rosette",
    ),
    (
        "peace_demo.jpg",
        "peace_lily",
        ["indoor", "white flowers", "dark green leaves", "shade tolerant", "humidity loving"],
        [(20, 50, 30), (15, 35, 22), (240, 240, 245)],
        "peace",
    ),
]


def _leaf(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, color: tuple, rot: float = 0.0) -> None:
    pts = []
    for i in range(14):
        t = i / 13 * math.pi
        rx = scale * (0.55 + 0.15 * math.sin(3 * t))
        ry = scale * 1.1
        x = rx * math.sin(t)
        y = -ry * math.cos(t)
        ca, sa = math.cos(rot), math.sin(rot)
        xr, yr = x * ca - y * sa, x * sa + y * ca
        pts.append((cx + xr, cy + yr))
    draw.polygon(pts, fill=color)


def render(style: str, palette: list[tuple[int, int, int]], seed: int = 0) -> Image.Image:
    rng = random.Random(seed)
    w, h = 640, 480
    img = Image.new("RGB", (w, h), (18, 22, 28))
    draw = ImageDraw.Draw(img)
    # soft bg
    for i in range(8):
        c = 22 + i * 4
        draw.ellipse((i * 20, i * 15, w - i * 20, h - i * 15), outline=(c, c + 4, c + 8))

    base = palette[0]
    dark = palette[1]
    accent = palette[2] if len(palette) > 2 else palette[0]

    if style == "fenestrated":
        for i, (dx, dy, sc, rot) in enumerate(
            [(-40, 20, 110, -0.4), (60, 10, 120, 0.35), (10, 60, 90, 0.1), (-80, 80, 70, -0.8)]
        ):
            _leaf(draw, w // 2 + dx, h // 2 + dy, sc, base if i % 2 == 0 else dark, rot)
        # holes
        for _ in range(12):
            x = w // 2 + rng.randint(-90, 90)
            y = h // 2 + rng.randint(-70, 70)
            r = rng.randint(8, 18)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(18, 22, 28))
    elif style == "upright":
        for i in range(7):
            x = w // 2 - 90 + i * 28
            draw.rounded_rectangle(
                (x, 80 + (i % 3) * 10, x + 22, 400),
                radius=10,
                fill=base if i % 2 == 0 else dark,
            )
            # yellow edge stripe
            draw.line((x + 4, 90, x + 4, 390), fill=accent, width=3)
    elif style == "trailing":
        for i in range(10):
            x = 80 + i * 50
            y = 120 + int(40 * math.sin(i / 2))
            _leaf(draw, x, y, 45, base if i % 2 == 0 else accent, rot=i * 0.3)
            if i < 9:
                draw.line((x, y, x + 50, 120 + int(40 * math.sin((i + 1) / 2))), fill=dark, width=3)
    elif style == "rosette":
        for i in range(12):
            ang = i / 12 * math.tau
            _leaf(
                draw,
                w // 2 + int(30 * math.cos(ang)),
                h // 2 + int(20 * math.sin(ang)),
                70,
                base if i % 2 == 0 else dark,
                rot=ang,
            )
    elif style == "peace":
        _leaf(draw, w // 2 - 40, h // 2 + 30, 100, dark, -0.3)
        _leaf(draw, w // 2 + 50, h // 2 + 40, 90, base, 0.4)
        # white spathe
        draw.ellipse((w // 2 + 20, 90, w // 2 + 100, 200), fill=accent)
        draw.rectangle((w // 2 + 52, 150, w // 2 + 68, 280), fill=(240, 235, 200))
    else:
        _leaf(draw, w // 2, h // 2, 100, base, 0)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    photos = []
    for i, (fname, species, tags, palette, style) in enumerate(SPECS):
        img = render(style, palette, seed=10 + i)
        path = OUT / fname
        img.save(path, quality=90)
        photos.append(
            {
                "file": fname,
                "expected_species": species,
                "tags": tags,
                "label": species.replace("_", " ").title(),
                "license": "synthetic-generated-offline",
            }
        )
        print("wrote", path, path.stat().st_size)
    man = {"version": 1, "photos": photos}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    print("manifest", len(photos), "photos")


if __name__ == "__main__":
    main()
