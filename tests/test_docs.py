"""The examples in the contributor guide must actually build, so the guide can't drift from the site."""

import re

from conftest import ROOT

# profile guide first: its markdown example must be the first one
GUIDE = "\n".join((ROOT / "docs" / "guides" / name).read_text() for name in (
    "UPDATE-PROFILE.md", "ADD-A-PAPER.md", "TROUBLESHOOTING.md", "START-HERE.md", "EDIT-SITE-TEXT.md"))


def fenced(language):
    return re.findall(rf"```{language}\n(.*?)```", GUIDE, flags=re.S)


def test_guide_has_the_expected_examples():
    assert len(fenced("markdown")) >= 1 and len(fenced("bibtex")) >= 1


def test_example_profile_builds_cleanly(sandbox):
    sandbox.write("people/jane-doe.md", fenced("markdown")[0])
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    html = result.page("people/jane-doe/index.html")
    assert "Jane Doe" in html and "I build computational models of learning" in html


def test_example_paper_builds_cleanly_and_uses_every_option_it_shows(sandbox):
    sandbox.write("people/jane-doe.md", fenced("markdown")[0])
    sandbox.write("publications/2026-doe-learning-under-uncertainty.bib", fenced("bibtex")[0])
    sandbox.write("people/alireza-soltani-example.md", "---\nname: Alireza Soltani\nrole: postdoc\nstatus: current\n---\n")
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    paper = next(p for p in result.site["publications"] if p["key"] == "doe2026learning")
    assert paper["abstract"] and [link["label"] for link in paper["links"]] == ["DOI", "PDF", "PubMed"]
    assert paper["keywords"] == ["learning", "uncertainty"] and paper["date"] == "Mar 2026"
    html = result.page("people/jane-doe/index.html")
    assert "Learning under uncertainty" in html  # the paper appears on Jane's page
    page = result.page("publications/2026-doe-learning-under-uncertainty/index.html")
    assert "<h2>Keywords</h2>" in page and "Mar 2026" in page  # and has a page of its own
    assert 'au au-cofirst' not in html  # profile pages only highlight their owner


def test_example_join_page_builds_cleanly_and_shows_its_openings(sandbox):
    example = next(block for block in fenced("yaml") if "openings:" in block)
    sandbox.write("join.md", example)
    result = sandbox.build()
    assert result.ok and result.warnings == [], result.errors + result.warnings
    html = result.page("contact/index.html")
    assert "<h3>Postdoctoral researcher</h3>" in html and "Apply by December 1, 2026" in html
    assert "<h3>Undergraduate research</h3>" in html and "General note shown under the openings." in html


def test_every_error_message_quoted_in_the_guide_still_exists_in_the_code():
    code = "\n".join(p.read_text() for p in (ROOT / "ccnl").glob("*.py"))
    quoted = [
        "the file name must use only lowercase letters, digits and hyphens",
        "unknown field",
        "missing required field",
        "is not valid YAML",
        "rename the image to",
        "contains GPS location data",
        "no valid BibTeX entry found",
        "entries. Use one .bib file per paper",
        "is also used in",
        "who is not among the authors",
        "do not go in this folder",
        "match any person, paper or research theme",
        "`month` must be a number from 1 to 12",
        "`pmid` must be just the number",
    ]
    for phrase in quoted:
        assert phrase in code, phrase
    for phrase in ("lowercase letters, digits and hyphens", "unknown field", "missing required field", "is not valid YAML",
                   "rename the image to", "contains GPS location data", "no valid BibTeX entry found", "is also used in",
                   "who is not among the authors", "do not go in this folder", "match any person, paper or research theme",
                   "`month` must be a number from 1 to 12", "`pmid` must be just the number"):
        assert phrase in GUIDE, phrase
