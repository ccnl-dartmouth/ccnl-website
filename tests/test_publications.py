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


def test_author_roles_are_styled_by_class_not_marked_with_symbols(sandbox):
    sandbox.write("publications/new.bib", bib(cofirst="Doe, Investigator", corresponding="Investigator"))
    result = sandbox.build()
    assert result.ok, result.errors
    block = result.page("publications/index.html").split("A title")[1].split("</li>")[0]
    # Doe is not in People: co-first only. Pat Investigator is a lab member, co-first and corresponding.
    assert '<span class="au au-cofirst">Doe J<span class="sr-only"> (co-first author)</span></span>' in block
    assert ('<span class="au au-member au-cofirst au-corr">Investigator P'
            '<span class="sr-only"> (lab member, co-first author, corresponding author)</span></span>') in block
    assert "&deg;" not in block and "\u00b0" not in block and "*" not in block


def test_corresponding_author_and_lab_member_styles_are_separate(sandbox):
    sandbox.write("publications/new.bib", bib(corresponding="Doe"))
    block = sandbox.build().page("publications/index.html").split("A title")[1].split("</li>")[0]
    assert '<span class="au au-corr">Doe J<span class="sr-only"> (corresponding author)</span></span>' in block
    assert '<span class="au au-member">Investigator P<span class="sr-only"> (lab member)</span></span>' in block


def test_authors_outside_the_lab_are_not_styled(sandbox):
    html = sandbox.build().page("publications/index.html")
    block = html.split("A range-normalization model")[1].split("</li>")[0]
    assert ", Outsider M, " in block  # plain text, no span
    assert "Collaborator K" in block and 'au-member' in block.split("Collaborator K")[0][-120:]


def test_legend_lists_the_styles_that_occur(sandbox):
    legend = sandbox.build().page("publications/index.html").split('class="author-key')[1].split("</p>")[0]
    assert "lab member" in legend and "co-first author" in legend and "corresponding author" in legend
    for name in ("2024-student-context", "2025-postdoc-preprint", "2012-investigator-range"):
        text = sandbox.path(f"publications/{name}.bib").read_text()
        text = "\n".join(line for line in text.splitlines() if not line.strip().startswith(("cofirst", "corresponding")))
        sandbox.write(f"publications/{name}.bib", text)
    legend = sandbox.build().page("publications/index.html").split('class="author-key')[1].split("</p>")[0]
    assert "lab member" in legend and "co-first" not in legend and "corresponding" not in legend


# ----- matching authors to the People page


def _people(*names):
    return [{"name": n} for n in names]


def test_lab_members_are_matched_by_last_name_and_first_initial():
    from ccnl.content import style_authors, parse_authors

    people = _people("Michael (Chong) Wang", "Jae Hyung Woo", "Shih-Wei Wu", "Jos\u00e9 P\u00e9rez", "Carl Harris")
    pub = {"authors": parse_authors("Wang, MC and Woo, JH and Wu, S-W and Perez, J and Harris, L and Harris, C and Smith, A")}
    style_authors([pub], people)
    flags = {a["last"] + " " + a["initials"]: a["member"] for a in pub["authors"]}
    assert flags == {"Wang MC": True, "Woo JH": True, "Wu SW": True, "Perez J": True, "Harris L": False, "Harris C": True, "Smith A": False}


def test_et_al_is_never_styled():
    from ccnl.content import style_authors, parse_authors

    pub = {"authors": parse_authors("Doe, J and others")}
    style_authors([pub], _people("Jane Doe"))
    assert pub["authors"][0]["member"] is True and "member" not in pub["authors"][1]


def test_every_publication_has_a_right_aligned_thumbnail_with_a_generic_fallback(sandbox):
    html = sandbox.build().page("publications/index.html")
    items = html.split('<li class="pub">')[1:]
    assert len(items) == 12
    for item in items:
        assert item.index('class="pub-body"') < item.index('class="pub-thumb"')  # text first, thumbnail after (right column)
        assert 'alt=""' in item.split('class="pub-thumb"')[1][:200]
    assert "images/publications/student2024context.jpg" in html
    assert html.count("static/pub-placeholder.svg") == 12 - 5  # sample has 5 papers with their own image


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
    assert [p["preprint"] for p in result.site["publications"]].count(True) == 2


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


def test_run_together_initials_are_kept_whole():
    names = parse_authors("Wang, MC and Woo, JH and Wang, Xiao-Jing and Public, Jane Q. and Wu, S-W and Soltani, A")
    assert [n["initials"] for n in names] == ["MC", "JH", "XJ", "JQ", "SW", "A"]
