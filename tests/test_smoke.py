"""Smoke tests: the real content and the sample content both build. Deeper tests come in phase 5."""

from pathlib import Path

import pytest

from ccnl.build import build
from ccnl.problems import Problems

ROOT = Path(__file__).resolve().parent.parent


def run_build(content, out):
    problems = Problems()
    site = build(ROOT / content, out, ROOT / "templates", ROOT / "static", root=ROOT, problems=problems)
    return site, problems


@pytest.mark.parametrize("content", ["content", "sample_content"])
def test_builds_without_errors(content, tmp_path):
    out = tmp_path / "site"
    site, problems = run_build(content, out)
    assert not problems.errors
    assert (out / "index.html").is_file()
    assert (out / "404.html").is_file()


def test_sample_content_has_expected_pages(tmp_path):
    out = tmp_path / "site"
    site, _ = run_build("sample_content", out)
    for page in ("people", "publications", "research", "join", "resources", "teaching", "contact"):
        assert (out / page / "index.html").is_file()
    assert (out / "people" / "pat-investigator" / "index.html").is_file()
    assert not (out / "people" / "kim-collaborator").exists()  # profile: false


def test_base_path_prefixes_links(tmp_path):
    out = tmp_path / "site"
    problems = Problems()
    build(ROOT / "sample_content", out, ROOT / "templates", ROOT / "static", base_path="/ccnl-website", root=ROOT, problems=problems)
    html = (out / "index.html").read_text()
    assert 'href="/ccnl-website/people/"' in html
    assert 'href="/ccnl-website/static/style.css"' in html
