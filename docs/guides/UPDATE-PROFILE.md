# Update your profile

Your bio, photo, links and role live in one file named after you in `content/people/`, plus a photo in
`content/images/`. New to editing? Read [Start here](START-HERE.md) first for how saving ("committing") works.

## Write your bio

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
4. Paste the template, fill in your details (see "Change other details" below), write your bio, and commit.

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

## Upload your profile picture

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

## Change other details in your profile

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

## Where it shows up

Your file makes your **card** on the People page and your **own page**. Your card shows your name, role and affiliation (your
`current_position` if you set one, otherwise the lab's institution). Your page also lists every paper whose author list
matches your name, see [Add or fix a paper](ADD-A-PAPER.md).

Something wrong? See [When something goes wrong](TROUBLESHOOTING.md).
