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
| Contact | `lab.yaml` + `join.md` | Address and email; the "Join us" block (a card per open position, or a "not currently recruiting" line, plus a general note) from `join.md` |
| Resources | `resources/*.md` + `teaching/*.md` | collapsible "Code and data" and "Teaching" sections (closed by default, with counts; open automatically from a `#teaching` or `#code-data` link), each holding cards (Teaching is not a separate page) |

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
  images/                  # ALL pictures: photos, thumbnails, research figures (paired by name), logos, hero
templates/                 # Jinja2 HTML
static/                    # CSS, small JS
build.py                   # command-line entry point
ccnl/                      # the build: content.py (load + validate), images.py, build.py (render)
tests/
  fixture_lab/            # fake lab with every content type; the tests copy it and break it on purpose
docs/
  guides/                 # for lab members: START-HERE (with the where-does-it-come-from table), profile, papers, site text, troubleshooting
  maintainers/            # PLAN, STRUCTURE, OPERATIONS, CREDITS
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

- Photo: `content/images/<slug>.jpg|png|webp|heic` (same name as the `.md`); missing photo gets the person's first and last initials (e.g. MW) in a square. A photo that contains GPS location data triggers a warning (the original stays public in the repository).
- A profile page also lists the person's papers automatically (matched from the BibTeX author names by last name
  and first initial), grouped like the main Publications page; only the page's owner is highlighted (bold blue).
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
| `cofirst` | last names of co-first authors (shown in purple; no symbols) |
| `corresponding` | last names of corresponding authors |
| `status` | `preprint`, or omitted for published |
| `note` | short press/recognition note |
| `abstract` | shown in a collapsible "Abstract" section on the Publications page |
| `image` | optional: a file in `content/images/` other than the one named like the `.bib` file (see "Images" below); papers without a thumbnail get a generic filler (`static/pub-placeholder.svg`) |

### Research themes: `content/research/<slug>.md`

```yaml
---
title: Adaptive learning and decision making
order: 1                 # lower first
image_alt: Diagram of ...  # describe the figure (screen readers); the build warns if missing
# The figure is content/images/<this file's name>.jpg; an optional `image: other.jpg` line names a different file there.
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
updated: 2026-10
openings:                 # only what is open now; none (or `openings: []`) shows "not currently recruiting"
  - title: Postdoctoral researcher
    text: One or two sentences.
    deadline: 2026-12-01  # optional date; shown as "Apply by December 1, 2026"
    link: https://...     # optional, https only
---
General note shown under the openings (how to get in touch, etc.).
```

Each opening becomes a small card in the "Join us" block. The old `recruiting: open|closed` switch was removed (it is an error now): an empty list already means closed.

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
- Author styles in the Publications list (no ° or * symbols): lab members (anyone on the People page, matched by last name + first initial) are bold blue; co-first authors are purple; corresponding authors get a yellow highlight. Styles combine. Screen readers hear the roles, and a legend explains the styles.
- Drop News. No selected-publications section on Home.
- Join is not a page; its text lives on the Contact page (`join.md`).
- No Research page of fixed length: themes are files, the count can change.
- Obfuscate email addresses in the build.
- Warn on stale pages (12 months).
- Recruiting is not done through the site yet; `join.md` lists openings (an empty list means closed).

## Visual design (decided Oct 2026)

- **Home:** photo hero with the lab name and affiliation in a solid green card centered on the image, intro text,
  four entry cards. The hero uses a generated placeholder (`static/hero-default.svg`) until the lab adds a real photo.
