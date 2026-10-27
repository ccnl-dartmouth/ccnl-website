"""Whole-build behavior: output, atomic replacement, base path, links, and the command line."""

import importlib.util
import re
from pathlib import Path

from conftest import ROOT, TODAY, Sandbox, person_md

from ccnl.build import build
from ccnl.problems import Problems


def load_cli():
    spec = importlib.util.spec_from_file_location("ccnl_cli", ROOT / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ----- what gets built


def test_real_content_builds(tmp_path):
    """Guards the actual site content: if this fails, the next deploy would fail too."""
    problems = Problems()
    build(ROOT / "content", tmp_path / "site", ROOT / "templates", ROOT / "static", root=ROOT, today=TODAY, problems=problems)
    assert not problems.errors
    assert (tmp_path / "site" / "index.html").is_file()
    research = (tmp_path / "site" / "research" / "index.html").read_text()
    assert research.count('class="theme-fig"') == research.count('class="theme"') >= 1  # every theme has its image


def test_sample_content_is_clean(sandbox):
    result = sandbox.build()
    assert result.ok, result.errors
    assert result.warnings == []


def test_expected_pages_exist(sandbox):
    sandbox.build()
    for page in ("people", "publications", "research", "resources", "contact"):
        assert (sandbox.out / page / "index.html").is_file()
    assert (sandbox.out / "people" / "pat-investigator" / "index.html").is_file()
    assert (sandbox.out / "404.html").is_file()
    assert (sandbox.out / ".nojekyll").is_file()
    assert not (sandbox.out / "join").exists()  # Join lives on the Contact page
    assert not (sandbox.out / "teaching").exists()  # Teaching lives on the Resources page


def test_every_page_has_title_and_nav_and_no_template_leftovers(sandbox):
    sandbox.build()
    for page in sandbox.out.rglob("index.html"):
        html = page.read_text()
        assert '<html lang="en">' in html and 'class="skip-link"' in html and '<main id="main"' in html
        assert "<title>" in html and 'aria-label="Main"' in html
        assert "{{" not in html and "{%" not in html


def test_current_nav_item_is_marked(sandbox):
    assert 'href="/people/" aria-current="page"' in sandbox.build().page("people/index.html")


# ----- failures never damage the previous site


def test_failed_build_leaves_previous_site_untouched(sandbox):
    assert sandbox.build().ok
    before = (sandbox.out / "index.html").read_text()

    sandbox.remove("home.md")
    assert not sandbox.build().ok
    assert (sandbox.out / "index.html").read_text() == before
    assert not (sandbox.root / "_site.tmp").exists()


def test_failure_found_while_processing_images_also_keeps_previous_site(sandbox):
    assert sandbox.build().ok
    before = (sandbox.out / "index.html").read_text()

    sandbox.write("people/new-person.md", person_md())
    sandbox.write("images/new-person.jpg", b"garbage")  # only detected when images are processed
    assert not sandbox.build().ok
    assert (sandbox.out / "index.html").read_text() == before
    assert not (sandbox.root / "_site.tmp").exists()


def test_successful_build_replaces_old_output(sandbox):
    assert sandbox.build().ok
    stale = sandbox.out / "stale.html"
    stale.write_text("old")
    assert sandbox.build().ok
    assert not stale.exists()


def test_all_errors_are_reported_together(sandbox):
    sandbox.remove("home.md")
    sandbox.write("people/Bad_Name.md", "---\nname: X\n---\n")
    sandbox.write("publications/junk.bib", "nothing")
    assert len(sandbox.build().errors) >= 4


def test_missing_content_folder_is_an_error(tmp_path):
    sandbox = Sandbox(tmp_path)
    sandbox.dir = tmp_path / "does-not-exist"
    assert sandbox.build().has_error("content folder does not exist")


# ----- links


def test_base_path_prefixes_links_and_assets(sandbox):
    html = sandbox.build(base_path="/ccnl-website").page("index.html")
    assert 'href="/ccnl-website/people/"' in html
    assert 'href="/ccnl-website/static/style.css"' in html
    assert 'src="/ccnl-website/static/hero-default.svg"' in html


def test_without_base_path_links_start_at_root(sandbox):
    assert 'href="/people/"' in sandbox.build().page("index.html")


def test_every_internal_link_and_anchor_resolves(sandbox):
    assert sandbox.build(base_path="/ccnl-website").ok
    out = sandbox.out
    pattern = re.compile(r'(?:href|src)="(/ccnl-website/[^"]*)"')
    checked = 0
    for page in out.rglob("*.html"):
        for ref in pattern.findall(page.read_text()):
            path, _, fragment = ref.partition("#")
            path = path.removeprefix("/ccnl-website/")
            target = out / path / "index.html" if path == "" or path.endswith("/") else out / path
            assert target.is_file(), f"{page.relative_to(out)} links to missing {ref}"
            if fragment:
                assert f'id="{fragment}"' in target.read_text(), f"{page.relative_to(out)}: no #{fragment} in {target.relative_to(out)}"
            checked += 1
    assert checked > 50  # the loop really looked at the site


# ----- command line


def test_cli_exit_codes_and_messages(sandbox, capsys):
    cli = load_cli()
    out_dir = str(sandbox.root / "cli_site")
    assert cli.main(["--content", str(sandbox.dir), "--out", out_dir]) == 0
    assert (Path(out_dir) / "index.html").is_file()

    sandbox.remove("home.md")
    capsys.readouterr()
    assert cli.main(["--content", str(sandbox.dir), "--out", out_dir]) == 1
    output = capsys.readouterr().out
    assert "ERROR" in output and "home.md" in output and "was NOT updated" in output
