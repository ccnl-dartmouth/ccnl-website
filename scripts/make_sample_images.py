"""Generate the placeholder images used by tests/fixture_lab/. Run once; the output is committed.

    .venv/bin/python scripts/make_sample_images.py

Portraits are neutral silhouettes and figures are made-up plots, so nothing here looks like a real person or result.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixture_lab"
INK, GREEN, BLUE, ORANGE, GRAY = (28, 28, 28), (0, 105, 62), (46, 100, 170), (214, 130, 40), (120, 120, 120)


def save(im, path, **kw):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=82, **kw)


def portrait(path, bg, skin):
    """Neutral head-and-shoulders silhouette on a colored background."""
    size = 900
    im = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(im)
    d.ellipse((size * 0.12, size * 0.62, size * 0.88, size * 1.35), fill=skin)  # shoulders
    d.ellipse((size * 0.32, size * 0.18, size * 0.68, size * 0.62), fill=skin)  # head
    save(im, path)


def figure(path, kind, seed, size=(1600, 900)):
    """A made-up plot: scatter, lines, bars, heatmap, or raster."""
    rnd = random.Random(seed)
    w, h = size
    im = Image.new("RGB", size, (250, 250, 247))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = w * 0.1, h * 0.1, w * 0.94, h * 0.84
    d.line((x0, y0, x0, y1, x1, y1), fill=INK, width=max(2, w // 400))
    pts = lambda n: [(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * (0.2 + 0.6 * rnd.random())) for i in range(n)]
    if kind == "scatter":
        for _ in range(140):
            x, y = rnd.uniform(x0 + 20, x1 - 20), rnd.uniform(y0 + 20, y1 - 20)
            r = w // 130
            d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice((GREEN, BLUE, ORANGE)))
        d.line((x0 + 10, y1 - 10, x1 - 10, y0 + 10), fill=INK, width=w // 300)
    elif kind == "lines":
        for color in (GREEN, BLUE, ORANGE):
            p = pts(9)
            d.line(p, fill=color, width=w // 170, joint="curve")
    elif kind == "bars":
        n, gap = 8, (x1 - x0) / 8
        for i in range(n):
            top = y1 - (y1 - y0) * rnd.uniform(0.25, 0.9)
            d.rectangle((x0 + gap * i + gap * 0.18, top, x0 + gap * (i + 1) - gap * 0.18, y1 - 3), fill=(GREEN, BLUE)[i % 2])
    elif kind == "heat":
        cols, rows = 16, 9
        cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
        for i in range(cols):
            for j in range(rows):
                v = (rnd.random() * 0.6 + 0.4 * (1 - abs(i - cols / 2) / (cols / 2)))
                c = tuple(int(255 - v * (255 - g)) for g in GREEN)
                d.rectangle((x0 + cw * i + 2, y0 + ch * j + 2, x0 + cw * (i + 1) - 2, y0 + ch * (j + 1) - 2), fill=c)
    else:  # raster
        for row in range(14):
            y = y0 + (y1 - y0) * (row + 0.5) / 14
            for _ in range(rnd.randint(14, 40)):
                x = rnd.uniform(x0 + 6, x1 - 6)
                d.line((x, y - h * 0.018, x, y + h * 0.018), fill=(BLUE, GREEN)[row % 2], width=max(2, w // 500))
    save(im, path)


def logo(path, color, text):
    im = Image.new("RGB", (300, 120), color)
    d = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=40)
    box = d.textbbox((0, 0), text, font=font)
    d.text(((300 - box[2]) / 2, (120 - box[3]) / 2), text, fill="white", font=font)
    save(im, path)


if __name__ == "__main__":
    tones = [((0, 105, 62), (222, 190, 160)), ((70, 90, 160), (150, 105, 80)), ((160, 90, 70), (235, 205, 180)),
             ((110, 70, 150), (190, 140, 110)), ((30, 120, 120), (110, 75, 55)), ((150, 110, 30), (240, 215, 190)),
             ((90, 100, 110), (200, 160, 130))]
    for (slug, (bg, skin)) in zip(("pat-investigator", "alex-postdoc", "sam-student", "robin-student", "casey-student", "morgan-student", "devon-undergrad"), tones):
        portrait(ROOT / "images" / f"{slug}.jpg", bg, skin)

    for i, (slug, kind) in enumerate((("learning", "lines"), ("choice", "scatter"), ("models", "raster"), ("behavior", "bars"))):
        figure(ROOT / "images" / f"{slug}.jpg", kind, 10 + i)

    for i, (name, kind) in enumerate((("2024-student-context", "bars"), ("2021-alumna-models", "raster"), ("2026-casey-exploration", "scatter"), ("2025-jordan-adaptation", "lines"), ("2022-sam-risk", "heat"))):
        figure(ROOT / "images" / f"{name}.jpg", kind, 40 + i, size=(800, 600))

    logo(ROOT / "images" / "funder-one.png", (30, 60, 120), "FUNDER")
    logo(ROOT / "images" / "funder-two.png", (120, 60, 30), "GRANT")
    print("sample images written to", ROOT)
