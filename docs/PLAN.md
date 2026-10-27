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
- [ ] Reply from web support on whether sites.dartmouth.edu can redirect or only show a "we've moved" page.
- [ ] PI's GitHub username; list of lab members' GitHub usernames.
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
- [~] 6 Automation: `.github/workflows/deploy.yml` builds, tests and deploys to Pages on every push to
      `main` (first version; first run succeeded Oct 2026; skeleton live at
      https://ccnl-dartmouth.github.io/ccnl-website/). Still to do: failure alert emails to the PI/lab, uptime monitor, weekly link
      check, `main` ruleset requiring the build check.
- [ ] 2 Content audit (partly done during structure design), 7 design, 8 migration,
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
- [ ] 1.7 Ruleset on `main`: block force-push and deletion; require the build check, no required reviewers
      (finish after the workflow has run once, phase 6).
- [x] 1.8 Clone locally (this folder), add `.gitignore`, README stub, this plan, `CLAUDE.md`; first commit; pushed to origin.
- [ ] 1.9 Write `docs/OWNERSHIP.md` (owners, alert email, domain contact, monitor account, offboarding).

## Risks

- Dartmouth declines or delays the hostname: launch on github.io, redirect from the old site.
- Alerts that silently don't fire: test each with a deliberate failure in phase 9.
- Turnover: documentation and the handover checklist keep it running.
