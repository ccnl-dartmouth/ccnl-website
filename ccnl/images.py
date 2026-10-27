"""Image checking and processing: resize, strip metadata (incl. GPS), convert HEIC."""

import shutil
from pathlib import Path

from PIL import Image, ImageOps

try:  # HEIC support is optional; iPhone photos need it
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:  # pragma: no cover
    pillow_heif = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".gif", ".svg"}
MAX_BYTES = 25 * 1024 * 1024  # GitHub's browser upload limit; larger files are almost surely a mistake


def process_image(src, dest_dir, name, max_px, where, problems):
    """Write a web-sized copy of `src` into `dest_dir` as `name`.<ext>.

    Returns the output filename, or None (after recording an error).
    """
    src = Path(src)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()

    if src.stat().st_size > MAX_BYTES:
        problems.error(where, f"image '{src.name}' is larger than 25 MB. Shrink it (e.g. export at a lower quality) and upload it again.")
        return None

    if ext in (".svg", ".gif"):  # vector / animated: copy unchanged
        out = f"{name}{ext}"
        shutil.copyfile(src, dest_dir / out)
        return out

    if ext in (".heic", ".heif") and pillow_heif is None:
        problems.error(where, f"'{src.name}' is a HEIC photo and this build cannot read HEIC. Export it as JPG and upload that instead.")
        return None

    try:
        with Image.open(src) as im:
            if im.getexif().get_ifd(0x8825):  # GPS block
                problems.warn(
                    where,
                    f"'{src.name}' contains GPS location data. The website strips it, but the original file is public in the repository: "
                    "remove the location (e.g. re-export the photo without metadata) and upload it again.",
                )
            im = ImageOps.exif_transpose(im)  # apply camera rotation before metadata is dropped
            im.load()
    except Exception as exc:  # corrupt or not really an image
        problems.error(where, f"image '{src.name}' could not be opened ({exc.__class__.__name__}). Re-export it as JPG or PNG and upload it again.")
        return None

    im.thumbnail((max_px, max_px))  # keeps aspect ratio, never enlarges

    if im.mode == "P":  # palette images: expand so the copy below keeps the colors
        im = im.convert("RGBA" if "transparency" in im.info else "RGB")
    elif im.mode not in ("RGB", "RGBA", "L", "LA"):  # CMYK, 16-bit, ...
        im = im.convert("RGB")

    if ext == ".png":
        out, fmt, kwargs = f"{name}.png", "PNG", {"optimize": True}
    elif ext == ".webp":
        out, fmt, kwargs = f"{name}.webp", "WEBP", {"quality": 85}
    else:  # jpg, jpeg, heic, heif -> jpg (no alpha channel)
        out, fmt, kwargs = f"{name}.jpg", "JPEG", {"quality": 85, "optimize": True}
        if im.mode in ("RGBA", "LA"):
            im = im.convert("RGB")

    clean = Image.new(im.mode, im.size)  # new image object carries no EXIF/GPS
    clean.paste(im)
    clean.save(dest_dir / out, fmt, **kwargs)
    return out
