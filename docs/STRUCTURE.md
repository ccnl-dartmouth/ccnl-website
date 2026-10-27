# Site structure (phase 3)

Content model, repo layout and validation rules. Revised after reviewing other labs' sites
(Niv/Princeton, Kable/Penn, Brown LNCC, Contextual Dynamics/Dartmouth, Gershman/Harvard, Murray/Yale).
The old WordPress site is not being recreated; we keep its core information in a modern layout.

## What is fixed and what is flexible

**Fixed (the machinery and the member recipes):**
- How a content type is defined: a folder of files + a schema + a template.
- The validation and image pipeline, the CI/deploy/alerts.
- The member-facing recipes: edit your bio, add a paper, add a photo. People memorize these;
  changing them later means retraining.
- The people and publication file formats (the two things most members touch).

**Flexible (change freely, cheap):**
- Which sections exist, their order, their layout and text (listed in `content/site.yaml`).
- Adding a new content type (new folder + schema entry + template; nothing existing changes).
- Research themes (one file each; add or remove at will).
- Adding optional fields. Renaming/removing a field needs a migration script, so avoid it.

## Sections (modeled on the Niv Lab layout; add/subtract later)

| Section | Source | Notes |
|---|---|---|
| Home | `home.md` | Centered hero card (lab name + affiliation), intro text, entry cards (Research, Publications, People, Contact) |
| About | `about.md` | Longer description, funding, affiliation |
| Research | `research/*.md` | One file per theme: title, text, optional image |
| People | `people/*.md` | Current and alumni, grouped by role; profile pages generated |
| Publications | `publications/*.bib` | Preprints + published, by year |
| Contact | `lab.yaml` + `join.md` | Address and email; the "Join us" section (recruiting banner + text per career stage) from `join.md` |
| Resources | `resources/*.md` + `teaching/*.md` | "Code and data" cards, then a "Teaching" section with the course cards (Teaching is not a separate page) |

Deferred (can be added later without touching the rest): Participate / Active Studies, Press,
Lab Photos. Dropped: News (stale since 2023; replaced by nothing for now).

## Repo layout

```
content/
  site.yaml                # navigation: ordered list of pages/sections, labels, URLs
  lab.yaml                 # lab name, tagline, address, contact, funders, social links
  home.md                  # hero statement and intro
  about.md
  join.md
  research/
    reinforcement-learning.md       # one file per theme (+ optional same-name image)
  people/
    jane-doe.md
    jane-doe.jpg                    # photo: same filename as the .md
  publications/
    2024-yazdanpanah-statistical-learning.bib   # one BibTeX entry per file
  resources/
    salience-choice.md
  teaching/
    psyc-50-02-decision-making.md
  images/                  # site-wide images (funder logos, banners); referenced from lab.yaml
sample_content/            # fake lab with every content type; used for previews and tests
templates/                 # Jinja2 HTML
static/                    # CSS, small JS
build.py                   # command-line entry point
ccnl/                      # the build: content.py (load + validate), images.py, build.py (render)
tests/
docs/
.github/workflows/
```

Rule of thumb for members: add or edit files named after yourself or your paper. Never edit
someone else's file, templates, or `build.py`.

## Data formats

### Navigation: `content/site.yaml`

```yaml
nav:
  - {label: Home, page: home}
  - {label: Research, page: research}
  - {label: People, page: people}
  - {label: Publications, page: publications}
  - {label: Resources, page: resources}
  - {label: Contact, page: contact}
```

Each `page` must refer to a known page; build fails on unknown names. Reordering = reordering lines.

### People: `content/people/<slug>.md`

```yaml
---
name: Jane Doe
role: grad            # pi | postdoc | grad | undergrad | collaborator
status: current       # current | alumni
start: 2022           # optional; start and end are the only date fields
end:                  # optional year; leave empty while current
degrees: B.Sc.        # optional
current_position:     # alumni: where they are now; collaborators: their institution
profile: true         # default: everyone except collaborators gets a profile page (minimal until
                      # they add a bio); collaborators are only listed. true/false overrides
links:                # all optional
  scholar: https://scholar.google.com/...
  orcid: 0000-0000-0000-0000
  github: janedoe
  website: https://...
  email: jane.doe@dartmouth.edu   # obfuscated by the build
---
Bio in Markdown. Optional "## Research" section.
```

- Photo: `<slug>.jpg|png|webp|heic` next to the `.md`; missing photo gets an initial in a circle. A photo that contains GPS location data triggers a warning (the original stays public in the repository).
- Collaborators are listed at the bottom of the People page as a compact list (name linked to their site,
  institution, any other links), without profile pages.
- `content/people/_TEMPLATE.md` is a commented example to copy when joining (files starting with `_` are ignored).
- People page, menu and profile URLs are generated from these files, so they cannot disagree.
- Moving to alumni = edit your own file (`status`, `end`, `current_position`).

### Publications: `content/publications/<anything>.bib`

One standard BibTeX entry per file (paste from Google Scholar or the journal). Optional extra fields:

| Field | Meaning |
|---|---|
| `pdf`, `si`, `data`, `code`, `url` | link buttons |
| `cofirst` | last names of co-first authors (shown in blue; no symbols) |
| `corresponding` | last names of corresponding authors |
| `status` | `preprint`, or omitted for published |
| `note` | short press/recognition note |
| `abstract` | shown in a collapsible "Abstract" section on the Publications page |
| `image` | optional thumbnail filename next to the `.bib`; papers without one get a generic filler (`static/pub-placeholder.svg`) |

