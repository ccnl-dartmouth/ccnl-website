"""Generate the Research page picture for "Learning under uncertainty and change".

Many thin, wobbling lines follow nearly the same path (uncertainty: many possible versions of the same world), then the
whole bundle jumps to a new level (change). Each line fades from green to yellow, left to right. Deterministic (fixed
seed), so rerunning gives the same picture. Pure Pillow, no other libraries.

    .venv/bin/python scripts/make_uncertainty_and_change_image.py [output.png]     # default: content/images/uncertainty-and-change.png
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3  # drawn 3x larger, then shrunk, for smooth edges
LINES, STEPS = 26, 900
BEFORE, AFTER = 0.68, 0.32  # the bundle's height (fraction of the picture) before and after the change
CHANGE_AT = 0.55
STOPS = [(0.0, (0, 105, 62)), (0.5, (127, 168, 58)), (1.0, (242, 184, 0))]  # Dartmouth green, yellow-green, yellow


def colour(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def smoothstep(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def wobble(rng):
    """A smooth random wiggle made of a few sine waves."""
    waves = [(rng.uniform(1.5, 7) * math.pi, rng.uniform(0, 2 * math.pi), rng.uniform(0.3, 1)) for _ in range(5)]
    return lambda x: sum(a * math.sin(f * x + p) for f, p, a in waves) / 3


def draw(path):
    rng = random.Random(11)
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    left, right = 0.05, 0.95
    for _ in range(LINES):
        wiggle = wobble(rng)
        at = CHANGE_AT + rng.uniform(-0.035, 0.035)  # each line jumps at a slightly different moment
        drop = rng.uniform(0.85, 1.15)
        rng_amp = rng.uniform(0.07, 0.13)  # how far this line wanders
        width = rng.uniform(3.5, 6) * SCALE
        layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        pts = []
        for i in range(STEPS + 1):
            t = i / STEPS
            level = BEFORE + (AFTER - BEFORE) * drop * smoothstep((t - at) / 0.07)
            pts.append(((left + (right - left) * t) * W * SCALE, (level + rng_amp * wiggle(t)) * H * SCALE, colour(t)))
        for (x0, y0, c), (x1, y1, _) in zip(pts, pts[1:]):
            d.line((x0, y0, x1, y1), fill=c + (190,), width=round(width))
            r = width / 2
            d.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=c + (190,))
        big.paste(layer, (0, 0), layer)
    path.parent.mkdir(parents=True, exist_ok=True)
    big.resize((W, H), Image.LANCZOS).save(path)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "content" / "images" / "uncertainty-and-change.png")
