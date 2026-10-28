# Start here: editing the lab website

This guide is for lab members. You can do everything in your web browser, with no software to install. The website
rebuilds itself a couple of minutes after you save a change.

## Which guide do you need?

| I want to... | Guide |
|---|---|
| write my bio, change my photo, links or role, or mark myself as alumni | [Update your profile](UPDATE-PROFILE.md) |
| add a paper, or fix or complete one | [Add or fix a paper](ADD-A-PAPER.md) |
| change the home text, research topics, teaching, resources, contact or "join us" text, address, funders | [Edit the site's text and pictures](EDIT-SITE-TEXT.md) |
| understand an error message or a red cross | [When something goes wrong](TROUBLESHOOTING.md) |

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

## How saving works

Every change is saved by **committing** it. The steps are always the same:

1. Make your change in the browser editor.
2. Click the green **Commit changes...** button, then choose **Commit directly to the main branch** and confirm.
3. Wait 2 to 3 minutes. Open the **Actions** tab (https://github.com/ccnl-dartmouth/ccnl-website/actions) to watch: a
   green check means your change is on the website. A red cross means something needs fixing (see the end of this
   guide). The old version of the website stays up until a change builds successfully, so you can't break the site.

## Where does each part of the website come from?

Every piece of text or picture on the website comes from one file in the `content` folder
(https://github.com/ccnl-dartmouth/ccnl-website/tree/main/content). To change something, find it in this table, open that file, and edit it.

| On the website | Where it comes from | Guide |
|---|---|---|
| **Menu** at the top (page names and order) | `content/site.yaml` | [Site text](EDIT-SITE-TEXT.md) |
| **Footer**: lab name, department, institution and logo, funder logos, social links | `content/lab.yaml` and the logos in `content/images/` | [Site text](EDIT-SITE-TEXT.md) |
| **Home**: big title and intro paragraphs | `content/home.md` | [Site text](EDIT-SITE-TEXT.md) |
| **Home**: background photo | the file named in `content/home.md` (`hero_image`), stored in `content/images/` | [Site text](EDIT-SITE-TEXT.md) |
| **Home**: the department and college under the title | `content/lab.yaml` | [Site text](EDIT-SITE-TEXT.md) |
| **Home**: the boxes (Research, People, ...) | the menu in `content/site.yaml` | [Site text](EDIT-SITE-TEXT.md) |
| **Research**: each topic's title and text | `content/research/<topic>.md` | [Site text](EDIT-SITE-TEXT.md) |
| **Research**: each topic's picture | `content/images/<topic>.jpg` (same name as the topic's file) | [Site text](EDIT-SITE-TEXT.md) |
| **People**: a person's card and page, with bio and links | `content/people/<name>.md` | [Profile](UPDATE-PROFILE.md) |
| **People**: a person's photo | `content/images/<name>.jpg` (same name as the person's file) | [Profile](UPDATE-PROFILE.md) |
| **Publications**: a paper's card and its own page | `content/publications/<paper>.bib` | [Papers](ADD-A-PAPER.md) |
| **Publications**: a paper's thumbnail | `content/images/<paper>.jpg` (same name as the paper's file) | [Papers](ADD-A-PAPER.md) |
| **Resources**: software and datasets; the teaching list | `content/resources/<name>.md`, `content/teaching/<course>.md` | [Site text](EDIT-SITE-TEXT.md) |
| **Contact**: address and email | `content/lab.yaml` | [Site text](EDIT-SITE-TEXT.md) |
| **Contact**: "Join us" openings and general note | `content/join.md` | [Site text](EDIT-SITE-TEXT.md) |

Everything else (colors, fonts, layout) is part of the website's design and lives outside `content/`. Please leave it
to the lab's website maintainer.
