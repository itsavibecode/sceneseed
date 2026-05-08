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
| 0.5.1 | ✅ shipped | Audience UX polish: live countdown, prominent success state, prompt as visual centerpiece |
| 0.5.2 | ✅ shipped | Cushion direction flipped (+3s grace AFTER close, not before); seconds shown in hour countdowns; matching server grace |
| 0.6.0 | ✅ shipped | Host suggestions feed: live list, filter tabs (All / Favorites / Hidden / Used), search, favorite / hide / mark-used / delete |
| 0.6.1 | ✅ shipped | Show page 2-col layout (Suggestions 3fr + Public code 1fr); mobile header stacks; cleanup |
| 0.6.2 | ✅ shipped | Optional/required first-name collection per show + CSV export per show + dashboard "Past shows" section with downloads |
| 0.7.0 | ✅ shipped | Full-screen performer view (auto-fit text, tap/keyboard nav, favorite + mark-used inline) |
| 0.8.0 | ✅ shipped | Per-show QR code (PNG download) + ensemble share link with auto-expiry |
| 0.8.1 | ✅ shipped | Fix: audience page was restoring "Got it!" success card from browser bfcache on revisit |
| 0.9.0 | next | Post-show summary + PNG export |
| 0.6.0 | | Suggestions dashboard (favorite/hide/used/search/filter) |
| 0.7.0 | | Full-screen performer view |
| 0.8.0 | | QR code + ensemble share link with expiry |
| 0.9.0 | | Post-show summary + PNG export |
| 1.0.0 | | Polish, mobile QA, Lighthouse pass |

## Changelog

### v0.8.1 — 2026-05-08
- **Fix**: audience page was restoring the "Got it! Thanks for the seed" success card on revisit, even when the audience member hadn't typed anything yet. Cause: browsers' back-forward cache (bfcache) snapshots the entire DOM when you navigate away and slaps it back on return — including the toggled visibility of the success card from a previous submit. Symptom: open `/s/?c=<code>`, submit, navigate elsewhere, come back → the success state is still showing.
- **Fix**: added a `pageshow` listener on `s/index.html` that forces the form back to clean state every time the page is shown (initial load AND bfcache restore). Now every visit starts on the empty form, regardless of what the previous tab session looked like.

### v0.8.0 — 2026-05-07
- **QR code per show**: live SVG preview rendered into the Public-code aside on `show.html`, plus a "Download QR (PNG)" button that hands you a 1024×1024 PNG suitable for projecting, printing, or pasting into a flyer. Library: `qrcode@1.5.3` via `esm.run` CDN, wrapped in a tiny local `qr.js`.
- **Ensemble share link**: per-show toggle that exposes a read-only feed at `/view/?c=<publicCode>` for ensemble members (no sign-in needed). Defaults to expiring 24h after `showEndsAt`; host can extend or shorten via a datetime picker. Disabling the toggle revokes immediately.
- **`view/index.html`**: new public-but-restricted page that subscribes live to the suggestions feed when share is active. Hidden suggestions are filtered out for privacy. Shows ★ favorite and ✓ used tags as a quiet recap. Locked screen if share is off or expired.
- **`firestore.rules` updated**: suggestion `list` now allowed when the parent event has `shareEnabled == true && shareExpiresAt > request.time`, in addition to the existing owner-only path. **Re-publish required.**
- Trade-off: the share URL uses the same `publicCode` as the audience submission URL, so audience members technically have the URL while a share is active. Accepted as a feature for an MVP — hosts disable the share when they want the feed private again.

### v0.7.0 — 2026-05-07
- **`perform.html`** — full-screen performer view at `perform.html?code=<publicCode>`. Black background, suggestion text auto-fits to fill the screen via binary-search font-sizing. Built for projecting on a back wall, holding up a phone, or pushing to a TV.
- **Navigation**: tap (or click, or `→`, or space) for next; `←` for previous; `Esc` to exit. `F` toggles favorite, `U` toggles used.
- **Inline actions**: ★ favorite and ○ mark-used buttons in the top-right corner write back to Firestore — same as the dashboard, just bigger and quieter.
- **Filter dropdown**: Active (default — not used, not hidden) / All / ★ Favorites / Not used. Sorts oldest-first so the host walks chronologically through the queue.
- **Auto-fade chrome**: toolbar and keyboard hint fade out after 3s of no interaction so the suggestion text is the only thing on screen during the show. Move/tap to bring them back.
- **Submitter name** appears as a small accent-green caps line above the suggestion when set, perfect for "that's from Sarah!" call-outs.
- **`Perform` button** added to the show detail page hero, right next to Edit / Delete.

