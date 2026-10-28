"""Generate the Research page picture for "Learning in complex environments".

A 5 x 5 grid of objects built from three features, each changing in steps across the picture: colour changes down the
rows (blue, green, yellow), shape changes along the columns (triangle, square, hexagon, 12-sided, circle), and the stripe
pattern grows along the diagonal, from solid at the top left to bold stripes at the bottom right, turning from horizontal to vertical on the way. Every combination of
colour and shape is shown, so the options multiply quickly. Deterministic; pure Pillow.

    .venv/bin/python scripts/make_complex_environments_image.py [output.png]     # default: content/images/complex-environments.png
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3
N = 5  # the grid is N x N
SIDES = [3, 4, 6, 12, 0]  # 0 means a circle
STOPS = [(0.0, (26, 95, 180)), (0.5, (0, 105, 62)), (1.0, (242, 184, 0))]  # blue, Dartmouth green, yellow


def colour(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def outline(cx, cy, radius, sides):
    """A regular polygon with a flat bottom (a triangle points up), or a circle. Corners of few-sided shapes are pulled out a little so all shapes look about equally big."""
    if sides == 0:
        return [(cx + radius * math.cos(a / 90 * math.pi), cy + radius * math.sin(a / 90 * math.pi)) for a in range(180)]
    equal_area = math.sqrt(2 * math.pi / (sides * math.sin(2 * math.pi / sides)))
    r = radius * equal_area ** 0.6
    turn = math.pi / sides if sides % 2 == 0 else 0  # even-sided shapes are turned half a step so they sit flat
    return [(cx + r * math.sin(2 * math.pi * i / sides + turn), cy - r * math.cos(2 * math.pi * i / sides + turn)) for i in range(sides)]


def draw(path):
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    cell = H * 0.18 * SCALE
    x0, y0 = (W * SCALE - cell * N) / 2, (H * SCALE - cell * N) / 2
    radius = cell * 0.36
    for row in range(N):
        for col in range(N):
            cx, cy = x0 + (col + 0.5) * cell, y0 + (row + 0.5) * cell
            mask = Image.new("L", big.size, 0)
            ImageDraw.Draw(mask).polygon(outline(cx, cy, radius, SIDES[col]), fill=255)
            fill = colour(row / (N - 1))
            pale = tuple(round(c + (255 - c) * 0.55) for c in fill)  # stripes are a pale tint of the colour, so every outline stays whole
            layer = Image.new("RGB", big.size, fill)
            stripe = (row + col) / (2 * (N - 1))  # 0 = solid, 1 = boldest stripes
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
