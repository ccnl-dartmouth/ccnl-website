# CCNL website

Source for the Computational & Cognitive Neuroscience Lab website (Dartmouth):
https://ccnl-dartmouth.github.io/ccnl-website/

## Lab members: add your own content

You can update your bio, photo, links and papers in your web browser, with nothing to install:

**[Add your own content: step-by-step guide](docs/ADD-YOUR-CONTENT.md)**

In short: your page is a file in `content/people/` (copy `_TEMPLATE.md` if you don't have one), your photo goes next to it
with the same name, and each paper is one `.bib` file in `content/publications/`. After you save ("commit") a change,
the site rebuilds in 2 to 3 minutes; the Actions tab shows a green check when it is live, or an error message naming
the file to fix. A broken change never takes the site down.

## For maintainers

| Document | What it covers |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | decisions, status and open items |
| [docs/STRUCTURE.md](docs/STRUCTURE.md) | the content model, repo layout, validation rules, visual design |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | alerts, uptime and link checks, GitHub settings |
| [docs/CREDITS.md](docs/CREDITS.md) | third-party assets and licenses |

### Build locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python build.py --content sample_content --serve   # preview the fake sample site at http://localhost:8000
.venv/bin/python build.py --serve                            # build and preview the real content/
.venv/bin/python -m pytest                                   # run the tests
```

A failed build prints every problem with the file name and how to fix it, and leaves the previous `_site/` untouched.
On GitHub, every push to `main` builds, tests and deploys the site; if the build fails nothing is deployed.
