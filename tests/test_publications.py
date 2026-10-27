from conftest import bib, image_bytes

from ccnl.content import parse_authors


def pub_titles(result):
    return [p["title"] for p in result.site["publications"]]


def test_valid_entry_is_added(sandbox):
    sandbox.write("publications/new.bib", bib())
    result = sandbox.build()
    assert result.ok, result.errors
    assert "A title" in pub_titles(result)
    assert "A title" in result.page("publications/index.html")


def test_file_without_entry_explains_format(sandbox):
    sandbox.write("publications/junk.bib", "this is not bibtex")
    result = sandbox.build()
    assert result.has_error("junk.bib", "no valid BibTeX entry", "@article{smith2024")


def test_empty_file(sandbox):
    sandbox.write("publications/empty.bib", "")
    assert sandbox.build().has_error("empty.bib", "no valid BibTeX entry")


def test_two_entries_in_one_file(sandbox):
    sandbox.write("publications/two.bib", bib("a2024") + bib("b2024"))
    assert sandbox.build().has_error("two.bib", "2 entries", "one .bib file per paper")


def test_missing_year(sandbox):
    sandbox.write("publications/new.bib", bib(year=None))
    assert sandbox.build().has_error("new.bib", "missing: year")


def test_missing_title_and_author_listed_together(sandbox):
    sandbox.write("publications/new.bib", bib(title=None, author=None))
    assert sandbox.build().has_error("new.bib", "missing: author, title")


def test_missing_venue(sandbox):
    sandbox.write("publications/new.bib", bib(journal=None))
    assert sandbox.build().has_error("new.bib", "needs a journal")


def test_bad_year(sandbox):
    sandbox.write("publications/new.bib", bib(year="in press"))
    assert sandbox.build().has_error("new.bib", "year must be four digits")


def test_duplicate_keys_across_files(sandbox):
    sandbox.write("publications/a.bib", bib("same2024"))
    sandbox.write("publications/b.bib", bib("same2024", title="Other"))
    result = sandbox.build()
    assert result.has_error("b.bib", "'same2024' is also used in", "a.bib")


def test_other_file_types_are_ignored_with_warning(sandbox):
    sandbox.write("publications/notes.txt", "x")
    result = sandbox.build()
    assert result.ok and result.has_warning("notes.txt", "Publications must be .bib")


# ----- authors and markers


def test_cofirst_name_must_be_an_author(sandbox):
    sandbox.write("publications/new.bib", bib(cofirst="Nobody"))
    assert sandbox.build().has_error("new.bib", "`cofirst` lists nobody", "not among the authors")


def test_corresponding_name_must_be_an_author(sandbox):
    sandbox.write("publications/new.bib", bib(corresponding="Typo"))
    assert sandbox.build().has_error("new.bib", "`corresponding`")


def test_markers_are_rendered_and_legend_shown(sandbox):
    sandbox.write("publications/new.bib", bib(cofirst="Doe, Investigator", corresponding="Investigator"))
    result = sandbox.build()
    assert result.ok, result.errors
    html = result.page("publications/index.html")
    assert "Doe J&deg;" in html or "Doe J°" in html
    assert "co-first authors" in html and "corresponding author" in html


def test_no_legend_without_markers(sandbox):
    sandbox.edit("publications/2024-student-context.bib", "  cofirst = {Student, Postdoc},\n", "")
    sandbox.edit("publications/2024-student-context.bib", "  corresponding = {Investigator},\n", "")
    sandbox.edit("publications/2025-postdoc-preprint.bib", "  corresponding = {Investigator},\n", "")
    result = sandbox.build()
    assert result.ok, result.errors
    assert "co-first authors" not in result.page("publications/index.html")


def test_parse_authors_formats():
    names = parse_authors("Wang, Xiao-Jing and Jane Q. Public and van der Berg, Anna and others")
    assert [(n["last"], n["initials"]) for n in names[:3]] == [("Wang", "XJ"), ("Public", "JQ"), ("van der Berg", "A")]
    assert names[-1]["etal"] is True


def test_latex_accents_and_braces_are_cleaned(sandbox):
    result = sandbox.build()
    titles = pub_titles(result)
    assert "A circuit model of adaptation, with naïve assumptions" in titles
    assert "Context effects in Bayesian choice" in titles  # {B} braces removed


def test_et_al_rendered(sandbox):
    assert "et al." in sandbox.build().page("publications/index.html")


# ----- grouping, links, extras


def test_preprints_are_separate_and_published_sorted_newest_first(sandbox):
    result = sandbox.build()
    html = result.page("publications/index.html")
    assert html.index("Preprints") < html.index("Published papers")
    years = [p["year"] for p in result.site["publications"]]
    assert years == sorted(years, reverse=True)
    assert [p["preprint"] for p in result.site["publications"]].count(True) == 1


def test_doi_becomes_link(sandbox):
    sandbox.write("publications/new.bib", bib(doi="10.1000/abc"))
    result = sandbox.build()
    pub = next(p for p in result.site["publications"] if p["key"] == "new2024")
    assert pub["links"][0] == {"label": "DOI", "url": "https://doi.org/10.1000/abc"}


def test_bad_link_url(sandbox):
    sandbox.write("publications/new.bib", bib(pdf="not a url"))
    assert sandbox.build().has_error("new.bib", "'pdf' must be a full web address")


def test_status_must_be_preprint(sandbox):
    sandbox.write("publications/new.bib", bib(status="submitted"))
    assert sandbox.build().has_error("new.bib", "`status` must be `preprint`")


def test_selected_must_be_boolean(sandbox):
    sandbox.write("publications/new.bib", bib(selected="maybe"))
    assert sandbox.build().has_error("new.bib", "`selected` must be true or false")


def test_selected_papers_appear_on_home(sandbox):
    result = sandbox.build()
    home = result.page("index.html")
    assert "Selected publications" in home
    assert "Context effects in Bayesian choice" in home
    assert "A range-normalization model" not in home  # not selected


def test_image_field_must_exist_with_exact_name(sandbox):
    sandbox.write("publications/new.bib", bib(image="cover.png"))
    assert sandbox.build().has_error("new.bib", "image 'cover.png' was not found")
    sandbox.write("publications/Cover.png", image_bytes(fmt="PNG"))
    assert sandbox.build().has_error("new.bib", "must match the file name exactly", "Cover.png")


def test_thumbnail_is_processed(sandbox):
    sandbox.write("publications/new.bib", bib(image="cover.png"))
    sandbox.write("publications/cover.png", image_bytes((2000, 1000), fmt="PNG"))
    result = sandbox.build()
    assert result.ok, result.errors
    assert (sandbox.out / "images" / "publications" / "new2024.png").is_file()


def test_html_in_title_is_escaped(sandbox):
    sandbox.write("publications/new.bib", bib(title="Tricky <script>alert(1)</script> title"))
    html = sandbox.build().page("publications/index.html")
    assert "<script>alert(1)" not in html
    assert "&lt;script&gt;" in html
