# Running the site: alerts, monitoring, and settings

What watches the site, who gets told, and the one-time GitHub settings. No passwords or secret
tokens are used anywhere; everything runs on GitHub's built-in token.

## How problems reach people

Alerts are **tiered so nobody is spammed**. Every alert starts as a quiet issue. It only reaches
more people if it is still open after a while; anything that fixes itself, or that the person who
caused it fixes, never goes further.

| Problem | Detected by | First alert (quiet) | Escalation if still open |
|---|---|---|---|
| A commit breaks the build or tests | `deploy.yml` (every push to `main`) | Issue `build-failure` with the error message; mentions **only the person who pushed**. The site is not updated, but the live site is fine. | After **3 days**: team mentioned once |
| GitHub Pages deploy fails | `deploy.yml` | Same issue, with a note to re-run the workflow | Same |
| The site stops answering | `uptime.yml` (every 6 hours) | Issue `site-down`; mentions nobody | After **12 hours** (two missed checks): **team and PI** mentioned |
| Dead links on the site | `links.yml` (Mondays) | Issue `dead-links` listing each link and its page; mentions nobody. Sites that block bots are only listed as "could not verify". | After **14 days**: team mentioned |

Every issue closes itself with a comment when the problem is gone. Repeated failures add a comment
to the existing issue instead of opening duplicates. The escalation check is `escalate.yml`, which
runs every 6 hours and mentions people only once per issue (it adds the label `escalated`).
To change the waiting times, edit the `--after-hours` numbers in `escalate.yml`.

### Who gets escalation emails (one-time setup)

1. Create the team `lab-members` in the org (Teams -> New team) and add everyone.
2. In the repo: Settings -> Secrets and variables -> Actions -> **Variables** -> New repository variable. Add two:
   - `ALERT_MENTIONS_TEAM` = `@ccnl-dartmouth/lab-members`
   - `ALERT_MENTIONS_PI` = `@<PI-github-username>`
   The PI is only mentioned when the site itself is down, not for build or link problems.
3. Each person must have email notifications on for mentions (GitHub -> Settings -> Notifications).
   Anyone who wants every alert can click Watch -> Custom -> Issues on the repo; nobody has to.
4. The PI's address must be reachable after you leave: check it when you hand over.

If the variables are not set, escalation does nothing; the person who pushed still gets the quiet
first alert (and GitHub's own "workflow failed" email). The external uptime monitor below is the
fast channel for a downed site.

## Uptime monitoring

`uptime.yml` is a built-in check with no accounts, but it has two limits: GitHub can delay scheduled
runs by many minutes, and it only runs while the repo is active (see "60-day rule" below). For
something independent of GitHub, also set up a free external monitor (about 5 minutes):

1. Create a free account at uptimerobot.com using a lab address (not a personal one).
2. Add monitor -> type *HTTP(s)* (or *Keyword*, keyword `Computational`) -> URL of the site
   -> interval 5 minutes.
3. Alert contacts: add the PI's email and yours (and a lab list address if there is one).
4. Write the account name and who owns it in `docs/OWNERSHIP.md`.

If the address changes (custom domain), set the repository variable `SITE_URL` so `uptime.yml`
checks the new one, and update the external monitor.

## The 60-day rule for scheduled workflows

GitHub switches off scheduled workflows in a public repo after 60 days with no repository activity
(commits). Ordinary member edits keep them alive. After a long quiet spell, check the Actions tab:
a disabled workflow shows a yellow banner with an **Enable workflow** button.
The external uptime monitor is not affected, which is the main reason to have one.

## One-time GitHub settings

- **Pages:** Settings -> Pages -> Source: *GitHub Actions* (done).
- **Issues:** must be enabled on the repo (they are by default); alerts need them.
- **Workflow permissions:** the workflows ask for what they need in their own files; no change required.
- **Branch ruleset for `main`** (Settings -> Rules -> Rulesets -> New branch ruleset):
  - Name: `protect main`; Enforcement: *Active*; Target: *Default branch*.
  - Tick **Restrict deletions** and **Block force pushes**.
  - **Do not** tick "Require a pull request" and **do not** tick "Require status checks to pass".
    Required status checks make GitHub reject direct commits (a new commit has no check result yet),
    which would force every member's edit through a pull request and defeat the hands-off design.
    A broken commit cannot take the site down anyway: the build fails and the old version stays live.
  - If `main` is ever broken, anyone with Write access can fix the file, or click *Revert* on the
    offending commit in GitHub, and the next successful build closes the alert.

## Testing that the alerts work

Do this after changing anything in `.github/workflows/` or `ccnl/alerts.py` (and once with the
real mailing setup):

1. Commit a deliberately bad file, e.g. `content/people/test-person.md` containing `name: x`.
2. Within a couple of minutes: the Actions run turns red and an issue `The website build failed`
   appears with the error text, mentioning only you.
3. Delete the file. The next run goes green and the issue closes itself.

To test escalation without waiting 3 days: open an issue labelled `build-failure` by hand, then run
`escalate.yml` from the Actions tab with a temporarily lowered `--after-hours` (e.g. 0), or just
check that its log says "Escalated issues: none" when nothing is due.

Run `links.yml`, `uptime.yml` and `escalate.yml` by hand from the Actions tab (*Run workflow*) to see them work.
