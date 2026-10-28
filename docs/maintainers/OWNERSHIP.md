# Who owns what

The one page to read when someone leaves or takes over. Fill in the lines marked **TODO**; everything else is
accurate as of October 2026. Do not put passwords, tokens or recovery codes here: this repository is public.

## People

| Role | Person | Contact | Notes |
|---|---|---|---|
| Main maintainer (day to day) | Peter Duggins | peter.duggins@dartmouth.edu | Created the org and repo; fixes build problems and answers student questions. Leaving eventually: see "Handover". |
| Lab PI, org owner | Alireza Soltani | alireza.soltani@dartmouth.edu | Added to the GitHub org. **TODO:** write his GitHub username here and confirm his role is *Owner*. |
| Lab members | everyone in the team `lab-members` | | Have Write access to the repo. They only edit their own files in `content/`. |

Keep the number of org **owners** to two or three people. Owners can change settings and remove other owners;
Write access is enough for everything members do.

## Accounts and where they live

| What | Where | Owner / login | TODO |
|---|---|---|---|
| GitHub organization | https://github.com/ccnl-dartmouth | owners above | Change the org's contact email (Settings, Profile) from a personal address to a long-lived one (the PI's, or a lab list address). |
| Repository | https://github.com/ccnl-dartmouth/ccnl-website | org | |
| Live site | https://ccnl-dartmouth.github.io/ccnl-website/ | GitHub Pages, built by `deploy.yml` | |
| Alert mentions | repository variables `ALERT_MENTIONS_TEAM` and `ALERT_MENTIONS_PI` | see OPERATIONS.md | **TODO:** set both; record the values' meaning here, not any secret. |
| External uptime monitor | UptimeRobot (planned) | **TODO:** account name, and who owns it | Create it under a lab address, not a personal one; add the PI and the maintainer as alert contacts. |
| Custom domain | none yet (see PLAN.md) | **TODO:** who registers and pays; the registrant must be the PI, the department or the lab | |
| Old site | https://sites.dartmouth.edu/ccnl/ (WordPress) | Dartmouth web support; the PI approved admin access | Redirect or "we've moved" notice still to do (see PLAN.md). |

No passwords or secret tokens are used by the site or its workflows; they run on GitHub's built-in token.

## Where alerts go

See `docs/maintainers/OPERATIONS.md` for the full tiers. In short: a quiet issue first (mentions only the person
who pushed); after a few days the team is mentioned; if the site itself is down for 12 hours, the team and the PI.
Whoever is the maintainer must have email notifications on for mentions.

## Handover (when the maintainer changes or leaves)

1. Make sure the new maintainer is an org **owner**, with two-factor authentication on.
2. Transfer or recreate the external monitor and make them an alert contact; remove the old address.
3. Update this page: people, contact emails, the monitor account.
4. Check that the PI's address in `ALERT_MENTIONS_PI` and the monitor still works.
5. Walk through `docs/maintainers/OPERATIONS.md` once: the alert tiers, the 60-day rule for scheduled workflows,
   and the deliberate-failure test.
6. The new maintainer reads `docs/maintainers/PLAN.md` (decisions and open items) and `STRUCTURE.md` (what is fixed).

## When a lab member leaves

- **Alumni:** in their profile, change `status: current` to `status: alumni` (they move to the Alumni list). Their
  page and papers stay.
- **Access:** remove them from the `lab-members` team when they no longer edit the site (org Settings, Teams).
  Their past commits and their files remain.
- **Photo or data requests:** they can ask to have a profile page hidden (`profile: false`) or removed; the
  history of the repository keeps old versions, which is a reason to keep personal details out of profiles.
