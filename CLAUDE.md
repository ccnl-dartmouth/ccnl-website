# CCNL website

Static lab website (Computational & Cognitive Neuroscience Lab, Dartmouth), built with a small
custom Python script and deployed to GitHub Pages by GitHub Actions. Read `docs/maintainers/PLAN.md` first;
it holds the decisions, phases and open items.

## Principles

- Content is text, images and links only. Freeze the machinery (content-type mechanism, validation,
  image pipeline, CI) and the member recipes; keep sections, pages and layout flexible. See
  `docs/maintainers/STRUCTURE.md` for what is fixed and what is cheap to change.
- Lab members edit their own files in the GitHub web editor; they never install anything.
  Error messages from the build must name the file and say how to fix it in plain language.
- A failed build must not deploy; the last good site stays live.
- Few dependencies, all pinned in `requirements.txt`; CI uses the same Python version as local.
- The maintainer (Peter Duggins) is leaving eventually; favor simple code a postdoc can read.

## Conventions

- Python venv lives in `.venv` (not committed).
- Update `docs/maintainers/PLAN.md` checkboxes as steps finish.
