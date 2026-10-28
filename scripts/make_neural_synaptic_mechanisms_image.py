"""Generate the Research page picture for "Neural and synaptic mechanisms of learning".

A loose scatter of neurons, each a round cell body with branches. Branches from neighbouring neurons grow towards each
other and meet halfway, thinning as they go, and a few short branches end in the open. Branch thickness varies widely. Colour fades from
green to yellow, left to right, like the other Research pictures. Deterministic (fixed seed); pure Pillow.

    .venv/bin/python scripts/make_neural_synaptic_mechanisms_image.py [output.png]     # default: content/images/neural-synaptic-mechanisms.png
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3
MARGIN, MIN_GAP, NEIGHBOURS = 90, 118, 3  # keep-out edge, closest two cell bodies may be, outgoing connections per neuron
SOMA = 13  # cell body radius
STOPS = [(0.0, (0, 105, 62)), (0.5, (127, 168, 58)), (1.0, (242, 184, 0))]  # green, yellow-green, yellow


def colour(x):
    t = min(1, max(0, (x - MARGIN) / (W - 2 * MARGIN)))
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def scatter(rng):
    """Random points no closer than MIN_GAP (dart throwing), so the scatter looks even but not regular."""
    pts = []
    for _ in range(40000):
        p = (rng.uniform(MARGIN, W - MARGIN), rng.uniform(MARGIN, H - MARGIN))
        if all(math.dist(p, q) >= MIN_GAP for q in pts):
            pts.append(p)
    return pts


def free_dendrites(rng, cx, cy, taken):
    """Short branches that end in the open: they leave the cell body in directions not used by a connection, bend a little and fork at the end."""
    strokes = []
    for _ in range(rng.randint(2, 4)):
        for _ in range(40):
            a = rng.uniform(0, 2 * math.pi)
            if all(abs((a - b + math.pi) % (2 * math.pi) - math.pi) > 0.7 for b in taken):
                break
        else:
            continue
        taken.append(a)
        x, y = cx + SOMA * math.cos(a), cy + SOMA * math.sin(a)
        pts = [(x, y)]
        for _ in range(3):
            a += rng.uniform(-0.45, 0.45)
            x, y = x + 13 * math.cos(a), y + 13 * math.sin(a)
            pts.append((x, y))
        strokes.append((pts, 4.0, 1.8))
        for turn in (-0.55, 0.55):
            fa, fx, fy, fpts = a + turn + rng.uniform(-0.2, 0.2), x, y, [(x, y)]
            for _ in range(2):
                fa += rng.uniform(-0.3, 0.3)
                fx, fy = fx + 9 * math.cos(fa), fy + 9 * math.sin(fa)
                fpts.append((fx, fy))
            strokes.append((fpts, 1.8, 1.0))
    return strokes


def stroke(d, pts, w0, w1, c):
    """A line that tapers from width w0 to w1 (in picture pixels), drawn as short round-ended pieces."""
    n = len(pts) - 1
    for i, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:])):
        w = (w0 + (w1 - w0) * (i + 0.5) / n) * SCALE
        d.line((xa * SCALE, ya * SCALE, xb * SCALE, yb * SCALE), fill=c, width=round(w))
        r = w / 2
        d.ellipse((xb * SCALE - r, yb * SCALE - r, xb * SCALE + r, yb * SCALE + r), fill=c)


def link(rng, a, b):
    """A branch from neuron a and a branch from neuron b that grow towards each other and meet halfway, thinning as they go."""
    (x0, y0), (x1, y1) = a, b
    gap = math.dist(a, b)
    ang = math.atan2(y1 - y0, x1 - x0)
    sx, sy = x0 + SOMA * math.cos(ang), y0 + SOMA * math.sin(ang)
    ex, ey = x1 - SOMA * math.cos(ang), y1 - SOMA * math.sin(ang)
    nx, ny = -(ey - sy), ex - sx
    norm = math.hypot(nx, ny) or 1
    bend = rng.uniform(-0.22, 0.22) * gap
    mx, my = (sx + ex) / 2 + nx / norm * bend, (sy + ey) / 2 + ny / norm * bend
    curve = [((1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * ex, (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * ey) for t in [k / 24 for k in range(25)]]
    return curve[:13], curve[12:][::-1], ang


def draw(path):
    rng = random.Random(5)
    pts = scatter(rng)
    pairs = set()
    for i, p in enumerate(pts):
        for j in sorted((j for j in range(len(pts)) if j != i), key=lambda j: math.dist(p, pts[j]))[:NEIGHBOURS]:
            pairs.add((min(i, j), max(i, j)))
    taken = [[] for _ in pts]  # directions in which each neuron already has a connecting branch
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    d = ImageDraw.Draw(big)
    for i, j in sorted(pairs):
        half_i, half_j, ang = link(rng, pts[i], pts[j])
        taken[i].append(ang)
        taken[j].append(ang + math.pi)
        for half, owner in ((half_i, i), (half_j, j)):
            strength = math.exp(rng.uniform(math.log(1.5), math.log(7)))  # each side has its own strength: many weak, a few strong
            stroke(d, half, strength, 0.8, colour(pts[owner][0]))
    for (x, y), used in zip(pts, taken):
        c = colour(x)
        for spts, w0, w1 in free_dendrites(rng, x, y, used):
            stroke(d, spts, w0, w1, c)
        r, halo = SOMA * SCALE, 3 * SCALE
        d.ellipse((x * SCALE - r - halo, y * SCALE - r - halo, x * SCALE + r + halo, y * SCALE + r + halo), fill="white")  # white ring so the cell body stands clear of the branches
        d.ellipse((x * SCALE - r, y * SCALE - r, x * SCALE + r, y * SCALE + r), fill=c)
    path.parent.mkdir(parents=True, exist_ok=True)
    big.resize((W, H), Image.LANCZOS).save(path)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "content" / "images" / "neural-synaptic-mechanisms.png")
