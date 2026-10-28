"""Every paper gets its own page, built from the BibTeX file; the cards on the lists open it."""

from conftest import ROOT, bib, image_bytes


def paper_page(sandbox, name="new", **fields):
    sandbox.write(f"publications/{name}.bib", bib(name.replace("-", "") + "2024", **fields))
    result = sandbox.build()
    assert result.ok, result.errors
    return result.page(f"publications/{name}/index.html")


# ----- the pages exist and show the BibTeX

def test_every_paper_gets_a_page_named_after_its_bib_file(sandbox):
    result = sandbox.build()
    for pub in result.site["publications"]:
        assert (sandbox.out / "publications" / pub["slug"] / "index.html").is_file()
    page = result.page("publications/2024-student-context/index.html")
    assert "<h1>Context effects in Bayesian choice</h1>" in page and "Journal of Examples" in page
    assert 'href="/publications/"' in page  # back link


def test_page_shows_venue_date_citation_doi_and_bibtex(sandbox):
    page = paper_page(sandbox, month="nov", doi="10.1000/x.1", volume="4", number="2", pages="1--9")
    assert "Journal of Examples</em> 4(2), 1–9 &middot; Nov 2024" in page
    assert "Doe, J., &amp; Investigator, P. (2024). A title. Journal of Examples, 4(2), 1–9. https://doi.org/10.1000/x.1" in page
    assert '<a href="https://doi.org/10.1000/x.1">10.1000/x.1</a>' in page
    assert "@article{new2024," in page and "copy-bibtex" in page and "<summary>BibTeX</summary>" in page


def test_lab_member_authors_link_to_their_profile_and_others_do_not(sandbox):
    page = paper_page(sandbox)
    assert 'href="/people/pat-investigator/"' in page and "Investigator, P." in page
    assert "people/jane-doe" not in page and "Doe, J." in page


def test_author_roles_are_explained_only_when_present(sandbox):
    plain = paper_page(sandbox)
    assert 'class="author-key' not in plain
    roles = paper_page(sandbox, "roles", cofirst="Doe, Investigator", corresponding="Investigator")
    assert "co-first author</span>" in roles
    assert "au-corr" not in roles and "corresponding author</span>" not in roles  # no highlight or legend on the paper page


def test_corresponding_author_row_links_to_the_profile_after_the_ids(sandbox):
    page = paper_page(sandbox, "corr", corresponding="Investigator, Doe", doi="10.1000/x", pmid="123")
    assert page.index("<dt>PubMed ID</dt>") < page.index("<dt>Corresponding authors</dt>")
    assert 'Doe, J., <a href="/people/pat-investigator/">Investigator, P.</a></dd>' in page  # members link, others are plain text
    assert "data-user" not in page.split("<dt>Corresponding authors</dt>")[1].split("</dl>")[0]  # no email on the paper page


def test_paper_without_a_corresponding_author_has_no_row(sandbox):
    assert "Corresponding author" not in paper_page(sandbox, "none")


def test_no_related_papers_section(sandbox):
    sandbox.write("publications/one.bib", bib("one2024", title="First paper", keywords="alpha"))
    sandbox.write("publications/two.bib", bib("two2023", title="Second paper", year="2023", keywords="alpha"))
    assert "Related" not in sandbox.build().page("publications/one/index.html")


def test_page_carries_citation_metadata_for_search_engines(sandbox):
    page = paper_page(sandbox, doi="10.1000/x.1")
    assert '<meta name="citation_title" content="A title">' in page
    assert '<meta name="citation_author" content="Doe, J.">' in page
    assert '<meta name="citation_doi" content="10.1000/x.1">' in page and 'name="citation_journal_title"' in page


# ----- new fields

def test_month_is_optional_and_accepts_numbers_and_names(sandbox):
    assert "&middot; 2024<" in paper_page(sandbox, "a")
    assert "&middot; Mar 2024" in paper_page(sandbox, "b", month="3")
    assert "&middot; Sep 2024" in paper_page(sandbox, "c", month="September")


def test_bad_month_is_an_error_naming_the_file(sandbox):
    sandbox.write("publications/new.bib", bib(month="13"))
    assert sandbox.build().has_error("new.bib", "`month` must be a number from 1 to 12")


def test_pmid_adds_a_pubmed_link_and_must_be_a_number(sandbox):
    page = paper_page(sandbox, pmid="12345678")
    assert 'href="https://pubmed.ncbi.nlm.nih.gov/12345678/"' in page and "PubMed ID" in page
    sandbox.write("publications/bad.bib", bib("bad2024", pmid="PMC123"))
    assert sandbox.build().has_error("bad.bib", "`pmid` must be just the number")


def test_keywords_become_chips_that_search_the_publications_page(sandbox):
    page = paper_page(sandbox, keywords="decision making; learning, Learning")
    assert page.count('class="chips"') == 1
    assert '<a href="/publications/?q=decision%20making">decision making' in page and "?q=learning" in page
    assert page.count("?q=") == 2  # the repeat ("Learning") is dropped
    assert "<h2>Keywords</h2>" not in paper_page(sandbox, "none")


