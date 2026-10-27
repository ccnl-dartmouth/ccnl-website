"""Generate the placeholder images used by sample_content/. Run once; the output is committed.

    .venv/bin/python scripts/make_sample_images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "sample_content"


def card(path, size, color, text):
    im = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=max(size) // 6)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((size[0] - box[2]) / 2, (size[1] - box[3]) / 2), text, fill="white", font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=80)


people = {
    "pat-investigator": ((0, 105, 62), "PI"),
    "alex-postdoc": ((70, 90, 160), "AP"),
    "sam-student": ((160, 90, 70), "SS"),
    "robin-student": ((110, 70, 150), "RS"),
}
for slug, (color, text) in people.items():
    card(ROOT / "people" / f"{slug}.jpg", (1200, 1200), color, text)  # large on purpose: tests resizing

for slug, (color, text) in {
    "learning": ((30, 120, 120), "Learning"),
    "choice": ((150, 110, 30), "Choice"),
    "models": ((90, 90, 90), "Models"),
}.items():
    card(ROOT / "research" / f"{slug}.jpg", (1600, 900), color, text)

for name, color, text in (("context", (0, 105, 62), "Fig 1"), ("models", (70, 90, 160), "Fig 2")):
    card(ROOT / "publications" / f"{name}.jpg", (800, 600), color, text)

card(ROOT / "images" / "funder-one.png", (300, 120), (30, 60, 120), "FUNDER")
card(ROOT / "images" / "funder-two.png", (300, 120), (120, 60, 30), "GRANT")
print("sample images written to", ROOT)
