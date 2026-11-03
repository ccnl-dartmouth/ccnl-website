"""Publications without a year after the authors, and the automatic publication list on each profile page."""

import re

from conftest import person_md

from ccnl.content import person_names


def author_lines(html):
    return re.findall(r'<p class="pub-authors">(.*?)</p>', html, flags=re.S)


def test_author_lines_have_no_year_but_year_headings_remain(sandbox):
    html = sandbox.build().page("publications/index.html")
    lines = author_lines(html)
    assert len(lines) == 12
    assert not any(re.search(r"\(\d{4}\)", line) for line in lines)
    assert '<h2 class="year">2024</h2>' in html


# ----- profile pages


def test_profile_lists_every_paper_by_that_person(sandbox):
    result = sandbox.build()
    pat = next(p for p in result.site["people"] if p["slug"] == "pat-investigator")
    html = result.page("people/pat-investigator/index.html")
    assert 'id="publications"' in html
    assert len(pat["publications"]) == 12 and html.count('<li class="pub"') == 12
    assert "Publications <span class=\"count\">(12)</span>" in html


def test_profile_pages_style_authors_like_the_publications_page_and_repeat_the_legend(sandbox):
    html = sandbox.build().page("people/alex-postdoc/index.html")
    block = html.split('>Context effects in Bayesian choice</a>')[1].split("</li>")[0]
    assert '<span class="au au-member">Postdoc A<span class="sr-only"> (lab member' in block
    assert "au-pi" in block  # the PI is yellow here too, not only on the Publications page
    assert 'class="author-key' in html and "lab member" in html.split('class="author-key')[1].split("</p>")[0]


def test_profile_groups_preprints_and_years_under_one_publications_heading(sandbox):
    html = sandbox.build().page("people/alex-postdoc/index.html")
    assert "<h3>Preprints</h3>" in html and '<h3 class="year">2024</h3>' in html
    assert "<h2>Published papers</h2>" not in html
    assert html.index("<h2>Publications") < html.index("<h3>Preprints</h3>") < html.index('<h3 class="year">')


def test_profile_papers_are_newest_first(sandbox):
    html = sandbox.build().page("people/pat-investigator/index.html")
    years = [int(y) for y in re.findall(r'<h3 class="year">(\d{4})</h3>', html)]
    assert years == sorted(years, reverse=True)


def test_profile_entries_have_abstracts_links_and_thumbnails_like_the_main_page(sandbox):
    html = sandbox.build().page("people/pat-investigator/index.html")
    assert "<details" not in html and "pub-links" in html and 'class="pub-thumb"' in html
    assert "images/publications/student2024context.jpg" in html


def test_person_without_papers_has_no_publications_section(sandbox):
    sandbox.write("people/new-person.md", person_md(body=""))
    assert 'id="publications"' not in sandbox.build().page("people/new-person/index.html")


def test_a_different_first_initial_does_not_match(sandbox):
    sandbox.write("people/casey-investigator.md", person_md(name="Casey Investigator", body=""))  # not "Investigator P"
    result = sandbox.build()
    assert 'id="publications"' not in result.page("people/casey-investigator/index.html")


def test_collaborators_have_no_profile_page_even_with_papers(sandbox):
    sandbox.build()
    assert not (sandbox.out / "people" / "kim-collaborator").exists()


def test_person_names_forms():
    assert person_names("Michael (Chong) Wang") == ("wang", {"michael", "chong"})
    assert person_names("Jos\u00e9 P\u00e9rez") == ("perez", {"jose"})
    assert person_names("Shih-Wei Wu") == ("wu", {"shihwei"})
    assert person_names("Cher") == ("cher", set())
