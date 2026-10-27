#!/usr/bin/env python3
"""Build the CCNL website.

    python build.py                    build content/ into _site/
    python build.py --serve            build, then preview at http://localhost:8000
    python build.py --content sample_content    build the fake sample content instead

On GitHub the base path is set to /ccnl-website (the site lives at <org>.github.io/ccnl-website/).
"""

import argparse
import functools
import http.server
import sys
from pathlib import Path

from ccnl.build import build
from ccnl.problems import BuildFailed, Problems

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--content", default="content", help="content folder (default: content)")
    parser.add_argument("--out", default="_site", help="output folder (default: _site)")
    parser.add_argument("--base-path", default="", help="URL prefix, e.g. /ccnl-website (default: none)")
    parser.add_argument("--serve", action="store_true", help="after building, serve the site locally")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    problems = Problems()
    try:
        site = build(
            content_dir=ROOT / args.content,
            out_dir=ROOT / args.out,
            templates_dir=ROOT / "templates",
            static_dir=ROOT / "static",
            base_path=args.base_path,
            root=ROOT,
            problems=problems,
        )
    except BuildFailed:
        problems.report()
        return 1
    problems.report()
    print(
        f"Built {len(site['people'])} people, {len(site['publications'])} publications, "
        f"{len(site['research'])} research themes into {args.out}/"
    )

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / args.out))
        with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            print(f"Preview at http://localhost:{args.port}/  (Ctrl+C to stop)")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
