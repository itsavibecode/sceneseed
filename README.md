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
| 0.2.0 | next | Auth (email link + Google), protected dashboard shell |
| 0.3.0 | | Groups CRUD |
| 0.4.0 | | Shows CRUD with public-code generation |
| 0.5.0 | | Public audience submission page (`/s/?c=…`) with character counter |
| 0.5.1 | | Profanity filter + dedupe + window enforcement audited end-to-end |
| 0.6.0 | | Suggestions dashboard (favorite/hide/used/search/filter) |
| 0.7.0 | | Full-screen performer view |
| 0.8.0 | | QR code + ensemble share link with expiry |
| 0.9.0 | | Post-show summary + PNG export |
| 1.0.0 | | Polish, mobile QA, Lighthouse pass |

## Changelog

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
