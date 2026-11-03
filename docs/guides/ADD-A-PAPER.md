# Add or fix a paper

Each paper is **one `.bib` file** in `content/publications/`. It makes the paper's card on the Publications page, its
own page, and its entry on the profile page of each author who has one (lab members). New to editing? Read
[Start here](START-HERE.md) first for how saving ("committing") works.

A `.bib` file is the standard bibliography format that Google Scholar and journals provide.

## Step 1: get the BibTeX

- **From Google Scholar:** find the paper, click the quotation mark **Cite** under it, then click **BibTeX**, and
  copy the text.
- **From a DOI:** paste the DOI into https://www.doi2bib.org and copy the result.
- **From the journal:** most article pages have a "Cite" or "Export citation" button with a BibTeX option.

## Step 2: create the file

The easiest start is the template https://github.com/ccnl-dartmouth/ccnl-website/blob/main/content/publications/_TEMPLATE.bib:
it lists every line the website understands, and every paper file already has the same blank lines, so you only fill in
the ones you want. Lines left as `{}` are ignored. The steps below work either way.

1. Go to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/publications, click **Add file**, then
   **Create new file**.
2. Name it `content/publications/` + year + your last name + a few words from the title + `.bib`, in lowercase with
   hyphens. For example `content/publications/2026-doe-learning-under-uncertainty.bib`. (The name only has to be
   unique and end in `.bib`.)
3. Paste the BibTeX. **One paper per file.**
4. **Check the author line:** write the first name in full for every author who is on the People page (`Doe, Jane`, not
   `Doe, J`; Google Scholar often gives initials). See "Good to know" below for why.
5. Add the extra lines below if you want them, then commit.

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
  senior = {Soltani},
  abstract = {A short summary of the paper, copied from the journal or Google Scholar.},
}
```

## What the website needs and what you can add

**Required:** `author`, `title`, `year`, and a venue (`journal`, or `booktitle` for a chapter or proceedings, or
`howpublished` for a preprint). Authors are written `Last, First and Last, First`, with the first name in full for anyone on the People page.

**Optional extras:**

| Line | What it does |
|---|---|
| `month = {mar}` | shown as "Mar 2026" on the paper's page (a number 1 to 12 or a month name) |
| `doi = {...}` | adds a DOI button |
| `pmid = {12345678}` | adds a PubMed button; just the number |
| `pdf`, `preprint`, `si`, `data`, `code`, `video`, `slides`, `poster`, `url` | adds a link to the row of links on the paper's page (not on the Publications list); values must start with `https://` |
| `abstract = {...}` | the abstract, shown in full on the paper's own page |
| `keywords = {learning, uncertainty}` | keyword chips on the paper's page; clicking one searches the Publications page. Separate with commas or semicolons. To list the paper on the Research page, add the tag of each research topic it belongs to: `uncertainty-and-change`, `complex-environments`, `attention-bias-decision-making`, `neural-synaptic-mechanisms` |
| `cofirst = {Doe, Smith}` | marks these authors (by last name) as co-first authors, shown with a ¶ after the name. Use the same last names as in the author line. |
| `corresponding = {Soltani}` | marks corresponding authors: a ♦ after the name, and a "Corresponding author" line under Cite on the paper's page that links to their profile (put your email on your profile if you want it shown) |
| `senior = {Soltani, Izquierdo}` | marks the senior (supervising) authors by last name; several are allowed for co-senior papers. Follow the PI's CV. Senior authors get a ★ after the name. Leave `cofirst`, `corresponding` and `senior` empty on a single-author paper: there is nothing to tell apart. |
| `status = {preprint}` | lists the paper under "Preprints" |
| `note = {...}` | a short note shown under the venue, for example "Highlighted in Nature" |
| `image = {figure.jpg}` | optional: use this file from `content/images/` instead of the one named like the paper's file (see "A thumbnail" below) |

## A thumbnail (optional)

The lab's convention is the journal's cover for the issue the paper appeared in (or the journal logo if the journal has
no issue covers); see `docs/maintainers/COVER-IMAGES.md` for what is in place. Papers without an image show no thumbnail. To add your own
(a figure from the paper, for example), upload it
to https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content/images (the same `images` folder as photos) and
give it **the same name as the paper's `.bib` file**. For `2026-doe-learning-under-uncertainty.bib` upload
`2026-doe-learning-under-uncertainty.jpg`. No other change is needed.

To use a picture with a different name, or one picture for several papers, upload it to `content/images` under any
name and add `image = {shared-figure.jpg}` to each of those `.bib` files.

## The paper's own page

Every paper gets its own page, built from its `.bib` file: the cards on the Publications page open it. It shows the
venue and date, authors (anyone with a profile links to it), a row of links (DOI, PDF, ...), the full abstract, keywords, a formatted
citation with a copy-BibTeX button, and the corresponding author (linked to their profile). The page's web address is the `.bib`
file name, so use lowercase letters, digits and hyphens only. Nothing extra to write: just fill in more BibTeX lines.

## Good to know

- **Write the first name in full for anyone on the People page.** A paper joins a person's page when an author has their
  last name and first name (`Doe, Jane` matches Jane Doe; a nickname in parentheses on the People page counts too).
  Lab members (postdocs, graduate and undergraduate students, past and present) are bold blue in the author lists, the PI
  is bold yellow, and collaborators are plain. A key at the top of the page explains the marks.
- **If the build stops on an author:** an author written with initials only (`Doe, J`) who could be someone on the People
  page makes the build stop, because it can't tell whether it is them or another person with the same name. The message names
  the author. If it is the person on the People page, write their first name in full. If it is someone else, write that
  person's first name in full. Authors who could not be anyone on the People page can stay as initials.
- **Fixing or completing a paper:** open its `.bib` file, click the pencil, change it, and commit. Every paper file already
  has all the optional lines with empty braces (`doi = {},`), so to add a missing keyword, abstract, DOI or link, just
  type the value between the braces. Blank lines are ignored and never shown on the website.

Something wrong? See [When something goes wrong](TROUBLESHOOTING.md).