### v0.6.2 — 2026-05-07
- **Per-show first-name collection** with three modes (`off` / `optional` / `required`). Set on the show edit dialog (and at creation). Default `off` so existing shows are unchanged. Audience page conditionally shows a name field above the suggestion textarea, labelled `(optional)` or `(required)` to match. Host dashboard shows the submitter's name in italics next to each suggestion card.
- **`firestore.rules` updated** to validate `submitterName`: must be a string ≤ 50 chars, and non-empty if the event's `nameCollection == 'required'`. Existing shows without the field are treated as `'off'` via `event.get('nameCollection', 'off')`. **Re-publish required.**
- **Per-show CSV download** — new "Download CSV" button in the suggestions toolbar exports `Time, Name, Suggestion, Favorite, Hidden, Used` columns. Excel-friendly UTF-8 BOM, CRLF line endings. Filename includes the public code + slugified title + show date.
- **Dashboard "Past shows" section** lists every show whose `showEndsAt` has passed, sorted newest-first across all your groups. Each row has a one-click `Download CSV` plus an `Open` link to revisit the show page. Closest thing to "automatic" without a separate cron worker — your archive is one click away from the dashboard.
- **Privacy policy refreshed** to reflect that names are collected only when a host opts in, and that the field is shown to the host only.

### v0.6.1 — 2026-05-07
- **Show page layout reshuffled.** Suggestions move up to right under the show hero. Suggestions (3fr) and Public code (1fr) live side-by-side in a 2-column grid on desktop (≥900px); on mobile they stack with Suggestions on top. Public code card on desktop is sticky so it stays visible while you scroll a long suggestions list.
- **Mobile header stacks.** Site-wide top bar — brand on its own line, account email + sign-out below it instead of crammed against the logo on narrow screens.
- **Removed `llms.txt` link from the landing-page footer.** It's not a user-facing convention; the file still lives at `/llms.txt` for AI crawlers that go looking.

### v0.6.0 — 2026-05-07
- **Host suggestions feed** lives on `show.html`, replacing the v0.5.x placeholder.
  - Live list via `onSnapshot` — new audience submissions appear instantly without refresh.
  - **Filter tabs:** All / ★ Favorites / Hidden / Used — each shows a count badge that updates live.
  - **Free-text search** filters by case-insensitive substring of suggestion text.
  - **Per-suggestion actions:** ★ favorite, ⊘ hide, ○ mark-used, ✕ delete. All write back to Firestore; visual state on the card (gold tint for favorited, dashed border for hidden, line-through for used) reflects flags immediately.
  - Sorted newest-first client-side (no composite index required).
  - Empty / no-match / search-empty states each get their own copy.
- **`host-suggestions.js`** — new module for owner-side suggestion CRUD, sibling to the existing audience-side `submissions.js`.

### v0.5.2 — 2026-05-07
- **Cushion direction fix.** Previously the form locked 3 seconds *before* the official close. Flipped to 3 seconds *after* — if the show closes at 2:30:00, the audience form keeps working until 2:30:03. The countdown still ticks down to the *official* close (2:30:00 → "0s") and then hides itself; the cushion stays invisible. This matches the original intent: a quiet generosity for late submitters and slow connections.
- **Server grace matches.** `firestore.rules` now allows submissions until `submissionCloseAt + duration.value(3, 's')` so writes during the client cushion actually save. **Re-publish the rules** for this to take effect.
- **Seconds in long countdowns.** Format now shows seconds even in the hour-and-up case: `Closes in 1h 23m 45s` (was `Closes in 1h 23m`).

### v0.5.1 — 2026-05-07
- **Live countdown** under the open-state pill: `Closes in 1h 23m`, `Closes in 12m 45s`, `Closes in 23s`. Updates every second. Goes amber under 60s, red under 10s.
- **Hidden 3-second client cushion** — the audience form locks 3s before the actual server close time so a slow audience doesn't get a confusing rejection from latency. The server still has those extra seconds of grace; we don't tell the audience.
- **Success state replaces the form** — instead of a small "Got it" line below the textarea, a successful submission swaps the whole form for a centered success card (big checkmark, "Got it!" headline, "Send another suggestion" button to swap back).
- **Prompt is now the visual centerpiece** — show title becomes a small uppercase label above the prompt; the prompt itself becomes a serif display headline with an accent rule above it. If no prompt is set, the title falls back to the headline slot. Audience instantly sees "what am I being asked?"

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
