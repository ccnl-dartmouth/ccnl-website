# CCNL website

Source for the Computational & Cognitive Neuroscience Lab website (Dartmouth).

Work in progress. See `docs/PLAN.md` for the plan and `docs/STRUCTURE.md` for the content model.
Instructions for lab members will go here.

## Build locally (maintainers)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python build.py --content sample_content --serve   # preview the fake sample site at http://localhost:8000
.venv/bin/python build.py                                    # build the real content/ into _site/
.venv/bin/python -m pytest                                   # run the tests
```

A failed build prints every problem with the file name and how to fix it, and leaves the previous
`_site/` untouched.
