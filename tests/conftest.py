"""Shared helpers: a throwaway copy of the sample content that each test can break in one specific way."""

import datetime
import io
import shutil
from pathlib import Path

import pytest
from PIL import Image

from ccnl.build import build
from ccnl.problems import BuildFailed, Problems

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date(2026, 10, 27)  # fixed so stale-page warnings do not depend on the real date


def image_bytes(size=(60, 40), fmt="JPEG", mode="RGB", color="red", **save_kwargs):
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, fmt, **save_kwargs)
    return buf.getvalue()


class Result:
    def __init__(self, site, problems, sandbox):
        self.site = site
        self.problems = problems
        self.sandbox = sandbox

    @property
    def ok(self):
        return self.site is not None and not self.problems.errors

    @property
    def errors(self):
        return self.problems.errors

    @property
    def warnings(self):
        return self.problems.warnings

    def has_error(self, *parts):
        return any(all(p in e for p in parts) for e in self.errors)

    def has_warning(self, *parts):
        return any(all(p in w for p in parts) for w in self.warnings)

    def page(self, rel):
        return (self.sandbox.out / rel).read_text(encoding="utf-8")


class Sandbox:
    """A copy of sample_content/ in a temp folder, plus helpers to edit it and build it."""

    def __init__(self, tmp_path):
        self.root = tmp_path
        self.dir = tmp_path / "content"
        self.out = tmp_path / "_site"
        shutil.copytree(ROOT / "sample_content", self.dir)

    def path(self, rel):
        return self.dir / rel

    def write(self, rel, content=""):
        path = self.path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def remove(self, rel):
        self.path(rel).unlink()

    def edit(self, rel, old, new):
        path = self.path(rel)
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{old!r} not found in {rel}"
        path.write_text(text.replace(old, new), encoding="utf-8")

    def build(self, today=TODAY, base_path=""):
        problems = Problems()
        try:
            site = build(
                self.dir,
                self.out,
                ROOT / "templates",
                ROOT / "static",
                base_path=base_path,
                root=self.root,
                today=today,
                problems=problems,
            )
        except BuildFailed:
            site = None
        return Result(site, problems, self)


@pytest.fixture
def sandbox(tmp_path):
    return Sandbox(tmp_path)


def person_md(body="Bio.\n", **over):
    fields = {"name": "New Person", "role": "grad", "status": "current", "start": 2023}
    fields.update(over)
    lines = [f"{k}: {v}" for k, v in fields.items() if v is not None]
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def bib(key="new2024", entry_type="article", **fields):
    base = {"author": "Doe, Jane and Investigator, Pat", "title": "A title", "journal": "Journal of Examples", "year": "2024"}
    base.update(fields)
    lines = [f"  {k} = {{{v}}}," for k, v in base.items() if v is not None]
    return f"@{entry_type}{{{key},\n" + "\n".join(lines) + "\n}\n"
