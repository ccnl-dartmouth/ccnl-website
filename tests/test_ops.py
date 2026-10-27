"""Tests for the alert issue text and the link checker (run against a local HTTP server, no internet)."""

import datetime
import http.server
import re
import threading
from pathlib import Path

import pytest

from ccnl import alerts, linkcheck

ENV = {
    "GITHUB_SERVER_URL": "https://github.com",
    "GITHUB_REPOSITORY": "ccnl-dartmouth/ccnl-website",
    "GITHUB_SHA": "abc123",
    "GITHUB_RUN_ID": "42",
    "GITHUB_ACTOR": "student1",
    "ALERT_MENTIONS": "@ccnl-dartmouth/lab-members",
}


# ----- alert issue body


def test_first_alert_mentions_only_the_person_who_pushed():
    body = alerts.build_body("The build failed.", log_text="ERROR  people/x.md: bad", env=ENV)
    assert "https://github.com/ccnl-dartmouth/ccnl-website/actions/runs/42" in body
    assert "https://github.com/ccnl-dartmouth/ccnl-website/commit/abc123" in body
    assert "@student1" in body
    assert "lab-members" not in body  # the team is only mentioned on escalation
    assert "ERROR  people/x.md: bad" in body
    assert "last good version" in body


def test_body_keeps_only_the_log_tail():
    log = "\n".join(f"line {i}" for i in range(200))
    body = alerts.build_body("x", log_text=log, env=ENV, max_lines=10)
    assert "line 199" in body and "line 190" in body and "line 189" not in body


def test_body_cannot_be_broken_by_backticks_in_log():
    body = alerts.build_body("x", log_text="oops ``` closes the fence", env=ENV)
    assert body.count("```") == 2


def test_body_does_not_mention_bots_and_works_without_a_log():
    env = {**ENV, "GITHUB_ACTOR": "github-actions[bot]"}
    body = alerts.build_body("Weekly check failed.", env=env)
    assert "@github-actions" not in body and "cc:" not in body
    assert "```" not in body


def test_body_includes_details_verbatim():
    body = alerts.build_body("x", details="## Dead links\n- http://dead.example", env=ENV)
    assert "## Dead links" in body


def test_cli_dry_run_prints_body(capsys, tmp_path):
    log = tmp_path / "ci.log"
    log.write_text("ERROR something\n")
    code = alerts.main(["open", "--label", "build-failure", "--title", "t", "--summary", "Broke.", "--log-file", str(log), "--dry-run"])
    assert code == 0
    assert "ERROR something" in capsys.readouterr().out


def test_open_alert_comments_on_existing_issue(monkeypatch):
    calls = []

    def fake_gh(*args):
        calls.append(args)
        return "7\n" if args[:2] == ("issue", "list") else ""

    monkeypatch.setattr(alerts, "gh", fake_gh)
    alerts.open_alert("build-failure", "title", "body")
    assert any(c[:3] == ("issue", "comment", "7") for c in calls)
    assert not any(c[:2] == ("issue", "create") for c in calls)  # no duplicate issue


def test_open_alert_creates_issue_when_none_open(monkeypatch):
    calls = []
    monkeypatch.setattr(alerts, "gh", lambda *a: calls.append(a) or "")
    alerts.open_alert("build-failure", "title", "body")
    assert any(c[:2] == ("issue", "create") for c in calls)
    assert any(c[:2] == ("label", "create") for c in calls)


def test_close_alerts_closes_every_open_issue(monkeypatch):
    calls = []

    def fake_gh(*args):
        calls.append(args)
        return "3 5\n" if args[:2] == ("issue", "list") else ""

    monkeypatch.setattr(alerts, "gh", fake_gh)
    alerts.close_alerts("build-failure", "Fixed")
    closed = [c[2] for c in calls if c[:2] == ("issue", "close")]
    assert closed == ["3", "5"]


# ----- escalation

