"""Generate the Research page picture for "Value, attention and bias in choice".

A lattice of identical circles seen through a lens that is focused off-centre: near the focus the circles swell, turn
yellow and push their neighbours apart; farther away they shrink, turn green and fade. Everything underneath is the same,
but not the same as perceived. Deterministic; pure Pillow.

    .venv/bin/python scripts/make_value_attention_bias_image.py [output.png]     # default: content/images/value-attention-bias.png
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3
SPACING = 62  # distance between neighbouring circles before the lens is applied
FOCUS = (0.62 * W, 0.46 * H)
REACH = 300  # how far the lens reaches
PUSH = 1.1  # how strongly the lens pushes circles apart near the focus
STOPS = [(0.0, (0, 105, 62)), (0.5, (127, 168, 58)), (1.0, (242, 184, 0))]  # green, yellow-green, yellow
FADE = 90  # circles shrink away over this many pixels near the picture's edge


def colour(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def smoothstep(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def draw(path):
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    d = ImageDraw.Draw(big)
    fx, fy = FOCUS
    dots = []
    rows = int(H / (SPACING * 0.866)) + 6
    cols = int(W / SPACING) + 6
    for j in range(-3, rows - 3):
        for i in range(-3, cols - 3):
            x, y = (i + 0.5 * (j % 2)) * SPACING, j * SPACING * 0.866  # a hexagonal lattice
            dx, dy = x - fx, y - fy
            dist = math.hypot(dx, dy)
            near = math.exp(-((dist / REACH) ** 2))  # 1 at the focus, fading to 0 far away
            push = 1 + PUSH * near  # the lens spreads the lattice out around the focus
            px, py = fx + dx * push, fy + dy * push
            edge = min(px, W - px, py, H - py)
            if edge <= 0:
                continue
            radius = SPACING * (0.12 + 0.50 * near) * smoothstep(edge / FADE) * 1.0
            dots.append((near, px, py, radius))
    for near, px, py, r in sorted(dots):  # big ones last, so they sit on top
        c = colour(near)
        r *= SCALE
        d.ellipse((px * SCALE - r, py * SCALE - r, px * SCALE + r, py * SCALE + r), fill=c)
    path.parent.mkdir(parents=True, exist_ok=True)
    big.resize((W, H), Image.LANCZOS).save(path)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "content" / "images" / "value-attention-bias.png")