- **People:** current groups (PI, postdocs, grad students, undergraduates) sit side by side while they fit and
  wrap onto new rows as they fill up; every listing is a fixed-size, fully clickable card (photo cards with first and last initials when there is no photo; compact text cards for alumni and collaborators; cards show role and affiliation, not years: the affiliation is `current_position` if set, otherwise the lab's institution for current members; years stay on the profile page, so rows align when fields are missing and no separator lines are needed); alumni in subsections by role (postdoctoral scholars, graduate students, undergraduates, in that order; empty ones are left out).
  Profile page: details card (photo, role, years, links) beside the bio.
- **Publications:** semi-dense list by year; each entry has the BibTeX-derived text on the left (authors styled by
  role, title, venue, link buttons; no year after the authors since the list is grouped by year; the abstract is on the paper's own page) and a right-aligned thumbnail (own image or generic filler).
- **Page titles:** Research, People, Publications, Resources and Contact start with a centered serif title on a 3 px
  amber line that spans the content area (class `page-title`; the text sits on top of the line with the page
  background behind it).
- **Research:** one section per theme: an abstract-style paragraph (block-justified from 56 rem up, left-aligned on
  narrower screens, with the "N related papers" link ending the paragraph) beside a figure that alternates left/right
  (stacked below 56 rem). Titles use a fluid size so they stay on one line. The four figures are generated schematics
  (`scripts/make_uncertainty_and_change_image.py`, `make_complex_environments_image.py`,
  `make_attention_bias_decision_making_image.py`, `make_neural_synaptic_mechanisms_image.py`; Pillow only, fixed
  seed, 1600x1000 PNG written to `content/images/<topic>.png`). To replace one with a real figure, delete the
  generated PNG and upload the new file under the same name (the build refuses two images with the same name).
- **Header:** only a centered navigation bar (no lab name at the left); order Home, Research, People, Publications,
  Resources, Contact.
- **Footer:** lab name and affiliation at the left; small SVG logos at the right (institution from
  `institution_logo` in `lab.yaml`, funders from `funders[].logo`) on white chips so they work in dark mode; an optional
  `credit` line in `lab.yaml` (required for the CC BY-SA Dartmouth D-Pine logo).
- **Resources:** simple stacked entries; also holds Teaching.
- **Contact:** two columns (stacked below 44 rem): contact details on the left, "Join us" openings (cards) on the right.
- **Home hero:** the lab name in large type, then the department and "Dartmouth College" on separate lines; intro text centered.
- **Palette:** Dartmouth green `#00693e` (6.8:1 on white), ink `#1c1c1c`, amber `#f2a900` as decoration only;
  automatic dark mode following the system setting.
- **Fonts:** Source Serif 4 headings, Inter body, self-hosted in `static/fonts/` (SIL OFL licenses included),
  latin and latin-ext subsets.
- **Accessibility target:** WCAG 2.2 AA: skip link, landmarks, visible focus, contrast, alt text prompts,
  keyboard-operable abstract disclosure, reduced-motion friendly, usable at 200% zoom.

## Images: one folder, paired by name (decided Oct 2026)

Every picture goes directly in `content/images/` (no subfolders) and is paired with its page or paper **by name**:

| Picture | File name | Pairs with |
|---|---|---|
| Profile photo | `content/images/jane-doe.jpg` | `content/people/jane-doe.md` |
| Paper thumbnail | `content/images/2026-doe-paper.jpg` | `content/publications/2026-doe-paper.bib` |
| Research figure | `content/images/uncertainty-and-change.png` | `content/research/uncertainty-and-change.md` |
| Logos, hero photo | any name | named in `lab.yaml` / `home.md` |

- No `image:` line is needed when the names match. For papers and research themes an optional `image` line names
  any file in `content/images/` instead (for example one figure shared by several papers, or a differently named file).
- Names are what tell the kinds apart: people are `first-last`, papers start with the year, research themes are topic
  words. If one name is used by two kinds of file and a picture has that name, the build stops (the picture cannot be
  paired); without such a picture there is no problem.
- Reported mistakes: wrong capitals (error), two files with the same name (error), a name shared by two kinds (error),
  an image that matches nothing and is not named in `lab.yaml`/`home.md`/an `image` line (warning, not shown), and an
  image left in `content/people/`, `content/publications/`, `content/research/` and the other text folders (warning,
  not used).
- Only logos and the hero photo are published as "site" images (`images/site/`); photos, thumbnails and figures are
  resized and published with their page. The original files in the repository are public, so remove GPS data first.
- One folder means one upload page to remember and no near-identical `people` folders to confuse; the cost is one long
  alphabetical list (GitHub's file finder, key `t`, finds a file by name).

- Publications are bordered cards with a minimum height (text left, thumbnail right); unlike people cards they are not wholly clickable, because each has several links and an abstract toggle.
- Publications page: one search box (needs JavaScript; hidden without it) matching every word against every BibTeX field, a row of links to each year and Preprints, big serif year headings with a rule, and condensed cards (6rem thumbnail). Each year is a `section#year-YYYY`; years with no match are hidden while searching. Profile pages keep the smaller headings.
- Research topics link to papers by keyword: a paper whose `keywords` include a research file's name (e.g. `uncertainty-and-change`) is counted in that topic's "N related papers" link, which opens `/publications/?q=<name>`. No separate field; tags are plain keywords, so students add them like any other keyword (the four current tags are listed in `_TEMPLATE.bib` and the paper guide).
- Paper pages: every `.bib` file also builds `publications/<file name>/` (template `publication.html`) from its fields. Shown: venue + date (`month` optional), title, authors (lab members link to profiles; co-first key when present), link buttons, full abstract, `keywords` chips (each searches the Publications page via `?q=`), a generated plain-text citation, DOI/PubMed ID, copyable BibTeX, a "Corresponding author" row under the PubMed ID (names, linked to profiles for lab members; no email on the paper page, the profile holds it; corresponding authors are not highlighted on the paper page, only on the list), and `citation_*` meta tags for Google Scholar. The thumbnail sits top right of the header card at 15rem, uncropped (it stacks below the text on phones); there is no generic filler on the page. List cards open the page through a stretched title link; their small link buttons stay clickable above it, and the abstract toggle moved from the cards to the page. Skipped on purpose: automatic topic/approach tagging, citation counts, a personal reading list. New optional fields: `month`, `pmid`, `keywords`, and extra link fields (`preprint`, `video`, `slides`, `poster`).
- `content/publications/_TEMPLATE.bib` (ignored by the build, like `people/_TEMPLATE.md`) lists every supported field with comments; every paper file carries the same blank optional lines (`field = {}`), which the loader ignores and the page's BibTeX view hides, so students fill in values without looking fields up. A test checks the template and all real paper files list every optional field, so a new field means adding it to `OPTIONAL_FIELDS` in `tests/test_paper_pages.py`, the template and the files.