NOW = datetime.datetime(2026, 11, 10, 12, 0, tzinfo=datetime.timezone.utc)


def issue(number, created, labels=()):
    return {"number": number, "createdAt": created, "labels": [{"name": n} for n in labels]}


def test_only_old_unescalated_issues_are_due():
    issues = [
        issue(1, "2026-11-10T08:00:00Z"),                       # 4 hours old: still quiet
        issue(2, "2026-11-06T12:00:00Z"),                       # 4 days old: due
        issue(3, "2026-11-01T12:00:00Z", labels=["escalated"]),  # already escalated
    ]
    due = alerts.due_for_escalation(issues, after_hours=72, now=NOW)
    assert [n for n, _ in due] == [2]


def test_boundary_is_inclusive():
    assert alerts.due_for_escalation([issue(1, "2026-11-07T12:00:00Z")], 72, NOW)  # exactly 72h
    assert not alerts.due_for_escalation([issue(1, "2026-11-07T12:00:01Z")], 72, NOW)


def test_mentions_come_from_named_env_vars():
    env = {"ALERT_MENTIONS_TEAM": "@org/team", "ALERT_MENTIONS_PI": " @pi ", "OTHER": "@no"}
    assert alerts.mentions_from_env(["ALERT_MENTIONS_TEAM"], env) == "@org/team"
    assert alerts.mentions_from_env(["ALERT_MENTIONS_TEAM", "ALERT_MENTIONS_PI"], env) == "@org/team @pi"
    assert alerts.mentions_from_env(["MISSING"], env) == ""


def test_escalation_comments_once_and_labels(monkeypatch):
    calls = []

    def fake_gh(*args):
        calls.append(args)
        if args[:2] == ("issue", "list"):
            return '[{"number": 9, "createdAt": "2026-11-01T00:00:00Z", "labels": []}]'
        return ""

    monkeypatch.setattr(alerts, "gh", fake_gh)
    done = alerts.escalate_alerts("build-failure", 72, "@org/team", "Still broken.", now=NOW)
    assert done == [9]
    comment = next(c for c in calls if c[:2] == ("issue", "comment"))
    assert "@org/team" in comment[-1] and "Still broken." in comment[-1]
    assert any(c[:2] == ("issue", "edit") and "escalated" in c for c in calls)


def test_escalation_does_nothing_when_nothing_is_due(monkeypatch):
    calls = []
    monkeypatch.setattr(alerts, "gh", lambda *a: calls.append(a) or "[]")
    assert alerts.escalate_alerts("site-down", 12, "@pi", "x", now=NOW) == []
    assert not any(c[:2] in (("issue", "comment"), ("label", "create")) for c in calls)


def test_cli_without_configured_mentions_is_a_noop(monkeypatch, capsys):
    monkeypatch.delenv("ALERT_MENTIONS_TEAM", raising=False)
    monkeypatch.setattr(alerts, "gh", lambda *a: pytest.fail("gh must not be called"))
    code = alerts.main(["escalate", "--label", "x", "--after-hours", "1", "--mentions-env", "ALERT_MENTIONS_TEAM", "--message", "m"])
    assert code == 0
    assert "nobody to escalate to" in capsys.readouterr().out


# ----- link checker


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, code, headers=None):
        self.send_response(code)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def do_HEAD(self):
        if self.path == "/nohead":
            return self.respond(405)
        self.route()

    def do_GET(self):
        self.route()

    def route(self):
        table = {"/ok": 200, "/missing": 404, "/gone": 410, "/blocked": 403, "/limited": 429}
        if self.path == "/redirect":
            return self.respond(301, {"Location": "/ok"})
        if self.path in ("/nohead",):
            return self.respond(200)
        self.respond(table.get(self.path, 404))


