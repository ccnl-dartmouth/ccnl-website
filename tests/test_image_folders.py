"""All pictures live together in content/images/ and are paired with pages and papers by name."""

from conftest import bib, image_bytes, person_md


# ----- people photos


def test_people_photo_in_the_images_folder_is_paired_by_name(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("images/new-person.jpg", image_bytes((900, 900)))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    assert (sandbox.out / "images" / "people" / "new-person.jpg").is_file()


def test_photo_left_next_to_the_profile_file_is_flagged_and_not_used(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("people/new-person.jpg", image_bytes())
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("people/new-person.jpg", "content/images/")
    assert not (sandbox.out / "images" / "people" / "new-person.jpg").exists()


def test_photo_name_with_wrong_capitals_is_an_error(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("images/New-Person.JPG", image_bytes())
    assert sandbox.build().has_error("New-Person.JPG", "rename the image to 'new-person.jpg'", "case-sensitive")


def test_two_images_with_the_same_name_is_an_error(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("images/new-person.jpg", image_bytes())
    sandbox.write("images/new-person.png", image_bytes(fmt="PNG"))
    assert sandbox.build().has_error("new-person.png", "two images named 'new-person'")


# ----- paper thumbnails


def test_thumbnail_named_like_the_bib_file_is_used_without_an_image_line(sandbox):
    sandbox.write("publications/2026-doe-paper.bib", bib("doe2026paper", title="Thumbnail paper"))
    sandbox.write("images/2026-doe-paper.jpg", image_bytes((800, 600)))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    assert (sandbox.out / "images" / "publications" / "doe2026paper.jpg").is_file()
    block = result.page("publications/index.html").split('pub-title">Thumbnail paper')[1].split("</li>")[0]
    assert "images/publications/doe2026paper.jpg" in block and "pub-placeholder.svg" not in block


def test_image_line_can_name_any_file_in_the_images_folder(sandbox):
    sandbox.write("images/duggins2024spiking_thumb.png", image_bytes((900, 600), fmt="PNG"))
    sandbox.write("publications/duggins2024spiking.bib", bib("duggins2024spiking", title="Spiking paper", image="duggins2024spiking_thumb.png"))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings  # an explicit line also counts as "used"
    assert (sandbox.out / "images" / "publications" / "duggins2024spiking.png").is_file()


def test_one_figure_can_be_shared_by_several_papers(sandbox):
    sandbox.write("images/shared.png", image_bytes((900, 600), fmt="PNG"))
    sandbox.write("publications/a.bib", bib("a2024", title="Paper A", image="shared.png"))
    sandbox.write("publications/b.bib", bib("b2024", title="Paper B", image="shared.png"))
    result = sandbox.build()
    assert result.ok, result.errors
    assert (sandbox.out / "images" / "publications" / "a2024.png").is_file()
    assert (sandbox.out / "images" / "publications" / "b2024.png").is_file()


def test_missing_image_line_target_names_the_folder_to_use(sandbox):
    sandbox.write("publications/new.bib", bib(image="cover.png"))
    assert sandbox.build().has_error("new.bib", "image 'cover.png' was not found in content/images/")


def test_thumbnail_left_in_the_publications_folder_is_flagged(sandbox):
    sandbox.write("publications/stray.jpg", image_bytes())
    result = sandbox.build()
    assert result.ok and result.has_warning("publications/stray.jpg", "content/images/")


# ----- research figures


def test_research_figure_named_like_the_theme_file_is_used(sandbox):
    sandbox.write("research/new-theme.md", "---\ntitle: New theme\norder: 9\nimage_alt: A figure\n---\nText\n")
    sandbox.write("images/new-theme.jpg", image_bytes((1600, 1000)))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    assert "images/research/new-theme.jpg" in result.page("research/index.html")


def test_research_image_line_names_a_file_in_the_images_folder(sandbox):
    sandbox.write("research/new-theme.md", "---\ntitle: New theme\norder: 9\nimage: other.jpg\nimage_alt: A figure\n---\nText\n")
    sandbox.write("images/other.jpg", image_bytes((1600, 1000)))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    assert (sandbox.out / "images" / "research" / "new-theme.jpg").is_file()


def test_research_figure_left_in_the_research_folder_is_flagged(sandbox):
    sandbox.write("research/stray.png", image_bytes(fmt="PNG"))
    result = sandbox.build()
    assert result.ok and result.has_warning("research/stray.png", "content/images/")


def test_theme_without_a_figure_builds_without_an_image_warning(sandbox):
    sandbox.write("research/plain.md", "---\ntitle: Plain theme\norder: 9\n---\nText only.\n")
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings


# ----- one folder: collisions, unused images, site images


def test_a_name_used_by_two_kinds_of_file_cannot_be_paired(sandbox):
    sandbox.write("people/learning.md", person_md(name="Learning Person"))  # 'learning' is also a research theme
    result = sandbox.build()
    assert result.has_error("images/learning.jpg", "belongs to both a person and a research theme")


def test_same_name_for_two_kinds_is_fine_when_there_is_no_image(sandbox):
    sandbox.remove("images/learning.jpg")
    sandbox.write("people/learning.md", person_md(name="Learning Person"))
    assert sandbox.build().ok


def test_an_image_that_matches_nothing_warns(sandbox):
    sandbox.write("images/nothing-here.jpg", image_bytes())
    result = sandbox.build()
    assert result.ok
    assert result.has_warning("images/nothing-here.jpg", "doesn't match any person, paper or research theme")


def test_logos_and_the_hero_are_not_reported_as_unused(sandbox):
    result = sandbox.build()
    assert result.warnings == [], result.warnings  # institution-logo.svg and the funder logos are named in lab.yaml


def test_only_logos_and_hero_are_published_as_site_images(sandbox):
    sandbox.build()
    site = sandbox.out / "images" / "site"
    assert (site / "institution-logo.svg").is_file() and (site / "funder-one.png").is_file()
    assert not (site / "pat-investigator.jpg").exists() and not (site / "learning.jpg").exists()
