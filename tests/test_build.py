import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_cli():
    spec = importlib.util.spec_from_file_location("ccnl_cli", ROOT / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failed_build_leaves_previous_site_untouched(sandbox):
    assert sandbox.build().ok
    marker = sandbox.out / "index.html"
    before = marker.read_text()

    sandbox.remove("home.md")
    result = sandbox.build()
    assert not result.ok
    assert marker.read_text() == before
    assert not (sandbox.root / "_site.tmp").exists()


def test_failed_image_stage_also_keeps_previous_site(sandbox):
    from conftest import person_md

    assert sandbox.build().ok
    before = (sandbox.out / "index.html").read_text()
    sandbox.write("people/new-person.md", person_md())
    sandbox.write("people/new-person.jpg", b"garbage")  # only detected when images are processed
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
    result = sandbox.build()
    assert len(result.errors) >= 4


def test_base_path_prefixes_links_and_assets(sandbox):
    result = sandbox.build(base_path="/ccnl-website")
    html = result.page("index.html")
    assert 'href="/ccnl-website/people/"' in html
    assert 'href="/ccnl-website/static/style.css"' in html
    assert 'src="/ccnl-website/images/research/learning.jpg"' in html


def test_no_base_path_links_start_at_root(sandbox):
    html = sandbox.build().page("index.html")
    assert 'href="/people/"' in html


def test_404_and_nojekyll_exist(sandbox):
    sandbox.build()
    assert (sandbox.out / "404.html").is_file()
    assert (sandbox.out / ".nojekyll").is_file()


def test_every_page_has_title_nav_and_no_unrendered_templates(sandbox):
    sandbox.build()
    for page in sandbox.out.rglob("index.html"):
        html = page.read_text()
        assert "<title>" in html and 'aria-label="Main"' in html
        assert "{{" not in html and "{%" not in html


def test_nav_marks_current_page(sandbox):
    html = sandbox.build().page("people/index.html")
    assert 'href="/people/" aria-current="page"' in html


def test_cli_exit_codes_and_messages(sandbox, capsys):
    cli = load_cli()
    ok = cli.main(["--content", str(sandbox.dir), "--out", str(sandbox.root / "cli_site")])
    assert ok == 0
    assert (sandbox.root / "cli_site" / "index.html").is_file()

    sandbox.remove("home.md")
    capsys.readouterr()
    bad = cli.main(["--content", str(sandbox.dir), "--out", str(sandbox.root / "cli_site")])
    out = capsys.readouterr().out
    assert bad == 1
    assert "ERROR" in out and "home.md" in out and "was NOT updated" in out