def test_more_link_fields_are_buttons_on_the_card_and_the_page(sandbox):
    page = paper_page(sandbox, preprint="https://example.org/p", video="https://example.org/v",
                      slides="https://example.org/s", poster="https://example.org/po")
    for label in ("Preprint", "Video", "Slides", "Poster"):
        assert f">{label}</a>" in page


def test_bib_file_name_must_be_url_safe(sandbox):
    sandbox.write("publications/Bad_Name.bib", bib())
    assert sandbox.build().has_error("Bad_Name.bib", "the file name must use only lowercase letters, digits and hyphens")


# ----- thumbnails and correspondence

def test_thumbnail_is_shown_beside_the_title_only_when_the_paper_has_one(sandbox):
    assert "paper-thumb" not in paper_page(sandbox, "plain")
    sandbox.write("images/with-image.jpg", image_bytes((800, 600)))
    page = paper_page(sandbox, "with-image")
    assert 'class="paper-thumb" src="/images/publications/withimage2024.jpg"' in page
    assert "paper-head has-thumb" in page


# ----- cards link to the page

def test_the_whole_card_opens_the_paper_page_and_small_links_stay_clickable(sandbox):
    result = sandbox.build()
    html = result.page("publications/index.html")
    assert '<a class="card-link" href="/publications/2024-student-context/">Context effects in Bayesian choice</a>' in html
    css = (sandbox.out / "static" / "style.css").read_text()
    assert ".pub-links a { position: relative; z-index: 1; }" in css
    assert ".pub-title a { color: inherit; text-decoration: none; }" in css


def test_search_script_reads_the_q_address_parameter_and_copy_button_exists():
    js = (ROOT / "static" / "site.js").read_text()
    assert "URLSearchParams(location.search).get('q')" in js and "navigator.clipboard" in js


# ----- the paper template and blank fields

TEMPLATE = (ROOT / "content" / "publications" / "_TEMPLATE.bib").read_text(encoding="utf-8")
OPTIONAL_FIELDS = ("month", "volume", "number", "pages", "doi", "pmid", "keywords", "abstract", "note", "pdf", "preprint", "si",
                   "data", "code", "video", "slides", "poster", "url", "cofirst", "corresponding", "status", "image")


def test_template_lists_every_field_the_site_understands():
    for field in ("author", "title", "journal", "year") + OPTIONAL_FIELDS:
        assert f"  {field} = {{}}," in TEMPLATE, field


def test_template_is_ignored_in_place_and_builds_once_copied_and_filled(sandbox):
    sandbox.write("publications/_TEMPLATE.bib", TEMPLATE)
    result = sandbox.build()
    assert result.ok and result.warnings == [] and not (sandbox.out / "publications" / "_TEMPLATE").exists()
    filled = (TEMPLATE.replace("author = {}", "author = {Doe, Jane}").replace("title = {}", "title = {Copied template}")
              .replace("journal = {}", "journal = {Journal of Examples}").replace("year = {}", "year = {2026}"))
    sandbox.write("publications/2026-doe-copied-template.bib", filled)
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    page = result.page("publications/2026-doe-copied-template/index.html")
    assert "Copied template" in page and "<h2>Keywords</h2>" not in page and "<h2>Abstract</h2>" not in page


def test_blank_fields_and_comments_are_left_out_of_the_bibtex_shown_on_the_page(sandbox):
    filled = TEMPLATE.replace("author = {}", "author = {Doe, Jane}").replace("title = {}", "title = {Shown}").replace(
        "journal = {}", "journal = {J}").replace("year = {}", "year = {2026}")
    sandbox.write("publications/shown.bib", filled)
    page = sandbox.build().page("publications/shown/index.html")
    block = page.split('<pre id="bibtex-text">')[1].split("</pre>")[0]
    assert block.startswith("@article{yourkey2026,") and "= {}" not in block and "%" not in block
    assert "title = {Shown}" in block


def test_every_real_paper_file_lists_all_the_optional_fields(sandbox=None):
    import re
    for path in (ROOT / "content" / "publications").glob("*.bib"):
        text = path.read_text(encoding="utf-8")
        assert all(re.search(rf"^\s*{f}\s*=", text, re.M) for f in OPTIONAL_FIELDS), path.name


def test_research_topic_links_to_papers_tagged_with_its_file_name(sandbox):
    sandbox.write("publications/tagged-a.bib", bib("a2024", title="Tagged A", keywords="reward; models"))
    sandbox.write("publications/tagged-b.bib", bib("b2024", title="Tagged B", keywords="Models, other"))
    sandbox.write("publications/untagged.bib", bib("c2024", title="Untagged", keywords="other"))
    page = sandbox.build().page("research/index.html")
    assert '<a href="/publications/?q=models">2 related papers' in page.replace("/ccnl-website", "")
    assert "?q=behavior" not in page  # a topic with no tagged paper shows no link
