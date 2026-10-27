# CCNL website rebuild: plan

Rebuild of https://sites.dartmouth.edu/ccnl/ (WordPress, Oxygen 0.6.0 theme) as a static
site on GitHub Pages that lab members can update themselves.

## Decisions so far

- **Hosting:** GitHub Pages, deployed from GitHub Actions.
- **GitHub org:** `ccnl-dartmouth` (owners: Peter Duggins + the PI; members on a Write team).
  Repo: `ccnl-website`. Org, not a personal account, so ownership survives turnover.
- **Generator:** custom Python build (Jinja2, PyYAML, Markdown, bibtexparser, Pillow). Not Jekyll/Hugo/Astro.
  Reason: content is text, pictures and links only; structure will be frozen; students must get
  plain-language errors for bad images and BibTeX.
- **Maintenance model:** no required reviewers. `main` requires a passing build; a failed build
  leaves the last good site live. Members fix their own breakage. Failure and downtime alerts go to
  the PI and the lab.
- **Editing model:** members edit their own files in the GitHub web editor (or git push). No local
  setup needed; the build runs in Actions.
- **Domain:** Dartmouth web support (Oct 2026): no policy against pointing a dartmouth.edu subdomain
  at an external host, but labs are not eligible for one. They suggested `ccnl.host.dartmouth.edu`
  (cPanel/LAMP with Git). Decision: stay on GitHub Pages at `ccnl-dartmouth.github.io` (automated
  builds, no dependence on a NetID-bound server account, easy member edits). Keep
  `sites.dartmouth.edu/ccnl` as a redirect or "we've moved" page (asked web support which the
  platform supports; reply pending). Ask the department to update its link to the lab. Build must
  support a base path (`/ccnl-website/`) until/unless a custom domain is added.
  If a dartmouth.edu name becomes required, revisit host.dartmouth.edu; first ask: can the account
  belong to a department/PI, is automated deploy (SFTP/SSH) allowed, how does its Git feature work.
- **Old site:** the PI has approved admin access to the WordPress site for the migration.
- **Custom domain (deferred to launch, phase 11):** a .com/.org (~$10-15/yr) can be added later by
  pointing DNS at GitHub Pages and setting the workflow base path to empty. Checked Oct 2026 (RDAP):
  `ccnl.org/.com/.net`, `ccnlab.org/.com` are taken; `soltanilab.org/.com`, `soltani-lab.org`,
  `ccnl-lab.org`, `ccnl-dartmouth.org/.com` looked unregistered. Registrant must be the PI/department/lab
  (not a personal account), with lab email, 2FA and auto-renew; avoid "dartmouth" in the name unless
  Dartmouth approves. `.edu` is not available to labs.

## Design references

Reviewed other labs' sites (Oct 2026). Layout and content: **Niv Lab (Princeton)**; look and feel:
Contextual Dynamics Lab (Dartmouth) and Murray Lab (Yale). Also seen: Kable (Penn), LNCC (Brown),
Gershman (Harvard). Sections are chosen in `docs/STRUCTURE.md` and can change later.

## Open items

- [x] Dartmouth web support replied on the hostname (see Decisions).
- [x] Web support: sites.dartmouth.edu can redirect, but only as one global rule: every `/ccnl` URL goes to a
      single new page (not page-to-page). They do it on request via the ticket; ask at launch (phase 11).
      Alternative: we are admins of the old site, so we can instead leave a "we've moved" page there.
- [ ] **TODO: PI has no known GitHub account yet.** Needed before handover: ask him to create one (use his
      dartmouth.edu address + 2FA), then add him as an org owner (1.3) and set the repo variable
      `ALERT_MENTIONS_PI`. Until then he can still be alerted about a downed site by email through the
      external UptimeRobot monitor (no GitHub account needed); add him as an alert contact there.
- [ ] List of lab members' GitHub usernames.
- [ ] Long-lived contact email for the org (PI or lab list address).
- [ ] Get admin access to the old WordPress site.

## Phases

| # | Phase | Output |
|---|---|---|
| 0 | Decisions | Org name, go-ahead (done except Dartmouth reply) |
| 1 | GitHub setup | Org, repo, team, Pages, protections |
| 2 | Content audit | Inventory of old pages, people, papers, images |
| 3 | Structure design | Data schemas, repo layout, validation rules (machinery and member recipes then fixed; sections stay flexible). See `docs/STRUCTURE.md` |
| 4 | Core build | Python build, placeholder styling, local preview |
| 5 | Validation and tests | Friendly errors, pytest with broken fixtures |
| 6 | Automation | Actions build/deploy, failure alerts, uptime monitor, link check |
| 7 | Design | Reference sites, HTML/CSS, responsive, accessible |
| 8 | Content migration | Scripted + manual copy, members review own pages |
| 9 | Member testing | Non-owner account, deliberate failures, alerts confirmed |
| 10 | Documentation | Student README (3 recipes), maintainer docs |
| 11 | Launch | Custom domain + HTTPS, redirect from old site, update external links |
| 12 | Handover | PI is owner, alerts reach PI, OWNERSHIP.md complete |

## Progress

- [x] 0 Decisions, 1 GitHub setup (remaining: PI as owner, 2FA, team/invites, `main` ruleset), 3 Structure design
- [x] 4 Core build: `build.py` + `ccnl/` (loading, validation, images, rendering), templates, placeholder CSS,
      `sample_content/`, smoke tests. Validation already gives friendly errors; phase 5 adds the full test suite.
