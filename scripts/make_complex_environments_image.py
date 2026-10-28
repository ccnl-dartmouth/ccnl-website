"""Generate the Research page picture for "Learning in complex environments".

A grid of objects built from three features, each changing in steps across the picture: colour changes down the rows
(blue, green, yellow), shape changes along the columns (triangle, square, hexagon, star, plus, half-disc, circle), and
the stripe pattern grows along the diagonal, turning from horizontal to vertical and getting bolder, from solid at the
top left to boldest stripes at the bottom right. Every combination of colour and shape is shown, so the options multiply
quickly. Deterministic; pure Pillow.

    .venv/bin/python scripts/make_complex_environments_image.py [output.png]     # default: content/images/complex-environments.png
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3
ROWS = 5  # colours
SHAPES = ["triangle", "square", "hexagon", "star", "plus", "half-disc", "circle"]  # one column each
COLS = len(SHAPES)
STOPS = [(0.0, (26, 95, 180)), (0.5, (0, 105, 62)), (1.0, (242, 184, 0))]  # blue, Dartmouth green, yellow


def colour(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def regular(sides, turn=0.0):
    return [(math.sin(2 * math.pi * i / sides + turn), -math.cos(2 * math.pi * i / sides + turn)) for i in range(sides)]


def shape_points(name):
    """A shape as points around (0, 0), roughly 1 unit across, with its visual centre at the origin."""
    if name == "triangle":
        return regular(3)
    if name == "square":
        return regular(4, math.pi / 4)
    if name == "hexagon":
        return regular(6, math.pi / 6)
    if name == "star":
        return [((1 if i % 2 == 0 else 0.45) * math.sin(math.pi * i / 5), -(1 if i % 2 == 0 else 0.45) * math.cos(math.pi * i / 5)) for i in range(10)]
    if name == "plus":
        a, b = 1.0, 0.36  # arm length and half-width
        return [(b, -a), (b, -b), (a, -b), (a, b), (b, b), (b, a), (-b, a), (-b, b), (-a, b), (-a, -b), (-b, -b), (-b, -a)]
    if name == "half-disc":
        top = [(math.cos(a / 40 * math.pi), -math.sin(a / 40 * math.pi)) for a in range(41)]
        return [(x, y + 0.424) for x, y in top]  # the flat side sits below the centre, so the shape looks centred
    return [(math.cos(a / 90 * math.pi), math.sin(a / 90 * math.pi)) for a in range(180)]  # circle


def outline(cx, cy, radius, name):
    """The shape's corners in the picture, scaled so every shape covers about the same area (but pulled only part of the way, to keep them from crowding)."""
    pts = shape_points(name)
    area = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2
    s = radius * (math.pi / area) ** 0.35
    return [(cx + x * s, cy + y * s) for x, y in pts]


def draw(path):
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    cell = H * 0.18 * SCALE
    x0, y0 = (W * SCALE - cell * COLS) / 2, (H * SCALE - cell * ROWS) / 2
    radius = cell * 0.36
    for row in range(ROWS):
        for col in range(COLS):
            cx, cy = x0 + (col + 0.5) * cell, y0 + (row + 0.5) * cell
            mask = Image.new("L", big.size, 0)
            ImageDraw.Draw(mask).polygon(outline(cx, cy, radius, SHAPES[col]), fill=255)
            fill = colour(row / (ROWS - 1))
            pale = tuple(round(c + (255 - c) * 0.55) for c in fill)  # stripes are a pale tint of the colour, so every outline stays whole
            layer = Image.new("RGB", big.size, fill)
            stripe = (row + col) / (ROWS + COLS - 2)  # 0 = solid, 1 = boldest stripes
            if stripe:
                sd, thick = ImageDraw.Draw(layer), radius * 0.26 * stripe
                angle = math.pi / 2 * stripe  # the stripes turn from horizontal (just after the solid corner) through diagonal to vertical
                dx, dy = math.cos(angle), -math.sin(angle)  # along a stripe
                nx, ny = -dy, dx  # across the stripes
                for k in range(-6, 7):
                    off = k * radius * 0.44
                    px, py = cx + nx * off, cy + ny * off
                    sd.line((px - 2 * radius * dx, py - 2 * radius * dy, px + 2 * radius * dx, py + 2 * radius * dy), fill=pale, width=max(1, round(thick)))
            big.paste(layer, (0, 0), mask)
    path.parent.mkdir(parents=True, exist_ok=True)
    big.resize((W, H), Image.LANCZOS).save(path)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "content" / "images" / "complex-environments.png")
