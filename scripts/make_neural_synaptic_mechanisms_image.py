"""Generate the Research page picture for "Neural and synaptic mechanisms".

A loose scatter of neurons, each with an irregular cell body and nucleus, thick dendrites that taper and branch
repeatedly, tiny spines along the branches, and a short axon ending in a bulb. Each neuron is placed at random but is only
kept if it clears every neuron already placed, so nothing overlaps and nothing runs off the edge. Colour fades from
green to yellow, left to right, like the other Research pictures. Deterministic (fixed seed); pure Pillow.

    .venv/bin/python scripts/make_neural_synaptic_mechanisms_image.py [output.png]     # default: content/images/neural-synaptic-mechanisms.png
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 1600, 1000, 3
EDGE, CLEAR = 40, 15  # how close a neuron may come to the picture's edge, and to another neuron (pixels)
SIZES = (1.0, 0.82, 0.66, 0.52)  # how large a neuron may be, tried from the biggest down
FAIL_LIMIT, ATTEMPTS = 1500, 20000  # stop after this many failed tries in a row, or this many tries overall
COLOUR_FROM, COLOUR_TO = 90, W - 90  # the left and right ends of the colour fade
SOMA = 21  # cell body radius
STOPS = [(0.0, (0, 105, 62)), (0.5, (127, 168, 58)), (1.0, (242, 184, 0))]  # green, yellow-green, yellow


def colour(x, lift=0.0):
    t = min(1, max(0, (x - COLOUR_FROM) / (COLOUR_TO - COLOUR_FROM)))
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            c = tuple(a + (b - a) * f for a, b in zip(c0, c1))
            return tuple(round(v + (255 - v) * lift) for v in c)
    return STOPS[-1][1]


def grow(rng, x, y, ang, steps, step, width, depth, out):
    """One branch of a dendrite: it bends gently, tapers, then splits into two thinner branches."""
    pts = [(x, y)]
    for _ in range(steps):
        ang += rng.uniform(-0.4, 0.4)
        x, y = x + step * math.cos(ang), y + step * math.sin(ang)
        pts.append((x, y))
    end_width = width * 0.62
    out.append((pts, width, end_width))
    if depth:
        for turn in (-1, 1):
            grow(rng, x, y, ang + turn * rng.uniform(0.35, 0.75), max(2, steps - 1), step * 0.85, end_width, depth - 1, out)
        if depth == 2 and rng.random() < 0.4:  # now and then a third branch
            grow(rng, x, y, ang + rng.uniform(-0.2, 0.2), max(2, steps - 1), step * 0.85, end_width, depth - 1, out)


def neuron(rng, cx, cy, scale=1.0):
    """One neuron (`scale` shrinks its branches, so smaller ones can fill the gaps): dendrite strokes, spines, a short axon with its end bulb, and points sampled along all of it (for the overlap check)."""
    strokes = []
    count = rng.randint(4, 6)
    start = rng.uniform(0, 2 * math.pi)
    angles = [start + 2 * math.pi * k / count + rng.uniform(-0.3, 0.3) for k in range(count)]
    for a in angles:
        grow(rng, cx + SOMA * 0.8 * math.cos(a), cy + SOMA * 0.8 * math.sin(a), a, 4, 17 * scale, 8.5 * scale ** 0.5, 2, strokes)
    axon = start + math.pi / count + rng.uniform(-0.2, 0.2)  # one thin axon in the gap between dendrites, ending in a small bulb
    apts = [(cx + SOMA * 0.9 * math.cos(axon), cy + SOMA * 0.9 * math.sin(axon))]
    for _ in range(5):
        axon += rng.uniform(-0.25, 0.25)
        apts.append((apts[-1][0] + 14 * scale * math.cos(axon), apts[-1][1] + 14 * scale * math.sin(axon)))
    spines = []  # tiny stubs with a rounded head, sticking out along the thinner branches
    for spts, w0, _ in strokes:
        if w0 <= 5:
            for (xa, ya), (xb, yb) in zip(spts, spts[1:]):
                if rng.random() < 0.7:
                    t = rng.random()
                    x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
                    ang = math.atan2(yb - ya, xb - xa) + rng.choice((-1, 1)) * rng.uniform(1.0, 1.9)
                    L = rng.uniform(3.5, 6.5)
                    spines.append((x, y, x + L * math.cos(ang), y + L * math.sin(ang)))
    samples = [(cx + SOMA * math.cos(a), cy + SOMA * math.sin(a)) for a in [i * math.pi / 6 for i in range(12)]] + [(cx, cy)]
    for spts, _, _ in strokes + [(apts, 0, 0)]:
        for (xa, ya), (xb, yb) in zip(spts, spts[1:]):
            n = max(1, int(math.dist((xa, ya), (xb, yb)) / 4))
            samples += [(xa + (xb - xa) * i / n, ya + (yb - ya) * i / n) for i in range(n + 1)]
    samples += [(hx, hy) for _, _, hx, hy in spines]
    return {"x": cx, "y": cy, "strokes": strokes, "axon": apts, "spines": spines, "samples": samples}


def taper(d, pts, w0, w1, c):
    """A line that tapers from width w0 to w1 (in picture pixels), drawn as short round-ended pieces."""
    n = len(pts) - 1
    for i, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:])):
        w = (w0 + (w1 - w0) * (i + 0.5) / n) * SCALE
        d.line((xa * SCALE, ya * SCALE, xb * SCALE, yb * SCALE), fill=c, width=max(1, round(w)))
        r = w / 2
        d.ellipse((xb * SCALE - r, yb * SCALE - r, xb * SCALE + r, yb * SCALE + r), fill=c)


def dot(d, x, y, r, c):
    d.ellipse(((x - r) * SCALE, (y - r) * SCALE, (x + r) * SCALE, (y + r) * SCALE), fill=c)


def soma_outline(rng, cx, cy):
    """An irregular, slightly pointed cell body."""
    k, phase = rng.randint(3, 5), rng.uniform(0, 2 * math.pi)
    return [(cx + SOMA * (1 + 0.14 * math.cos(k * a + phase)) * math.cos(a), cy + SOMA * (1 + 0.14 * math.cos(k * a + phase)) * math.sin(a)) for a in [i * math.pi / 45 for i in range(90)]]


def place(rng):
    """Neurons at random spots, each kept only if all of it fits in the picture and stays clear of the neurons already placed."""
    cells, taken, cell = [], {}, CLEAR  # `taken` buckets every placed point by grid square, so the clearance check is quick
    key = lambda p: (int(p[0] // cell), int(p[1] // cell))
    fails = 0
    for _ in range(ATTEMPTS):
        if fails >= FAIL_LIMIT:
            break
        cx, cy = rng.uniform(EDGE + 30, W - EDGE - 30), rng.uniform(EDGE + 30, H - EDGE - 30)
        for scale in SIZES:  # the biggest version of the neuron that fits at this spot
            n = neuron(rng, cx, cy, scale)
            ok = all(EDGE <= x <= W - EDGE and EDGE <= y <= H - EDGE for x, y in n["samples"])
            for x, y in n["samples"] if ok else []:
                gx, gy = key((x, y))
                if any(math.dist((x, y), q) < CLEAR for i in (-1, 0, 1) for j in (-1, 0, 1) for q in taken.get((gx + i, gy + j), ())):
                    ok = False
                    break
            if ok:
                break
        if ok:
            for p in n["samples"]:
                taken.setdefault(key(p), []).append(p)
            cells.append(n)
            fails = 0
        else:
            fails += 1
    return cells


def draw(path):
    rng = random.Random(5)
    big = Image.new("RGB", (W * SCALE, H * SCALE), "white")
    d = ImageDraw.Draw(big)
    cells = place(rng)
    for n in cells:
        c = colour(n["x"])
        for spts, w0, w1 in n["strokes"]:
            taper(d, spts, w0, w1, c)
        for x, y, hx, hy in n["spines"]:
            d.line((x * SCALE, y * SCALE, hx * SCALE, hy * SCALE), fill=c, width=SCALE)
            dot(d, hx, hy, 1.7, c)
        taper(d, n["axon"], 2.6, 1.6, c)
        dot(d, n["axon"][-1][0], n["axon"][-1][1], 3.6, c)  # the axon's end bulb
    for n in cells:
        x, y = n["x"], n["y"]
        c = colour(x)
        body = soma_outline(rng, x, y)
        d.polygon([(px * SCALE, py * SCALE) for px, py in body], fill="white", outline="white", width=3 * SCALE)  # a white ring so the cell body stands clear of the branches
        d.polygon([(px * SCALE, py * SCALE) for px, py in body], fill=c)
        dot(d, x + 2, y - 1, SOMA * 0.42, colour(x, 0.45))  # the nucleus
    print(len(cells), "neurons")
    path.parent.mkdir(parents=True, exist_ok=True)
    big.resize((W, H), Image.LANCZOS).save(path)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "content" / "images" / "neural-synaptic-mechanisms.png")