- [x] 5 Validation and tests: 101 pytest tests (`tests/`) cover every validation rule, image handling (resize,
      EXIF strip, HEIC, corrupt/oversized), atomic output, base path, CLI exit codes. Each runs against a
      throwaway copy of `sample_content/` broken in one specific way. Known gap: BibTeX errors name the file
      and entry key but not a line number (the parser does not report them).
- [~] 8 Content migration (done Oct 2026, needs human review): old WordPress pages fetched through its REST API and
      converted by one-off scripts (not kept in the repo). Migrated: home text, PI profile + photo, 50 people
      (roles/years/positions parsed from the old People page), 48 publications as `.bib` files (matched to Crossref:
      DOIs for all 48, abstracts for 24, volumes/pages corrected where the old page was wrong, e.g. Aguirre 2024),
      4 resources, 5 courses, join text, funders and logos.
      **Review list:** (1) every person's years/positions; students should add bios and photos (everyone except collaborators gets an automatic minimal profile page to fill in; `content/people/_TEMPLATE.md` is the copy-me example; the old site's class years, awards and "WISP intern" notes were dropped); (2) research themes are
      drafted from the lab's own home/PI text, no figures yet; (3) 3 papers are marked `selected` tentatively;
      (4) `pdf`/`si` links and dataset zips still point to `sites.dartmouth.edu/ccnl/files/...`: they will BREAK when
      the old site is redirected (global redirect), so decide where to host them before launch (e.g. repo files, or
      drop PDF links); (5) Join text is from 2023 (build warns it is stale); stale "next offering" dates for courses
      were dropped; (6) Not migrated: News (17 items, dropped by decision), alumni individual profile pages (one had a
      personal email), media-coverage links (kept as a plain-text note), an Outlook tracking link.
- [~] 7b Design round 2 (Oct 2026): header is a centered nav only; hero card centered on the image with the
      affiliation; selected publications and funders removed from Home; Join moved into Contact; Teaching before
      Resources; SVG logos in the footer (Wikimedia Commons: NSF logo public domain, NIH logo public domain, Dartmouth
      wordmark public domain but marked "trademarked"). TODO: check Dartmouth's identity/brand guidelines before launch
      (is a Dartmouth wordmark on a lab site fine, and which file is official?); NIH/NSF have their own logo-use rules.
      Awards and programs of 7 alumni were moved into their bios.
- [~] 7 Design: layout and visual decisions recorded in `docs/STRUCTURE.md` ("Visual design"); templates, CSS,
      self-hosted fonts and placeholder hero built and checked in a browser (desktop, phone, light and dark).
      Still open: real hero photo and default people photo (placeholders now), fine-tuning publications,
      automated accessibility checks (e.g. axe in CI), print stylesheet review.
- [~] 6 Automation: `deploy.yml` builds, tests and deploys on every push to `main` (skeleton live at
      https://ccnl-dartmouth.github.io/ccnl-website/); failures open/close alert issues (`ccnl/alerts.py`);
      `uptime.yml` (6-hourly) and `links.yml` (weekly, `ccnl/linkcheck.py`) added; see `docs/OPERATIONS.md`.
      Build-failure alert drilled end to end (Oct 2026): a broken person file failed the build, the live site
      stayed up (200), issue #1 opened with the plain-language error, and closed itself on the next good deploy.
      Alerts are tiered (quiet first issue mentioning only the committer; `escalate.yml` mentions the team after
      3 days of build failure or 14 days of dead links, and team + PI after 12 h of site-down).
      Not yet run: `links.yml`, `uptime.yml`, `escalate.yml` (start each once from the Actions tab: Run workflow).
      Still to do by hand: `lab-members` team, variables `ALERT_MENTIONS_TEAM` / `ALERT_MENTIONS_PI`,
      `main` ruleset, UptimeRobot.
- [ ] 2 Content audit (partly done during structure design),
      9 member testing, 10 docs, 11 launch, 12 handover

Dependencies: 3 gates everything after it; 1 runs alongside 2 and 3; 5 and 6 need 4; 7 can start
once 3 is fixed; 9 needs 5, 6, 8; 11 needs the Dartmouth reply (can launch on github.io first).

## Phase 1 substeps

- [x] 1.1 Org name chosen: `ccnl-dartmouth` (`ccnl` and `soltanilab` are taken).
- [x] 1.2 Create the org (Free plan). Currently owned by Peter's personal account with his gmail as
      contact email; change the contact email before handover (org Settings -> Profile).
- [ ] 1.3 Add the PI as owner (deferred); keep owners to 2-3 people. Require 2FA for members
      (do this BEFORE inviting members, or non-2FA members get removed).
- [x] 1.4 Create public repo `ccnl-website`.
- [ ] 1.5 Create team `lab-members` with Write on the repo; org default permission Read; invite members.
- [x] 1.6 Settings -> Pages -> Source: GitHub Actions (done). Enforce HTTPS and custom domain later.
- [ ] 1.7 Ruleset on `main`: block force-push and deletion ONLY. Do not require status checks or pull
      requests: required checks reject direct pushes/web-editor commits, defeating the hands-off design,
      and a failed build already cannot deploy. See `docs/OPERATIONS.md`.
- [x] 1.8 Clone locally (this folder), add `.gitignore`, README stub, this plan, `CLAUDE.md`; first commit; pushed to origin.
- [ ] 1.9 Write `docs/OWNERSHIP.md` (owners, alert email, domain contact, monitor account, offboarding).

## Risks

- Dartmouth declines or delays the hostname: launch on github.io, redirect from the old site.
- Alerts that silently don't fire: test each with a deliberate failure in phase 9.
- Turnover: documentation and the handover checklist keep it running.
