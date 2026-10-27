"""Check the external links in a built site and write a report.

Only links that are definitely dead (404/410, unknown host, refused connection, repeated 5xx) count as
failures. Sites that block bots (403, 429, LinkedIn's 999) and timeouts are listed as "could not verify"
and never fail the check, so the weekly report stays quiet unless something is really broken.

    python3 -m ccnl.linkcheck --site _site --report links.md
"""

import argparse
import socket
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

USER_AGENT = "Mozilla/5.0 (compatible; ccnl-website-link-check)"
SOFT_STATUSES = {401, 403, 405, 406, 429, 451, 999}
DEAD_STATUSES = {404, 410}


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.urls.append(href.strip())


def extract_external_links(site_dir):
    """Map external URL -> sorted list of pages (relative to site_dir) that link to it."""
    found = {}
    site_dir = Path(site_dir)
    for page in sorted(site_dir.rglob("*.html")):
        parser = _Links()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for url in parser.urls:
            if urlsplit(url).scheme in ("http", "https"):
                found.setdefault(url, set()).add(str(page.relative_to(site_dir)))
    return {url: sorted(pages) for url, pages in found.items()}


def classify(status):
    if status is None:
        return "soft"
    if 200 <= status < 400:
        return "ok"
    if status in DEAD_STATUSES or status >= 500:
        return "dead"
    return "soft"


def _request(url, method, timeout):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status


def _attempt(url, timeout):
    """One try at a URL: returns (kind, detail)."""
    for method in ("HEAD", "GET"):  # some servers mishandle HEAD, so confirm a failure with GET
        try:
            status = _request(url, method, timeout)
            return classify(status), f"HTTP {status}"
        except urllib.error.HTTPError as exc:
            kind, detail = classify(exc.code), f"HTTP {exc.code}"
            if method == "HEAD" and kind != "ok":
                continue
            return kind, detail
        except (socket.timeout, TimeoutError):
            return "soft", "timed out"
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, socket.gaierror):
                return "dead", "host not found"
            if isinstance(exc.reason, ConnectionRefusedError):
                return "dead", "connection refused"
            return "soft", str(exc.reason)
        except Exception as exc:  # odd SSL/protocol problems are not proof that the link is dead
            return "soft", exc.__class__.__name__
    return "soft", "no answer"


def check_url(url, timeout=15, retries=2, pause=2):
    """Return (kind, detail) where kind is 'ok', 'dead' or 'soft'. Transient-looking failures are retried."""
    for attempt in range(retries + 1):
        kind, detail = _attempt(url, timeout)
        if kind != "dead" or detail in ("HTTP 404", "HTTP 410") or attempt == retries:
            return kind, detail
        time.sleep(pause)
    return kind, detail


def run_checks(links, timeout=15, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda u: (u, check_url(u, timeout)), links))
    return {url: result for url, result in results}


def format_report(results, links):
    dead = {u: r for u, r in results.items() if r[0] == "dead"}
    soft = {u: r for u, r in results.items() if r[0] == "soft"}
    lines = [f"Checked {len(results)} external links: {len(results) - len(dead) - len(soft)} fine, "
             f"{len(dead)} dead, {len(soft)} could not be verified.", ""]
    if dead:
        lines.append("## Dead links")
        lines.append("Fix or remove these in the file that contains them (the page is listed after each link).")
        lines.append("")
        for url, (_, detail) in sorted(dead.items()):
            lines.append(f"- {url}: {detail}")
            lines.append(f"  - on: {', '.join(links[url])}")
        lines.append("")
    if soft:
        lines.append("<details><summary>Could not verify (usually sites that block automated checks)</summary>")
        lines.append("")
        for url, (_, detail) in sorted(soft.items()):
            lines.append(f"- {url}: {detail}")
        lines += ["", "</details>"]
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", default="_site")
    parser.add_argument("--report", default="links.md")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args(argv)

    links = extract_external_links(args.site)
    results = run_checks(list(links), timeout=args.timeout)
    report = format_report(results, links)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 1 if any(kind == "dead" for kind, _ in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
