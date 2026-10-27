from conftest import image_bytes, person_md


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
    for field in ("role", "status"):
        assert result.has_error("new-person.md", f"missing required field '{field}'", "Add a line like")


def test_bad_role_lists_choices_and_suggests(sandbox):
    sandbox.write("people/new-person.md", person_md(role="postdoctoral"))
    result = sandbox.build()
    assert result.has_error("new-person.md", "'role' must be one of", "pi, postdoc, grad")


def test_current_member_must_not_have_end(sandbox):
    sandbox.write("people/new-person.md", person_md(end=2025))
    result = sandbox.build()
    assert result.has_error("new-person.md", "status: alumni")


def test_end_before_start(sandbox):
    sandbox.write("people/new-person.md", person_md(status="alumni", start=2023, end=2020))
    result = sandbox.build()
    assert result.has_error("new-person.md", "before")


def test_alumnus_without_position_is_fine(sandbox):
    sandbox.write("people/new-person.md", person_md(status="alumni", end=2025))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings


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
    assert [g["role"] for g in site["people_groups"]] == ["pi", "postdoc", "grad", "undergrad", "collaborator"]
    assert "Lee Alumna" in [p["name"] for p in site["alumni"]]
    assert all(p["status"] == "alumni" for p in site["alumni"])


def test_alumni_sorted_newest_first(sandbox):
    sandbox.write("people/old-alum.md", person_md(name="Old Alum", status="alumni", end=2010, start=2005, current_position="X"))
    sandbox.write("people/new-alum.md", person_md(name="New Alum", status="alumni", end=2024, start=2019, current_position="Y"))
    names = [p["name"] for p in sandbox.build().site["alumni"]]
    assert names.index("New Alum") < names.index("Lee Alumna") < names.index("Old Alum")


# ----- optional dates and profile pages


def test_dates_are_optional_for_everyone(sandbox):
    sandbox.write("people/current-person.md", person_md(start=None))
    sandbox.write("people/old-person.md", person_md(name="Old Person", status="alumni", start=None))
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    assert next(p for p in result.site["people"] if p["slug"] == "current-person")["years"] == ""


def test_years_labels():
    from ccnl.content import years_label

    assert years_label(2022, None, "current") == "2022\u2013present"
    assert years_label(2014, 2019, "alumni") == "2014\u20132019"
    assert years_label(2019, 2019, "alumni") == "2019"
    assert years_label(None, 2020, "alumni") == "until 2020"
    assert years_label(None, None, "current") == ""


def test_current_members_always_get_a_profile_page(sandbox):
    for role in ("postdoc", "grad", "undergrad"):
        sandbox.write(f"people/new-{role}.md", person_md(name=f"New {role}", role=role, body=""))
    sandbox.build()
    for role in ("postdoc", "grad", "undergrad"):
        assert (sandbox.out / "people" / f"new-{role}" / "index.html").is_file(), role


def test_alumni_and_collaborators_get_a_profile_only_with_a_bio(sandbox):
    sandbox.write("people/alum-no-bio.md", person_md(name="Alum NoBio", status="alumni", start=2015, end=2020, body=""))
    sandbox.write("people/alum-bio.md", person_md(name="Alum Bio", status="alumni", start=2015, end=2020, body="I did things.\n"))
    sandbox.write("people/collab-no-bio.md", person_md(name="Collab NoBio", role="collaborator", body=""))
    sandbox.write("people/collab-bio.md", person_md(name="Collab Bio", role="collaborator", body="Collaborates.\n"))
    sandbox.build()
    for slug, expected in (("alum-no-bio", False), ("alum-bio", True), ("collab-no-bio", False), ("collab-bio", True)):
        assert (sandbox.out / "people" / slug).exists() is expected, slug


def test_profile_flag_overrides_the_default(sandbox):
    sandbox.write("people/forced.md", person_md(name="Forced", status="alumni", start=2015, end=2020, body="", profile="true"))
    sandbox.write("people/hidden.md", person_md(name="Hidden", body="A bio.\n", profile="false"))
    sandbox.build()
    assert (sandbox.out / "people" / "forced" / "index.html").is_file()
    assert not (sandbox.out / "people" / "hidden").exists()


def test_current_member_cards_link_to_their_profile_page(sandbox):
    sandbox.write("people/new-person.md", person_md(body=""))
    assert 'href="/people/new-person/"' in sandbox.build().page("people/index.html")


def test_position_shows_in_alumni_list(sandbox):
    sandbox.write("people/new-alum.md", person_md(name="New Alum", status="alumni", end=2024, current_position="Doctor"))
    assert "Doctor" in sandbox.build().page("people/index.html")


def test_collaborators_without_dates_show_their_institution(sandbox):
    sandbox.write("people/collab.md", person_md(name="Some Collaborator", role="collaborator", start=None, current_position="Big University"))
    html = sandbox.build().page("people/index.html")
    assert "Some Collaborator" in html and "Big University" in html
