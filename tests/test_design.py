"""Page designs: hero, publication abstracts and thumbnails, people layouts, fonts, accessibility hooks."""

from conftest import image_bytes, person_md

HERO_HEADER = "---\nheadline: How do brains learn and decide?\nhero_image: lab.jpg\n{alt}---\n"


def set_hero(sandbox, alt="hero_alt: Lab members at the 2026 retreat\n", image=True):
    body = sandbox.path("home.md").read_text().split("---\n", 2)[2]
    sandbox.write("home.md", HERO_HEADER.format(alt=alt) + body)
    if image:
        sandbox.write("images/lab.jpg", image_bytes((3000, 1200)))


# ----- hero


def test_default_hero_is_used_without_a_photo_and_is_decorative(sandbox):
    html = sandbox.build().page("index.html")
    assert 'src="/static/hero-default.svg" alt=""' in html
    assert (sandbox.out / "static" / "hero-default.svg").is_file()


def test_lab_hero_photo_is_processed_and_described(sandbox):
    set_hero(sandbox)
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    html = result.page("index.html")
    assert 'src="/images/site/lab.jpg" alt="Lab members at the 2026 retreat"' in html
    from PIL import Image

    with Image.open(sandbox.out / "images" / "site" / "lab.jpg") as im:
        assert im.size[0] == 2000  # shrunk for the web


def test_missing_hero_file_is_an_error(sandbox):
    set_hero(sandbox, image=False)
    assert sandbox.build().has_error("home.md", "hero_image 'lab.jpg' was not found")


def test_hero_without_description_warns(sandbox):
    set_hero(sandbox, alt="")
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("home.md", "hero_alt")


# ----- home entry cards


def test_home_cards_follow_the_menu(sandbox):
    html = sandbox.build().page("index.html")
    for target in ("research/", "people/", "join/"):
        assert f'href="/{target}"' in html
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: People, page: people}\n")
    html = sandbox.build().page("index.html")
    assert 'href="/people/"' in html and 'href="/join/"' not in html and 'href="/research/"' not in html


# ----- publications


def test_abstract_is_collapsible_and_names_its_paper(sandbox):
    html = sandbox.build().page("publications/index.html")
    assert "<details" in html and "explains context effects" in html
    assert "<summary>Abstract<span class=\"sr-only\"> of Context effects in Bayesian choice</span></summary>" in html


def test_entry_without_abstract_has_no_details(sandbox):
    sandbox.write("publications/new.bib", "@article{plain2024,\n  author = {Doe, Jane},\n  title = {No abstract here},\n  journal = {J},\n  year = {2024},\n}\n")
    html = sandbox.build().page("publications/index.html")
    block = html.split("No abstract here")[1].split("</li>")[0]
    assert "<details" not in block


def test_thumbnails_only_on_publications_page_not_on_home(sandbox):
    result = sandbox.build()
    assert "images/publications/student2024context.jpg" in result.page("publications/index.html")
    assert "pub-thumb" not in result.page("index.html")
    assert "<details" not in result.page("index.html")  # home list is compact: no abstracts


def test_link_buttons_have_unambiguous_names(sandbox):
    html = sandbox.build().page("publications/index.html")
    assert 'PDF<span class="sr-only"> for A range-normalization model of context-dependent choice</span>' in html


# ----- people


def test_people_page_uses_photo_cards_for_current_and_a_list_for_alumni(sandbox):
    html = sandbox.build().page("people/index.html")
    current, alumni = html.split("<h2>Alumni</h2>")
    assert 'class="person-card"' in current and "person-card" not in alumni
    assert "Assistant Professor, Example College" in alumni


def test_person_without_photo_gets_an_initial(sandbox):
    sandbox.write("people/zed-nophoto.md", person_md(name="Zed Nophoto"))
    html = sandbox.build().page("people/index.html")
    assert 'class="avatar avatar-card placeholder" aria-hidden="true">Z<' in html


def test_profile_page_shows_details_card_and_bio(sandbox):
    html = sandbox.build().page("people/pat-investigator/index.html")
    assert 'aria-label="Details"' in html and "Principal Investigator" in html and "2015" in html
    assert "Pat is the (fictional) principal investigator" in html


# ----- fonts and static files


def test_fonts_are_self_hosted_with_licenses(sandbox):
    sandbox.build()
    fonts = sandbox.out / "static" / "fonts"
    for name in ("fonts.css", "inter-latin.woff2", "source-serif-4-latin.woff2", "LICENSE-Inter.txt", "LICENSE-SourceSerif4.md"):
        assert (fonts / name).is_file(), name
    css = (fonts / "fonts.css").read_text()
    assert "https://" not in css.replace("Inter and Source Serif 4", "")  # no third-party URLs
    html = sandbox.build().page("index.html")
    assert "fonts.googleapis" not in html and "gstatic" not in html


def test_collaborators_are_a_compact_list_linking_to_their_sites(sandbox):
    html = sandbox.build().page("people/index.html")
    section = html.split("<h2>Collaborators</h2>")[1].split("</section>")[0]
    assert "person-card" not in section and 'class="alumnus"' in section
    assert '<a href="https://example.org/kim">Kim Collaborator</a>' in section
    assert "Example Institute" in section
