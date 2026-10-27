from io import BytesIO

import pytest
from conftest import image_bytes, person_md
from PIL import Image

from ccnl.images import process_image
from ccnl.problems import Problems


def add_person_with_photo(sandbox, data, ext="jpg"):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write(f"images/new-person.{ext}", data)


def test_large_photo_is_shrunk(sandbox):
    add_person_with_photo(sandbox, image_bytes((4000, 3000)))
    assert sandbox.build().ok
    with Image.open(sandbox.out / "images" / "people" / "new-person.jpg") as im:
        assert im.size == (700, 525)


def test_small_photo_is_not_enlarged(sandbox):
    add_person_with_photo(sandbox, image_bytes((200, 100)))
    sandbox.build()
    with Image.open(sandbox.out / "images" / "people" / "new-person.jpg") as im:
        assert im.size == (200, 100)


def test_exif_is_stripped_and_rotation_applied(sandbox):
    exif = Image.Exif()
    exif[274] = 6  # orientation: rotate 90 degrees
    exif[0x010F] = "SecretCameraMaker"
    add_person_with_photo(sandbox, image_bytes((200, 100), exif=exif))
    assert sandbox.build().ok
    out = sandbox.out / "images" / "people" / "new-person.jpg"
    with Image.open(out) as im:
        assert im.size == (100, 200)  # rotated
        assert len(im.getexif()) == 0
    assert b"SecretCameraMaker" not in out.read_bytes()


def test_heic_is_converted_to_jpg(sandbox):
    pillow_heif = pytest.importorskip("pillow_heif")
    pillow_heif.register_heif_opener()
    try:
        data = image_bytes((300, 200), fmt="HEIF")
    except Exception as exc:  # encoder missing in this build of libheif
        pytest.skip(f"cannot create a HEIC test file here: {exc}")
    add_person_with_photo(sandbox, data, ext="heic")
    result = sandbox.build()
    assert result.ok, result.errors
    assert (sandbox.out / "images" / "people" / "new-person.jpg").is_file()


def test_png_stays_png_and_palette_images_work(sandbox):
    buf = BytesIO()
    Image.new("P", (40, 40)).save(buf, "PNG", transparency=0)
    add_person_with_photo(sandbox, buf.getvalue(), ext="png")
    result = sandbox.build()
    assert result.ok, result.errors
    assert (sandbox.out / "images" / "people" / "new-person.png").is_file()


def test_corrupt_image_explains_what_to_do(sandbox):
    add_person_with_photo(sandbox, b"this is not an image")
    result = sandbox.build()
    assert result.has_error("new-person.jpg", "could not be opened", "Re-export")


def test_oversized_image_is_rejected(sandbox):
    add_person_with_photo(sandbox, b"\0" * (26 * 1024 * 1024))
    assert sandbox.build().has_error("new-person.jpg", "larger than 25 MB")


def test_svg_is_copied_unchanged(tmp_path):
    src = tmp_path / "logo.svg"
    src.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    problems = Problems()
    out = process_image(src, tmp_path / "out", "logo", 100, "logo.svg", problems)
    assert out == "logo.svg" and (tmp_path / "out" / "logo.svg").is_file()
    assert not problems.errors


def test_photo_with_gps_data_warns_but_builds(sandbox):
    exif = Image.Exif()
    exif[0x8825] = {1: "N", 2: (43.0, 42.0, 10.0), 3: "W", 4: (72.0, 17.0, 20.0)}
    add_person_with_photo(sandbox, image_bytes((200, 100), exif=exif))
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("new-person.jpg", "GPS location data")


def test_photo_without_gps_data_does_not_warn(sandbox):
    add_person_with_photo(sandbox, image_bytes((200, 100)))
    assert sandbox.build().warnings == []
