from conftest import image_bytes, person_md


def test_sample_content_is_clean(sandbox):
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.warnings == []


def test_new_person_appears_on_people_page_and_gets_profile(sandbox):
    sandbox.write("people/new-person.md", person_md())
    result = sandbox.build()
    assert result.ok, result.errors
    assert "New Person" in result.page("people/index.html")
    assert (sandbox.out / "people" / "new-person" / "index.html").is_file()


def test_unknown_field_suggests_the_right_name(sandbox):
    sandbox.write("people/new-person.md", person_md(rol="grad", role=None))
    result = sandbox.build()
    assert result.has_error("people/new-person.md", "unknown field 'rol'", "did you mean 'role'")
    assert result.has_error("people/new-person.md", "missing required field 'role'")


def test_missing_required_fields_say_how_to_fix(sandbox):
    sandbox.write("people/new-person.md", "---\nname: New Person\n---\nBio\n")
    result = sandbox.build()
    for field in ("role", "status", "start"):
        assert result.has_error("new-person.md", f"missing required field '{field}'", "Add a line like")


def test_bad_role_lists_choices_and_suggests(sandbox):
    sandbox.write("people/new-person.md", person_md(role="postdoctoral"))
    result = sandbox.build()
    assert result.has_error("new-person.md", "'role' must be one of", "pi, postdoc, grad")


def test_alumnus_needs_end_year(sandbox):
    sandbox.write("people/new-person.md", person_md(status="alumni"))
    result = sandbox.build()
    assert result.has_error("new-person.md", "end: 2025")


def test_current_member_must_not_have_end(sandbox):
    sandbox.write("people/new-person.md", person_md(end=2025))
    result = sandbox.build()
    assert result.has_error("new-person.md", "status: alumni")


def test_end_before_start(sandbox):
    sandbox.write("people/new-person.md", person_md(status="alumni", start=2023, end=2020))
    result = sandbox.build()
    assert result.has_error("new-person.md", "before")


def test_alumnus_without_position_is_only_a_warning(sandbox):
    sandbox.write("people/new-person.md", person_md(status="alumni", end=2025))
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("new-person.md", "current_position")


def test_year_must_be_a_year(sandbox):
    sandbox.write("people/new-person.md", person_md(start="soon"))
    assert sandbox.build().has_error("new-person.md", "'start' must be a four-digit year")


def test_filename_must_be_lowercase_with_hyphens(sandbox):
    sandbox.write("people/New_Person.md", person_md())
    result = sandbox.build()
    assert result.has_error("New_Person.md", "lowercase letters, digits and hyphens")


def test_invalid_yaml_header_explains_cause(sandbox):
    sandbox.write("people/new-person.md", "---\nname: Bad: colon\nrole: grad\n---\nBio\n")
    result = sandbox.build()
    assert result.has_error("new-person.md", "not valid YAML", "quotes")


def test_header_must_be_closed(sandbox):
    # no closing '---': treated as plain text, so required fields are reported missing
    sandbox.write("people/new-person.md", "---\nname: New Person\nrole: grad\nBio\n")
    result = sandbox.build()
    assert result.has_error("new-person.md", "missing required field")


def test_windows_line_endings_and_bom_are_fine(sandbox):
    text = person_md().replace("\n", "\r\n")
    (sandbox.dir / "people").joinpath("new-person.md").write_bytes(b"\xef\xbb\xbf" + text.encode())
    result = sandbox.build()
    assert result.ok, result.errors


# ----- links and email


def test_links_are_validated_and_built(sandbox):
    sandbox.write(
        "people/new-person.md",
        "---\nname: New Person\nrole: grad\nstatus: current\nstart: 2023\nlinks:\n"
        "  scholar: https://scholar.google.com/x\n  orcid: 0000-0002-1825-0097\n"
        "  github: someone\n  email: n@example.edu\n---\nBio.\n",
    )
    result = sandbox.build()
    assert result.ok, result.errors
    html = result.page("people/new-person/index.html")
    assert "https://orcid.org/0000-0002-1825-0097" in html
    assert "https://github.com/someone" in html


def test_bad_link_entries(sandbox):
    sandbox.write(
        "people/new-person.md",
        "---\nname: N\nrole: grad\nstatus: current\nstart: 2023\nlinks:\n  scholr: https://x.org\n  website: example.org\n  email: nope\n---\n",
    )
    result = sandbox.build()
    assert result.has_error("new-person.md", "unknown entry 'scholr'", "scholar")
    assert result.has_error("new-person.md", "must be a full web address")
    assert result.has_error("new-person.md", "does not look like an email")


def test_email_is_obfuscated_in_html(sandbox):
    result = sandbox.build()
    html = result.page("people/pat-investigator/index.html")
    assert "mailto:" not in html
    assert 'data-user="pat"' in html and 'data-domain="example.edu"' in html
    assert "pat [at] example.edu" in html


# ----- photos


def test_photo_with_matching_name_is_used_and_resized(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("people/new-person.jpg", image_bytes((3000, 2000)))
    result = sandbox.build()
    assert result.ok, result.errors
    from PIL import Image

    with Image.open(sandbox.out / "images" / "people" / "new-person.jpg") as im:
        assert max(im.size) <= 700
    assert "images/people/new-person.jpg" in result.page("people/index.html")


def test_photo_name_case_mismatch_is_an_error(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("people/New-Person.JPG", image_bytes())
    result = sandbox.build()
    assert result.has_error("New-Person.JPG", "rename the image to 'new-person.jpg'", "case-sensitive")


def test_two_photos_for_one_person(sandbox):
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("people/new-person.jpg", image_bytes())
    sandbox.write("people/new-person.png", image_bytes(fmt="PNG"))
    assert sandbox.build().has_error("new-person", "two images")


def test_orphan_image_warns(sandbox):
    sandbox.write("people/someone-else.jpg", image_bytes())
    result = sandbox.build()
    assert result.ok
    assert result.has_warning("someone-else.jpg", "no matching .md")


def test_person_without_photo_is_fine(sandbox):
    sandbox.write("people/new-person.md", person_md())
    result = sandbox.build()
    assert result.ok and result.warnings == []


def test_stray_file_types_are_warned_about(sandbox):
    sandbox.write("people/notes.txt", "hello")
    result = sandbox.build()
    assert result.ok
    assert result.has_warning("notes.txt", "ignored")


# ----- grouping and profile pages


def test_profile_false_lists_person_without_page(sandbox):
    result = sandbox.build()
    assert "Kim Collaborator" in result.page("people/index.html")
    assert not (sandbox.out / "people" / "kim-collaborator").exists()


def test_groups_and_alumni_ordering(sandbox):
    site = sandbox.build().site
    assert [g["role"] for g in site["people_groups"]] == ["pi", "postdoc", "grad", "collaborator"]
    assert [p["name"] for p in site["alumni"]] == ["Lee Alumna"]


def test_alumni_sorted_newest_first(sandbox):
    sandbox.write("people/old-alum.md", person_md(name="Old Alum", status="alumni", end=2010, start=2005, current_position="X"))
    sandbox.write("people/new-alum.md", person_md(name="New Alum", status="alumni", end=2024, start=2019, current_position="Y"))
    site = sandbox.build().site
    assert [p["name"] for p in site["alumni"]] == ["New Alum", "Lee Alumna", "Old Alum"]
