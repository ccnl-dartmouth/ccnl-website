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
    for target in ("research/", "publications/", "people/", "contact/"):
        assert f'href="/{target}"' in html
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: People, page: people}\n")
    html = sandbox.build().page("index.html")
    assert 'href="/people/"' in html and 'href="/contact/"' not in html and 'href="/research/"' not in html


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


def test_thumbnails_are_on_the_publications_page_and_home_lists_no_papers(sandbox):
    result = sandbox.build()
    assert "images/publications/student2024context.jpg" in result.page("publications/index.html")
    home = result.page("index.html")
    assert "Selected publications" not in home and "pub-thumb" not in home and "Context effects" not in home


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


def test_collaborators_are_listed_last_after_alumni(sandbox):
    html = sandbox.build().page("people/index.html")
    assert html.index("<h2>Alumni</h2>") < html.index("<h2>Collaborators</h2>")
    assert html.index("<h2>Graduate Students</h2>") < html.index("<h2>Alumni</h2>")


def test_alumni_link_to_their_minimal_profile_pages(sandbox):
    html = sandbox.build().page("people/index.html")
    alumni = html.split("<h2>Alumni</h2>")[1].split("</section>")[0]
    assert 'href="/people/lee-alumna/"' in alumni and 'href="/people/quinn-alumnus/"' in alumni


# ----- header, hero, footer, contact page


def test_header_is_a_centered_nav_without_the_lab_name(sandbox):
    html = sandbox.build().page("people/index.html")
    header = html.split('<header class="site-header">')[1].split("</header>")[0]
    assert 'class="brand"' not in header and "Sample Neuroscience Lab" not in header
    assert 'aria-label="Main"' in header


def test_nav_order_has_teaching_before_resources(sandbox):
    html = sandbox.build().page("index.html")
    assert html.index(">Teaching<") < html.index(">Resources<") < html.index(">Contact<")
    assert ">Join<" not in html


def test_hero_card_shows_the_name_and_the_affiliation_not_the_tagline(sandbox):
    hero = sandbox.build().page("index.html").split('<div class="hero-overlay">')[1].split("</section>")[0]
    assert "Department of Examples, Example University" in hero
    assert "A fake lab used to test the website build." not in hero


def test_contact_page_includes_the_join_section(sandbox):
    result = sandbox.build()
    html = result.page("contact/index.html")
    assert 'id="join"' in html and "Join us" in html and "currently recruiting" in html
    assert "Graduate students" in html  # the join.md text


def test_contact_page_without_join_file_is_just_contact(sandbox):
    sandbox.remove("join.md")
    result = sandbox.build()
    assert result.ok, result.errors
    assert 'id="join"' not in result.page("contact/index.html")


def test_join_is_no_longer_a_page(sandbox):
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: Join, page: join}\n")
    assert sandbox.build().has_error("site.yaml", "unknown page 'join'")


def test_footer_shows_institution_and_funder_logos_with_alt_text(sandbox):
    footer = sandbox.build().page("index.html").split('<footer class="site-footer">')[1]
    assert 'alt="Example University"' in footer and 'href="https://example.org"' in footer
    assert 'alt="Example Science Foundation"' in footer and 'alt="Example Health Institute"' in footer
    assert "Funding" not in sandbox.build().page("index.html").split("<footer")[0]  # not repeated on the page

    sandbox.edit("lab.yaml", "    logo: funder-two.png\n", "")  # a funder without a logo is simply not shown here
    footer = sandbox.build().page("index.html").split('<footer class="site-footer">')[1]
    assert 'alt="Example Health Institute"' not in footer


def test_missing_institution_logo_is_an_error(sandbox):
    sandbox.edit("lab.yaml", "institution_logo: institution-logo.svg", "institution_logo: nope.svg")
    assert sandbox.build().has_error("lab.yaml", "institution_logo 'nope.svg' was not found")


def test_svg_footer_logos_are_published_unchanged(sandbox):
    sandbox.build()
    assert (sandbox.out / "images" / "site" / "institution-logo.svg").is_file()
