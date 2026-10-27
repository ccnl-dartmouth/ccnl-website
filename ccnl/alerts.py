"""Open and close GitHub issues from CI so failures reach people by email.

GitHub emails everyone mentioned in (or watching) a new issue, so an issue is a zero-secret way to
alert the lab. Issues for one problem are not duplicated: a repeat failure adds a comment, and the
issue closes itself when things work again. Uses the `gh` CLI that GitHub's runners provide.

    python3 -m ccnl.alerts open  --label build-failure --title "..." --summary "..." --log-file ci.log
    python3 -m ccnl.alerts close --label build-failure --comment "Fixed."
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

LABEL_COLOR = "D73A4A"
HELP_TEXT = (
    "**What to do:** read the message below. It names the file and says how to fix it. "
    "Edit that file on GitHub and commit. The website keeps showing the last good version "
    "until the build passes again. This issue closes itself when it does."
)


def build_body(summary, log_text=None, details=None, env=None, max_lines=60):
    env = os.environ if env is None else env
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    repo = env.get("GITHUB_REPOSITORY", "")
    lines = [summary, ""]
    sha, run_id, actor = env.get("GITHUB_SHA"), env.get("GITHUB_RUN_ID"), env.get("GITHUB_ACTOR", "")
    if sha and repo:
        who = f" (pushed by @{actor})" if actor and not actor.endswith("[bot]") else ""
        lines.append(f"- Commit: {server}/{repo}/commit/{sha}{who}")
    if run_id and repo:
        lines.append(f"- Run: {server}/{repo}/actions/runs/{run_id}")
    mentions = " ".join(m for m in [f"@{actor}" if actor and not actor.endswith("[bot]") else "", env.get("ALERT_MENTIONS", "")] if m)
    if mentions:
        lines.append(f"- cc: {mentions}")
    lines += ["", HELP_TEXT, ""]
    if details:
        lines += [details.strip(), ""]
    if log_text:
        tail = log_text.strip().splitlines()[-max_lines:]
        text = "\n".join(tail).replace("```", "'''")
        lines += ["```text", text, "```"]
    return "\n".join(lines).strip() + "\n"


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def open_issues(label):
    out = gh("issue", "list", "--label", label, "--state", "open", "--json", "number", "--jq", ".[].number")
    return [int(n) for n in out.split()]


def open_alert(label, title, body):
    gh("label", "create", label, "--color", LABEL_COLOR, "--description", "Opened automatically by CI", "--force")
    existing = open_issues(label)
    if existing:
        gh("issue", "comment", str(existing[0]), "--body", "Still failing.\n\n" + body)
        return existing[0]
    out = gh("issue", "create", "--title", title, "--body", body, "--label", label)
    return out.strip()


def close_alerts(label, comment):
    for number in open_issues(label):
        gh("issue", "close", str(number), "--comment", comment)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    op = sub.add_parser("open")
    op.add_argument("--label", required=True)
    op.add_argument("--title", required=True)
    op.add_argument("--summary", required=True)
    op.add_argument("--log-file")
    op.add_argument("--details-file")
    op.add_argument("--dry-run", action="store_true", help="print the issue body instead of creating it")
    cl = sub.add_parser("close")
    cl.add_argument("--label", required=True)
    cl.add_argument("--comment", required=True)
    args = parser.parse_args(argv)

    if args.command == "open":
        log = Path(args.log_file).read_text(errors="replace") if args.log_file and Path(args.log_file).is_file() else None
        details = Path(args.details_file).read_text(errors="replace") if args.details_file and Path(args.details_file).is_file() else None
        body = build_body(args.summary, log, details)
        if args.dry_run:
            print(body)
            return 0
        print("Alert issue:", open_alert(args.label, args.title, body))
    else:
        close_alerts(args.label, args.comment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