### Research themes: `content/research/<slug>.md`

```yaml
---
title: Adaptive learning and decision making
order: 1                 # lower first
image: figure.png        # optional, same folder
image_alt: Diagram of ...  # describe the figure (screen readers); the build warns if missing
---
Short description in Markdown. Link to papers by BibTeX key if wanted.
```

### Resources: `content/resources/<slug>.md`

```yaml
---
title: Salience-driven value construction
paper: spitmaan2019salience      # optional BibTeX key; validated if present
links:
  - {label: Code, url: https://github.com/...}
  - {label: Data, url: https://...}
---
Short description in Markdown.
```

### Teaching: `content/teaching/<slug>.md`

```yaml
---
code: PSYC 50.02
title: Decision making
next_offering: Winter 2027      # free text, e.g. TBD
updated: 2026-10
---
Course description in Markdown.
```

### Join text (shown on the Contact page): `content/join.md`

```yaml
---
recruiting: closed        # open | closed: shows a banner; flip in one line
updated: 2026-10
---
Sections per career stage (postdoc, graduate, undergraduate) and how to contact the PI.
Can link to a Google Form or an email address.
```

### Home: `content/home.md`

```yaml
---
headline: Computational & Cognitive Neuroscience Lab   # optional; defaults to the lab name
hero_image: lab-group.jpg   # optional, a file in content/images/; default is a placeholder picture
hero_alt: Lab members at the 2026 retreat   # describe the photo; the build warns if missing
---
Intro text in Markdown.
```

The entry cards on Home (Research, Publications, People, Contact) appear only for pages listed in `site.yaml`.

### Lab-wide: `content/lab.yaml`, `about.md`

Edited rarely, by anyone.

## Validation (errors fail the build with a plain-language message naming the file)

Errors (build fails, last good site stays live):
- Required fields missing; `role`/`status` not in the allowed list; `end` missing for alumni;
  dates not parseable; unknown page in `site.yaml`.
- Filename not lowercase-with-hyphens; duplicate slugs; image filename case mismatch (`Photo.JPG` vs `photo.jpg`).
- BibTeX: parse failure (file and line), missing author/title/year/venue, duplicate keys,
  `cofirst`/`corresponding` names not matching an author, `paper:` key not found.
- Images that cannot be opened or larger than a hard cap (e.g. 25 MB).
- Malformed URLs.

Warnings (printed in the build log, build passes):
- No photo; `join.md` or `teaching/` entries with `updated` older than 12 months; very large images
  (resized automatically); alumni without a current position.

Images: the build resizes to web sizes, strips metadata (including GPS), converts HEIC.
A weekly scheduled link check (separate from the build) reports dead links without failing deploys.

## Decisions recorded

- One `.bib` file per paper (errors stay local to one file).
- Co-first / corresponding authors are shown by text color in the author list (blue, orange, purple for both) with bold weight, screen-reader text and a legend, not by the old ° and * symbols.
- Drop News. No selected-publications section on Home.
- Join is not a page; its text lives on the Contact page (`join.md`).
- No Research page of fixed length: themes are files, the count can change.
- Obfuscate email addresses in the build.
- Warn on stale pages (12 months).
- Recruiting is not done through the site yet; `join.md` has an open/closed switch for later.

## Visual design (decided Oct 2026)

- **Home:** photo hero with the lab name and affiliation in a solid green card centered on the image, intro text,
  four entry cards. The hero uses a generated placeholder (`static/hero-default.svg`) until the lab adds a real photo.
- **People:** photo grid by role (initial in a circle when there is no photo); alumni as a plain list.
  Profile page: details card (photo, role, years, links) beside the bio.
- **Publications:** semi-dense list by year; each entry has the BibTeX-derived text on the left (authors colored by
  role, title, venue, link buttons, collapsible abstract) and a right-aligned thumbnail (own image or generic filler).
- **Research:** one section per theme with a large figure alternating left/right (stacked on phones). The real
  site currently uses generated placeholder illustrations, to be replaced with real figures.
- **Header:** only a centered navigation bar (no lab name at the left); order Home, Research, People, Publications,
  Resources, Contact.
- **Footer:** lab name and affiliation at the left; small SVG logos at the right (institution from
  `institution_logo` in `lab.yaml`, funders from `funders[].logo`) on white chips so they work in dark mode; an optional
  `credit` line in `lab.yaml` (required for the CC BY-SA Dartmouth D-Pine logo).
- **Resources, Contact:** simple stacked entries; Resources also holds Teaching, Contact also holds the Join text.
- **Home hero:** the lab name in large type, then the department and "Dartmouth College" on separate lines; intro text centered.
- **Palette:** Dartmouth green `#00693e` (6.8:1 on white), ink `#1c1c1c`, amber `#f2a900` as decoration only;
  automatic dark mode following the system setting.
- **Fonts:** Source Serif 4 headings, Inter body, self-hosted in `static/fonts/` (SIL OFL licenses included),
  latin and latin-ext subsets.
- **Accessibility target:** WCAG 2.2 AA: skip link, landmarks, visible focus, contrast, alt text prompts,
  keyboard-operable abstract disclosure, reduced-motion friendly, usable at 200% zoom.
