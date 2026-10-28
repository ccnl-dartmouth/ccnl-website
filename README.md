# CCNL website

Source for the Computational & Cognitive Neuroscience Lab website (Dartmouth):
https://ccnl-dartmouth.github.io/ccnl-website/

## Lab members: edit the website in your browser

Nothing to install. Open the file that controls the part of the site you want to change, click the pencil icon, and
save ("commit"). The site rebuilds in 2 to 3 minutes; the [Actions tab](https://github.com/ccnl-dartmouth/ccnl-website/actions)
shows a green check when it is live, or an error message naming the file to fix. A broken change never takes the site down.

**New here? Start with [the beginner guide](docs/guides/START-HERE.md).**

### Which guide do I need?

| I want to... | Guide |
|---|---|
| write my bio, change my photo, links or role | [Update your profile](docs/guides/UPDATE-PROFILE.md) |
| add a paper, or fix or complete one | [Add or fix a paper](docs/guides/ADD-A-PAPER.md) |
| change home text, research topics, teaching, resources, contact or "join us" text, funders | [Edit the site's text and pictures](docs/guides/EDIT-SITE-TEXT.md) |
| understand an error message or a red cross | [When something goes wrong](docs/guides/TROUBLESHOOTING.md) |

### Where does each part of the website come from?

All text and pictures are files in [`content/`](content). Pictures live in `content/images/` and are paired with a page by
having the same name (`jane-doe.md` goes with `jane-doe.jpg`).

| On the website | Edit this |
|---|---|
| Menu at the top | [`content/site.yaml`](content/site.yaml) |
| Footer, logos, funders, department and college | [`content/lab.yaml`](content/lab.yaml) |
| Home: title and intro | [`content/home.md`](content/home.md) |
| Home: background photo | the file named in `home.md`, in [`content/images/`](content/images) |
| Research topics: text | [`content/research/`](content/research), one file per topic |
| Research topics: pictures | [`content/images/`](content/images), same name as the topic's file |
| People: cards, pages, bios, links | [`content/people/`](content/people), one file per person |
| People: photos | [`content/images/`](content/images), same name as the person's file |
| Publications: cards and paper pages | [`content/publications/`](content/publications), one `.bib` file per paper |
| Publications: thumbnails | [`content/images/`](content/images), same name as the paper's file |
| Resources and teaching | [`content/resources/`](content/resources), [`content/teaching/`](content/teaching) |
| Contact: address and email | [`content/lab.yaml`](content/lab.yaml) |
| Contact: "Join us" text | [`content/join.md`](content/join.md) |

The full version of this table is in [the beginner guide](docs/guides/START-HERE.md#where-does-each-part-of-the-website-come-from).
Everything outside `content/` (layout, colors, build code) belongs to the website maintainer.

## For maintainers

| Document | What it covers |
|---|---|
| [docs/maintainers/PLAN.md](docs/maintainers/PLAN.md) | decisions, status and open items |
| [docs/maintainers/STRUCTURE.md](docs/maintainers/STRUCTURE.md) | the content model, repo layout, validation rules, visual design |
| [docs/maintainers/OPERATIONS.md](docs/maintainers/OPERATIONS.md) | alerts, uptime and link checks, GitHub settings |
| [docs/maintainers/CREDITS.md](docs/maintainers/CREDITS.md) | third-party assets and licenses |

Every push to `main` builds, tests and deploys the site. If the build or a test fails, nothing is deployed and the last
good version stays live.
