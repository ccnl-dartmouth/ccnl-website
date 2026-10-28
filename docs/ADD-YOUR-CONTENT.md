# Add your own content to the lab website

This guide is for lab members. You can do everything in your web browser, with no software to install. The website
rebuilds itself a couple of minutes after you save a change.

You will:

1. [Write your personal blurb (bio)](#1-write-your-bio)
2. [Upload a profile picture](#2-upload-your-profile-picture)
3. [Add a new paper](#3-add-a-paper)
4. [Change other details in your profile](#4-change-other-details-in-your-profile)

If something goes wrong, see [When something goes wrong](#when-something-goes-wrong).

## Before you start

- You need a GitHub account and an invitation to the **ccnl-dartmouth** GitHub organization. Ask the lab's website
  maintainer to add you with **Write** access. GitHub will ask you to turn on two-factor authentication.
- The website's files live at https://github.com/ccnl-dartmouth/ccnl-website. Everything you edit is in the
  `content` folder.
- **Only edit your own files:** your page in `content/people/`, your photo in `content/images/`, and the papers you add
  in `content/publications/` (with their optional thumbnails in `content/images/`). Please don't change other people's
  files, or anything outside `content/`.
- **One rule for pictures:** every picture goes in the one folder `content/images/` and has the **same name** as the
  page or paper it belongs to (lowercase). `jane-doe.md` goes with `jane-doe.jpg`, and `2026-doe-paper.bib` goes with
  `2026-doe-paper.jpg`. There are no subfolders.
- **Everything you upload is public**, including the original version of your photo.

### How saving works

Every change is saved by **committing** it. The steps are always the same:

1. Make your change in the browser editor.
2. Click the green **Commit changes...** button, then choose **Commit directly to the main branch** and confirm.
3. Wait 2 to 3 minutes. Open the **Actions** tab (https://github.com/ccnl-dartmouth/ccnl-website/actions) to watch: a
   green check means your change is on the website. A red cross means something needs fixing (see the end of this
   guide). The old version of the website stays up until a change builds successfully, so you can't break the site.

## 1. Write your bio

Everyone listed on the People page has a page of their own, made from one file named after you. The file has two parts:
a block of details at the top between `---` lines, and your bio underneath.

**If you already have a file** (most current lab members do):

1. Go to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/people and click your file, for example
   `jane-doe.md`.
2. Click the **pencil icon** (Edit this file) at the top right.
3. Write your bio **below the second `---` line**. Leave the block at the top as it is.
4. Click **Commit changes...** (see "How saving works").

**If you don't have a file yet**, create one:

1. Open the template: https://github.com/ccnl-dartmouth/ccnl-website/blob/main/content/people/_TEMPLATE.md and click
   the **Copy raw file** icon.
2. Go to the `content/people` folder, click **Add file**, then **Create new file**.
3. In the name box type `content/people/` followed by your name in lowercase with hyphens, ending in `.md`. For
   example `content/people/jane-doe.md`.
4. Paste the template, fill in your details (see section 4), write your bio, and commit.

A complete example:

```markdown
---
name: Jane Doe
role: grad
status: current
start: 2024
degrees: B.Sc.
links:
  scholar: https://scholar.google.com/citations?user=ABCDEFG
  github: janedoe
---
I am a graduate student interested in how people learn from rewards when the world keeps changing.
Before coming to Dartmouth I studied physics at Example University.

## Research

I build computational models of learning and test them with behavioral experiments.
```

### Formatting your bio

The bio is written in Markdown. The few things you need:

| You type | You get |
|---|---|
| a blank line between paragraphs | separate paragraphs |
| `**bold**` and `*italic*` | **bold** and *italic* |
| `[text of the link](https://example.org)` | a link |
| `## Research` on its own line | a section heading |

Two or three short paragraphs is plenty. Your name, role, years and links are shown automatically in the box next to
your bio, so you don't need to repeat them.

## 2. Upload your profile picture

1. Pick a headshot, ideally roughly square. The website crops it to a square and resizes it, so any normal size is
   fine (up to 25 MB). JPG, PNG, WEBP and iPhone HEIC photos all work.
2. **Name the file exactly like your page, in lowercase.** If your page is `jane-doe.md`, the picture must be
   `jane-doe.jpg` (or `.png`, `.webp`, `.heic`). Capital letters matter: `Jane-Doe.JPG` will not work.
3. Go to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/images (the `images` folder, not the
   `people` folder), click **Add file**, then **Upload files**, drag your picture in, and click **Commit changes**. No
   other change is needed: the website pairs the photo with your page by name.

To replace a picture, upload a new one with the same name.

**Remove location data first.** Photos from phones often contain the GPS location where they were taken. The
website strips it from the published picture, but the original file you upload stays visible in the repository.
The build will warn you if it finds location data. To remove it: on a Mac open the photo in Preview, choose
Tools, Show Inspector, then the GPS tab and **Remove Location Info**; on Windows right-click the file, choose
Properties, Details, **Remove Properties and Personal Information**; on a phone, share the photo with "Location"
switched off.

## 3. Add a paper

Each paper is **one `.bib` file** in `content/publications`. A `.bib` file is the standard bibliography format that
Google Scholar and journals provide.

### Step 1: get the BibTeX

- **From Google Scholar:** find the paper, click the quotation mark **Cite** under it, then click **BibTeX**, and
  copy the text.
- **From a DOI:** paste the DOI into https://www.doi2bib.org and copy the result.
- **From the journal:** most article pages have a "Cite" or "Export citation" button with a BibTeX option.

### Step 2: create the file

The easiest start is the template https://github.com/ccnl-dartmouth/ccnl-website/blob/main/content/publications/_TEMPLATE.bib:
it lists every line the website understands, and every paper file already has the same blank lines, so you only fill in
the ones you want. Lines left as `{}` are ignored. The steps below work either way.

1. Go to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/publications, click **Add file**, then
   **Create new file**.
2. Name it `content/publications/` + year + your last name + a few words from the title + `.bib`, in lowercase with
   hyphens. For example `content/publications/2026-doe-learning-under-uncertainty.bib`. (The name only has to be
   unique and end in `.bib`.)
3. Paste the BibTeX. **One paper per file.**
4. Add the extra lines below if you want them, then commit.

A complete example (the lines after `year` are all optional):

```bibtex
@article{doe2026learning,
  author = {Doe, Jane and Smith, Alex and Soltani, Alireza},
  title = {Learning under uncertainty},
  journal = {Journal of Examples},
  volume = {12},
  number = {3},
  pages = {100--112},
  year = {2026},
  month = {mar},
  doi = {10.1000/example.2026.1},
  pmid = {12345678},
  keywords = {learning, uncertainty},
  pdf = {https://example.org/learning.pdf},
  cofirst = {Doe, Smith},
  corresponding = {Soltani},
  abstract = {A short summary of the paper, copied from the journal or Google Scholar.},
}
```

### What the website needs and what you can add

**Required:** `author`, `title`, `year`, and a venue (`journal`, or `booktitle` for a chapter or proceedings, or
`howpublished` for a preprint). Authors are written `Last, First and Last, First`.

**Optional extras:**

| Line | What it does |
|---|---|
| `month = {mar}` | shown as "Mar 2026" on the paper's page (a number 1 to 12 or a month name) |
| `doi = {...}` | adds a DOI button |
| `pmid = {12345678}` | adds a PubMed button; just the number |
| `pdf`, `preprint`, `si`, `data`, `code`, `video`, `slides`, `poster`, `url` | adds link buttons; values must start with `https://` |
| `abstract = {...}` | the abstract, shown in full on the paper's own page |
| `keywords = {learning, uncertainty}` | keyword chips on the paper's page; clicking one searches the Publications page. Separate with commas or semicolons |
| `cofirst = {Doe, Smith}` | marks these authors (by last name) as co-first authors, shown in purple |
| `corresponding = {Soltani}` | marks corresponding authors: a yellow highlight on the Publications list, and a "Corresponding author" line under Cite on the paper's page that links to their profile (put your email on your profile if you want it shown) |
| `status = {preprint}` | lists the paper under "Preprints" |
| `note = {...}` | a short note shown under the venue, for example "Highlighted in Nature" |
| `image = {figure.jpg}` | optional: use this file from `content/images/` instead of the one named like the paper's file (see "A thumbnail" below) |

### A thumbnail (optional)

Papers without a thumbnail get a generic picture. To add your own (a figure from the paper, for example), upload it
to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/images (the same `images` folder as photos) and
give it **the same name as the paper's `.bib` file**. For `2026-doe-learning-under-uncertainty.bib` upload
`2026-doe-learning-under-uncertainty.jpg`. No other change is needed.

To use a picture with a different name, or one picture for several papers, upload it to `content/images` under any
name and add `image = {shared-figure.jpg}` to each of those `.bib` files.

### The paper's own page

Every paper gets its own page, built from its `.bib` file: the cards on the Publications page open it. It shows the
venue and date, authors (lab members link to their profiles), buttons, the full abstract, keywords, a formatted
citation with a copy-BibTeX button, and the corresponding author (linked to their profile). The page's web address is the `.bib`
file name, so use lowercase letters, digits and hyphens only. Nothing extra to write: just fill in more BibTeX lines.

### Good to know

- **Your name links papers to your page.** Papers appear on a person's page when an author matches their name by
  **last name and first initial** (so "Doe, Jane" matches Jane Doe). Anyone listed on the People page is
  highlighted in bold blue in the author lists. Write author names the same way in each paper.
- **Fixing or completing a paper:** open its `.bib` file, click the pencil, change it, and commit. Every paper file already
  has all the optional lines with empty braces (`doi = {},`), so to add a missing keyword, abstract, DOI or link, just
  type the value between the braces. Blank lines are ignored and never shown on the website.

## 4. Change other details in your profile

All your details are the lines between the two `---` lines at the top of your file in `content/people/`. Open the
file, click the pencil, change a line, and commit.

| Line | Meaning | Example |
|---|---|---|
| `name` | your name as it should appear | `name: Jane Doe` |
| `role` | `postdoc`, `grad`, `undergrad` (the lab manager sets `pi` and `collaborator`) | `role: grad` |
| `status` | `current` or `alumni` | `status: current` |
| `start` | the year you joined (optional) | `start: 2024` |
| `end` | the year you left (optional; leave it out while you're in the lab) | `end: 2029` |
| `degrees` | shown after your name | `degrees: M.S.` |
| `current_position` | where you are now (for alumni) | `current_position: Data Scientist, Example Co.` |
| `links` | any of the links below | see below |
| `profile` | `false` hides your personal page | `profile: false` |

**Links.** Put these under a `links:` line, indented by two spaces, one per line. Use only the ones you want:

```
links:
  scholar: https://scholar.google.com/citations?user=ABCDEFG
  orcid: 0000-0002-1825-0097
  github: janedoe
  website: https://example.org/jane
  cv: https://example.org/jane/cv.pdf
  linkedin: https://www.linkedin.com/in/janedoe
  bluesky: https://bsky.app/profile/jane.bsky.social
  email: jane.doe@dartmouth.edu
```

Your email is shown with a spam-protected link. ORCID takes the number, and GitHub takes just your user name.

**When you leave the lab:** change `status: current` to `status: alumni`, add `end: 2029`, and add
`current_position: ...` if you like. You'll move to the Alumni list automatically, and your page and papers stay.

## When something goes wrong

If the **Actions** tab shows a red cross, click the failed run and open the **Build the site** step. The message
names the file and says what to fix. Fix that file and commit again. The website keeps showing the last good version
in the meantime. A GitHub issue titled "The website build failed" is also opened and closes itself when it's fixed.

| The message says | What to do |
|---|---|
| `the file name must use only lowercase letters, digits and hyphens` | rename the file, for example `jane-doe.md` |
| `unknown field 'rol' (did you mean 'role'?)` | fix the spelling of the line |
| `missing required field 'role'` | add the line shown in the message |
| `... is not valid YAML` | a value with a colon in it needs quotes, for example `current_position: "Lab: Example"` |
| `rename the image to 'jane-doe.jpg'` | the picture name must be lowercase and match your page name (or the paper's `.bib` name) |
| `images do not go in this folder` | a picture was uploaded next to the text files: move it to `content/images/` |
| `this image doesn't match any person, paper or research theme` | a warning: the picture's name doesn't match any page or paper, so it isn't shown; rename it |
| `the name '...' belongs to both a person and a ...` | two kinds of file share a name, so the picture can't be paired; rename one of the files |
| `there are two images named '...'` | `jane-doe.jpg` and `jane-doe.png` both exist: delete one |
| `contains GPS location data` | remove the location from the original photo and upload it again (see section 2) |
| `no valid BibTeX entry found` | the `.bib` file is empty or has unbalanced `{ }` braces or a missing comma |
| `contains 2 entries` | put each paper in its own `.bib` file |
| `entry '...' is missing: year` | add `year = {2026},` |
| `BibTeX key '...' is also used in ...` | change the word after `@article{` so it's unique |
| `` `month` must be a number from 1 to 12 `` | write `month = {3}` or `month = {mar}` |
| `` `pmid` must be just the number `` | write only the digits, for example `pmid = {12345678}` |
| `` `cofirst` lists ..., who is not among the authors `` | use last names exactly as they appear in the author list |

Still stuck? Ask the lab's website maintainer and send them the error text.

## Optional: preview your change on your own computer

You don't need this, but if you want to check a change before saving it, install Python 3.12, clone the repository,
and run:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py --serve
```

Then open http://localhost:8000.
