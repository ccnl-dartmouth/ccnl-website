# Edit the site's text and pictures

The pages that are not about one person or one paper (home, research, resources, teaching, contact, footer) come from a
few text files in `content/`. They are edited the same way as your own profile: open the file on GitHub, click the
pencil, change it, and commit. New to editing? Read [Start here](START-HERE.md) first for how saving works and for the
table of which file controls what. These files are shared, so check with the lab's website maintainer before changing
them.

Text files have a block of settings between two `---` lines at the top, then text below it written in Markdown (see
"Formatting your bio" in [Update your profile](UPDATE-PROFILE.md)). Keep the settings' names exactly as they are and
change only the values.

## Home page: `content/home.md`

```yaml
---
headline: Computational & Cognitive Neuroscience Lab   # the big title (optional)
hero_image: lab-group.jpg   # optional: a file in content/images/ for the background photo
hero_alt: Lab members at the 2026 retreat   # describe the photo for screen readers
---
Intro text, in Markdown.
```

The text below the settings is the intro paragraphs. The department and college shown under the title come from
`content/lab.yaml`. The boxes below the intro (Research, Publications, People, ...) come from the menu in
`content/site.yaml`.

## Research topics: `content/research/<topic>.md`

One file per topic. `title` is the heading, `order` sets the sequence (lowest first), the text below is the summary,
and `image_alt` describes the picture for screen readers. The picture is `content/images/<topic>.jpg`, with the same
name as the topic's file. To add a topic, add a new file; to remove one, delete its file.

## Resources: `content/resources/<name>.md`

Software, datasets and other things to share. `title` is the heading, `links` lists buttons, and `paper` (optional) is
the BibTeX key of the related paper. The text below is a short description.

```yaml
---
title: Salience-driven value construction
paper: spitmaan2019salience
links:
  - {label: Code, url: "https://github.com/..."}
---
Short description.
```

## Teaching: `content/teaching/<course>.md`

One file per course, shown on the Resources page. `code` is the course number, `title` the name, `next_offering`
(optional) says when it runs next, and the text below is the description.

## Contact page

- **Address and email:** in `content/lab.yaml` (`address`, `email`).
- **"Join us" text:** `content/join.md`. `recruiting: open` or `closed` switches the banner, and `updated` is the date
  the text was last checked. The text below the settings is shown on the Contact page.

## Lab-wide details: `content/lab.yaml`

The lab name, tagline, department, institution, address, email, the institution logo, the funders (name, logo, web
address) and social links. They appear in the footer and on the Home and Contact pages. Logos are files in
`content/images/`, named in this file.

## Menu: `content/site.yaml`

The list of pages in the top menu. Reorder the lines to reorder the menu, or change a `label` to rename a page. Don't
change the `page:` values.

Something wrong? See [When something goes wrong](TROUBLESHOOTING.md).
