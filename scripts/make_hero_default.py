"""Generate static/hero-default.svg, the placeholder hero picture used until the lab adds a real photo.

An abstract network of nodes on dark green. Deterministic (fixed seed), so rerunning gives the same file.

    .venv/bin/python scripts/make_hero_default.py
"""

import random
from pathlib import Path

W, H = 1600, 560
random.seed(7)

nodes = [(random.uniform(40, W - 40), random.uniform(30, H - 30), random.choice((2.5, 3, 4, 5, 7))) for _ in range(70)]
links = []
for i, (x1, y1, _) in enumerate(nodes):
    near = sorted(range(len(nodes)), key=lambda j: (nodes[j][0] - x1) ** 2 + (nodes[j][1] - y1) ** 2)[1:3]
    for j in near:
        if i < j or i not in [n for n in near]:
            links.append((i, j))

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="presentation" aria-hidden="true">',
    f'<rect width="{W}" height="{H}" fill="#0b3b29"/>',
    '<g stroke="#4fa57d" stroke-opacity="0.45" stroke-width="1.2">',
]
for i, j in links:
    parts.append(f'<line x1="{nodes[i][0]:.0f}" y1="{nodes[i][1]:.0f}" x2="{nodes[j][0]:.0f}" y2="{nodes[j][1]:.0f}"/>')
parts.append("</g>")
for k, (x, y, r) in enumerate(nodes):
    fill = "#f2a900" if k % 11 == 0 else "#bfe3cf"
    opacity = 0.95 if k % 11 == 0 else 0.55
    parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{fill}" fill-opacity="{opacity}"/>')
parts.append("</svg>")

out = Path(__file__).resolve().parent.parent / "static" / "hero-default.svg"
out.write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
