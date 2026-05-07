# SceneSeed

> Audience suggestion collector for improv shows. Hosts create a show, set a submission window, and share a QR code with the audience. Performers see suggestions stream in live.

**Live:** [itsavibecode.github.io/sceneseed](https://itsavibecode.github.io/sceneseed/)

## What it does

SceneSeed gives improv teams a simple way to collect audience suggestions through a show-specific QR code. The submission window is **enforced server-side** — not just on the frontend — so a forged request still gets bounced by Google's clock.

- Admins create improv groups and shows
- Each show has a memorable public code like `coral-2042` and a downloadable QR
- Audiences scan, type a suggestion, submit during the open window
- Duplicate suggestions are rejected automatically (deterministic Firestore doc IDs)
- Performers see suggestions live, can favorite/hide/mark-used, search, and flip to a full-screen view
- A separate ensemble-share link with expiry lets other team members view suggestions read-only

## Stack

- **Frontend:** vanilla HTML / CSS / JavaScript — no framework, no build step
- **Auth:** Firebase Authentication (email link passwordless + Google OAuth)
- **DB:** Firebase Firestore — the submission window is enforced via security rules using `request.time`
- **Hosting:** GitHub Pages
- **Analytics:** Google Analytics 4

## Public code format

Show codes follow `{color}-2###` — for example `coral-2042` or `teal-2007`. The "2" prefix is a decade marker for 2026–2029. Shorter color names are used first, longer color names later in the year-tier (a vintage signal — older shows have longer names).

## Local development

It's a static site. Serve the folder with anything:

```bash
python -m http.server 8098
# then open http://localhost:8098/
```

The Firebase web config is embedded in `firebase-config.js` (public values, safe to commit). Firestore security rules live in `firestore.rules` and are deployed via the Firebase console.

## Deploying Firestore rules

```bash
# one-time
npm install -g firebase-tools
firebase login

# deploy
firebase deploy --only firestore:rules
```

…or paste `firestore.rules` into [the Firebase console](https://console.firebase.google.com/project/sceneseed-336c9/firestore/rules) directly.

## Roadmap

| Version | Status | What lands |
|---|---|---|
| 0.1.0 | ✅ shipped | Landing page, favicon, SEO basics, GA4, privacy page, Firestore rules |
| 0.2.0 | ✅ shipped | Auth (email link + Google), protected dashboard shell, profile auto-create |
| 0.3.0 | ✅ shipped | Groups CRUD — create, list (live), view, edit, delete |
| 0.3.1 | ✅ shipped | Fix: groups list stuck on Loading (composite index avoidance + error logging) |
| 0.4.0 | ✅ shipped | Shows CRUD: create / list / view / edit / delete + auto `color-2###` public-code generator |
| 0.5.0 | ✅ shipped | Public audience submission page (`/s/?c=…`) with character counter, window state, dedup feedback |
| 0.5.1 | | Profanity filter + dedupe + window enforcement audited end-to-end |
| 0.6.0 | | Suggestions dashboard (favorite/hide/used/search/filter) |
| 0.7.0 | | Full-screen performer view |
| 0.8.0 | | QR code + ensemble share link with expiry |
| 0.9.0 | | Post-show summary + PNG export |
| 1.0.0 | | Polish, mobile QA, Lighthouse pass |

## Changelog

### v0.5.0 — 2026-05-07
- **Audience submission page** at `/s/?c={publicCode}` — no login, mobile-first, dark-mode aware
- Reads the show by public code, displays title + prompt + character counter (live)
- Window state pill below the form: `Open · closes 8:30 PM`, `Opens Fri Apr 14, 7:30 PM`, or `Submissions are closed`. Auto-refreshes every 30s so a "before" page flips to "open" without a manual refresh.
- Submit flow: `submissions.js` writes to `/events/{publicCode}/suggestions/{hash}` where `hash` is the first 16 hex chars of SHA-256 of the normalized text — duplicates collide on doc ID, so a re-submission of the same text gets a precise "Someone beat you to that one" message instead of a generic failure.
- All actual enforcement (window times, length cap, manual override) lives in Firestore security rules. The client is just a friendlier face on the same checks.
- **Firestore rules updated** — split suggestion `read` into `get: if true` (so the audience page can do duplicate detection) and `list: if owner` (so the full feed stays private). **Re-publish required.**

### v0.4.0 — 2026-05-07
- **Shows CRUD** — full create / list / view / edit / delete under a group
- `shows.js` data layer with all spec fields (title, venue, prompt, show + submission windows, timezone, manualStatus, max length, profanity + dedupe toggles)
- **Public-code generator** — `{color}-{decade}{NNN}` (e.g. `coral-2042`); collision-checked against existing event docs (up to 12 retries before failing). Color pool grows by year-tier (2026 short colors only, +5-char in 2027, +6-char in 2028, +7-char in 2029); decade digit rolls every 10 years.
- New show dialog with sensible defaults (next 24h start, 90-min run, window opens 30min before, closes 60min after start; user's local timezone auto-detected)
- New `show.html` detail page: prompt, window times, public code, public-URL with copy button, state badge (Open / Opens soon / Closed), Edit + Delete dialogs (Edit also exposes manual override `force_open` / `force_closed`)
- Group page now lists shows under the group as cards with date range, venue, public code, and live state badge
- `windowState()` helper (in `shows.js`) computes the same logic the Firestore rules use, so UI status always agrees with what the server enforces

### v0.3.1 — 2026-05-07
- Fix: dashboard groups list stayed on "Loading…" forever after creating
  a group. The Firestore query combined `where('ownerId','==',uid)` with
  `orderBy('createdAt','desc')`, which requires a composite index that
  wasn't deployed. `onSnapshot` was failing silently with no error callback.
- Dropped the `orderBy` from the query and sort newest-first client-side
  instead — no composite index needed, no extra setup step.
- Added an `onSnapshot` error callback that logs failures and shows the
  empty state instead of leaving the loading spinner up forever.

### v0.3.0 — 2026-05-07
- Groups CRUD: create, list (live via `onSnapshot`), view detail, edit, delete
- `groups.js` data layer — owner-scoped writes guarded by Firestore rules
- Dashboard now shows your groups in a card grid with a "+ New group" modal
- New `group.html` detail page with Edit + Delete modals (shows list placeholder for v0.4.0)
- `<dialog>`-based modals with native backdrop, ESC close, focus management
- Cleanup: removed "Source" link from page footers; tightened privacy policy
  (dropped data-deletion section, removed Firestore/Firebase mentions to reduce
  attack-surface signal — repo source still on GitHub for those who go looking)

### v0.2.0 — 2026-05-07
- Auth: email-link passwordless sign-in (primary) + Google OAuth (secondary)
- `signin.html` with two-option form, magic-link return handler, status messaging
- `dashboard.html` with auth gate, user header, sign-out, and empty state
- `auth.js` shared helpers — every sign-in funnels through `ensureProfile()` to create `/profiles/{uid}` on first login
- Landing-page CTA now reflects auth state ("Sign in to host a show" → "Open dashboard")

### v0.1.0 — 2026-05-07
- Initial scaffold: landing page, privacy page, 404 page, favicon (P5e Line Art), OG image
- Firestore security rules with server-side submission-window enforcement
- Firebase web config wired up (project `sceneseed-336c9`)
- Full SEO meta: canonical, OG, Twitter card, JSON-LD (Organization + WebSite + WebApplication)
- `robots.txt`, `sitemap.xml`, `llms.txt`, `humans.txt`, `site.webmanifest`
- Google Analytics 4 (`G-D04TM51CVE`) wired on every page
- Editorial line-art aesthetic with light/dark color-scheme support
- MIT license

## License

MIT — see [LICENSE](LICENSE)
