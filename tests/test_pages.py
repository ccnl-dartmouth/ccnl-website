import datetime

from conftest import image_bytes


# ----- site.yaml, lab.yaml, home.md


def test_unknown_page_in_nav_suggests_name(sandbox):
    sandbox.edit("site.yaml", "page: people", "page: peple")
    result = sandbox.build()
    assert result.has_error("site.yaml", "unknown page 'peple'", "Did you mean 'people'")


def test_nav_item_needs_label_and_page(sandbox):
    sandbox.write("site.yaml", "nav:\n  - {label: Home}\n")
    assert sandbox.build().has_error("site.yaml", "nav item 1")


def test_missing_site_yaml(sandbox):
    sandbox.remove("site.yaml")
    assert sandbox.build().has_error("site.yaml", "missing")


def test_nav_order_follows_file(sandbox):
    sandbox.write("site.yaml", "nav:\n  - {label: People, page: people}\n  - {label: Home, page: home}\n")
    html = sandbox.build().page("index.html")
    assert html.index(">People<") < html.index(">Home<")


def test_pages_not_in_nav_are_not_built(sandbox):
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: People, page: people}\n")
    result = sandbox.build()
    assert result.ok, result.errors
    assert (sandbox.out / "people" / "index.html").is_file()
    assert not (sandbox.out / "join").exists()
    assert "Join us" not in result.page("index.html")  # call to action hidden without a Join page


def test_missing_lab_yaml(sandbox):
    sandbox.remove("lab.yaml")
    assert sandbox.build().has_error("lab.yaml", "missing")


def test_lab_yaml_requires_name(sandbox):
    sandbox.write("lab.yaml", "short_name: X\n")
    assert sandbox.build().has_error("lab.yaml", "missing required field 'name'")


def test_funder_logo_must_exist(sandbox):
    sandbox.edit("lab.yaml", "logo: funder-one.png", "logo: nope.png")
    assert sandbox.build().has_error("lab.yaml", "logo 'nope.png' was not found")


def test_funder_logo_with_transparency_survives(sandbox):
    from PIL import Image

    sandbox.write("images/funder-one.png", image_bytes((100, 50), fmt="PNG", mode="RGBA", color=(255, 0, 0, 0)))
    result = sandbox.build()
    assert result.ok, result.errors
    with Image.open(sandbox.out / "images" / "site" / "funder-one.png") as im:
        assert im.mode == "RGBA"


def test_social_link_validation(sandbox):
    sandbox.edit("lab.yaml", "github: https://github.com/example", "mastodon: https://x.org")
    assert sandbox.build().has_error("lab.yaml", "unknown site 'mastodon'")


def test_missing_home(sandbox):
    sandbox.remove("home.md")
    assert sandbox.build().has_error("home.md", "missing")


def test_about_missing_only_matters_if_in_nav(sandbox):
    sandbox.remove("about.md")
    assert sandbox.build().ok  # 'about' is not in the sample nav
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: About, page: about}\n")
    assert sandbox.build().has_error("about.md", "missing")


def test_about_page_rejects_front_matter_fields(sandbox):
    sandbox.write("site.yaml", "nav:\n  - {label: Home, page: home}\n  - {label: About, page: about}\n")
    sandbox.write("about.md", "---\ntitle: X\n---\nText\n")
    assert sandbox.build().has_error("about.md", "unknown field 'title'")


# ----- research themes


def test_research_order_and_title(sandbox):
    site = sandbox.build().site
    assert [t["title"] for t in site["research"]] == ["Adaptive learning", "Context-dependent choice", "Circuit models", "Naturalistic behavior"]


def test_research_theme_requires_title(sandbox):
    sandbox.write("research/untitled.md", "---\norder: 4\n---\nText\n")
    assert sandbox.build().has_error("untitled.md", "missing required field 'title'")


def test_research_image_must_exist(sandbox):
    sandbox.edit("research/learning.md", "image: learning.jpg", "image: missing.jpg")
    assert sandbox.build().has_error("learning.md", "image 'missing.jpg' was not found")


def test_research_image_is_processed_and_has_anchor(sandbox):
    result = sandbox.build()
    assert (sandbox.out / "images" / "research" / "learning.jpg").is_file()
    html = result.page("research/index.html")
    assert 'id="learning"' in html
    assert 'alt="Made-up line plot of three learning curves rising at different rates"' in html


def test_research_image_without_description_warns(sandbox):
    sandbox.edit("research/learning.md", "image_alt: Made-up line plot of three learning curves rising at different rates\n", "")
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("learning.md", "image_alt")


# ----- resources


def test_resource_paper_key_must_match_a_publication(sandbox):
    sandbox.edit("resources/context-data.md", "paper: student2024context", "paper: wrongkey")
    assert sandbox.build().has_error("context-data.md", "does not match any publication", "BibTeX key")


def test_resource_shows_linked_paper(sandbox):
    html = sandbox.build().page("resources/index.html")
    assert "Context effects in Bayesian choice" in html


def test_resource_links_need_label_and_url(sandbox):
    sandbox.write("resources/new.md", "---\ntitle: T\nlinks:\n  - {label: Code}\n---\n")
    assert sandbox.build().has_error("new.md", "links item 1", "label and a url")


# ----- teaching, join and stale pages


def test_stale_teaching_page_warns_but_builds(sandbox):
    sandbox.edit("teaching/psyc-50-decision-making.md", "updated: 2026-10", "updated: 2024-01")
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.has_warning("psyc-50-decision-making.md", "over a year ago")


def test_recent_page_does_not_warn(sandbox):
    assert sandbox.build(today=datetime.date(2027, 3, 1)).warnings == []


def test_stale_join_page_warns(sandbox):
    result = sandbox.build(today=datetime.date(2028, 1, 1))
    assert result.has_warning("join.md", "over a year ago")


def test_bad_month_format(sandbox):
    sandbox.edit("join.md", "updated: 2026-10", "updated: October")
    assert sandbox.build().has_error("join.md", "'updated' must look like 2026-10")


def test_recruiting_switch(sandbox):
    assert "currently recruiting" in sandbox.build().page("join/index.html")
    sandbox.edit("join.md", "recruiting: open", "recruiting: closed")
    assert "not currently recruiting" in sandbox.build().page("join/index.html")
    sandbox.edit("join.md", "recruiting: closed", "recruiting: maybe")
    assert sandbox.build().has_error("join.md", "'recruiting' must be one of: open, closed")


def test_teaching_needs_code_and_title(sandbox):
    sandbox.write("teaching/new.md", "---\ntitle: Only a title\n---\n")
    assert sandbox.build().has_error("new.md", "missing required field 'code'")