@pytest.fixture
def server():
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def make_site(tmp_path, base, paths):
    site = tmp_path / "site"
    site.mkdir()
    links = "".join(f'<a href="{base}{p}">x</a>' for p in paths)
    (site / "index.html").write_text(
        f'<html><body>{links}<a href="mailto:a@b.org">m</a><a href="/people/">internal</a><a href="#top">t</a></body></html>'
    )
    (site / "sub").mkdir()
    (site / "sub" / "index.html").write_text(f'<a href="{base}/ok">again</a>')
    return site


def test_extract_ignores_mailto_internal_and_anchors(tmp_path):
    site = make_site(tmp_path, "http://example.test", ["/a"])
    links = linkcheck.extract_external_links(site)
    assert set(links) == {"http://example.test/a", "http://example.test/ok"}  # /ok comes from the sub page


def test_extract_lists_every_page_using_a_link(tmp_path, server):
    site = make_site(tmp_path, server, ["/ok"])
    links = linkcheck.extract_external_links(site)
    assert links[f"{server}/ok"] == ["index.html", "sub/index.html"]


@pytest.mark.parametrize(
    "path, kind",
    [("/ok", "ok"), ("/redirect", "ok"), ("/nohead", "ok"), ("/missing", "dead"), ("/gone", "dead"), ("/blocked", "soft"), ("/limited", "soft")],
)
def test_classification_against_local_server(server, path, kind):
    assert linkcheck.check_url(server + path, timeout=5, retries=0)[0] == kind


def test_refused_connection_is_dead():
    kind, detail = linkcheck.check_url("http://127.0.0.1:9/", timeout=3, retries=0)
    assert kind == "dead" and "refused" in detail


def test_cli_exit_code_and_report(tmp_path, server, capsys):
    site = make_site(tmp_path, server, ["/ok", "/missing", "/blocked"])
    report = tmp_path / "links.md"
    code = linkcheck.main(["--site", str(site), "--report", str(report), "--timeout", "5"])
    text = report.read_text()
    assert code == 1
    assert f"{server}/missing" in text and "HTTP 404" in text and "index.html" in text
    assert "Could not verify" in text and f"{server}/blocked" in text
    dead_section = text.split("## Dead links")[1].split("<details>")[0]
    assert f"{server}/ok" not in dead_section and f"{server}/blocked" not in dead_section


def test_cli_passes_when_only_soft_failures(tmp_path, server):
    site = make_site(tmp_path, server, ["/ok", "/blocked"])
    code = linkcheck.main(["--site", str(site), "--report", str(tmp_path / "r.md"), "--timeout", "5"])
    assert code == 0


# ----- internal links in the built site


def test_every_internal_link_and_anchor_resolves(sandbox):
    result = sandbox.build(base_path="/ccnl-website")
    assert result.ok, result.errors
    out = sandbox.out
    pattern = re.compile(r'(?:href|src)="(/ccnl-website/[^"]*)"')
    checked = 0
    for page in out.rglob("*.html"):
        for ref in pattern.findall(page.read_text()):
            path, _, fragment = ref.partition("#")
            path = path.split("?")[0].removeprefix("/ccnl-website/")
            target = out / path
            if path == "" or path.endswith("/"):
                target = out / path / "index.html"
            assert target.is_file(), f"{page.relative_to(out)} links to missing {ref}"
            if fragment:
                assert f'id="{fragment}"' in target.read_text(), f"{page.relative_to(out)}: no #{fragment} in {target.relative_to(out)}"
            checked += 1
    assert checked > 50


def test_workflow_files_are_valid_yaml_with_expected_triggers():
    import yaml

    root = Path(__file__).resolve().parent.parent / ".github" / "workflows"
    for name in ("deploy.yml", "links.yml", "uptime.yml", "escalate.yml"):
        data = yaml.safe_load((root / name).read_text())
        assert "jobs" in data
        assert "on" in data or True in data  # PyYAML reads the key `on` as boolean True
    deploy = yaml.safe_load((root / "deploy.yml").read_text())
    assert deploy["permissions"]["issues"] == "write"
