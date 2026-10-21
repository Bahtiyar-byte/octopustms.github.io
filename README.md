# octopustms.com

The LLMP landing page for Octopus TMS (Load Lifecycle Management and Payments), served by GitHub Pages straight from this repo. Pushing to `main` deploys it.

## Editing

All text lives in **`src/strings.py`**, with English and Russian side by side. The page, its Russian twin and the legal pages are generated from it:

```bash
python3 src/build.py      # Python 3 only, no packages needed
```

Then commit the regenerated files together with `src/`.

| Output | Source |
|---|---|
| `index.html`, `ru/index.html` | `src/strings.py` + `src/build.py`. Same page with EN and RU pre-rendered. The flag toggle switches language without a reload and remembers the choice. A Russian browser gets RU by default. |
| `privacy/`, `terms/`, `payment-terms/`, `refund-policy/` | `src/legal/*.md`, which are copies of `docs/legal/*.md` in the octopus app repo. The app copy is canonical: when a legal doc changes there, copy it here and rebuild. |
| `sitemap.xml`, `robots.txt` | Generated. |
| `images/og.jpg` | The link-preview image (1200×630), a screenshot of the hero. Re-take it if the hero changes. |

Links and addresses all live at the top of `src/strings.py`:

| Constant | Value | Used for |
|---|---|---|
| `REGISTER_URL` | app.octopustms.com/register | "Start free" |
| `DEMO_URL` | Brandon's Calendly (30 min) | "Talk to Brandon", "Book 30 min with Brandon" |
| `CONTACT_EMAIL` | ask@octopustms.com | Questions, billing, footer |
| `PARTNERS_EMAIL` | partners@octopustms.com | Partnerships, investors |
| `PRIVACY_EMAIL` | privacy@octopustms.com | Privacy and data requests |

The pricing calculator's defaults (load rate, cut %, loads a month, the $20 fee) are in `CALC`.

## Click counting (PostHog)

Set `POSTHOG_KEY` in `src/strings.py` to the project's public key (starts with `phc_`, safe to publish) and rebuild. Empty means no analytics script loads at all. It runs cookieless (nothing stored in the visitor's browser), records no sessions, respects Do Not Track, and sends only these named events:

| Event | When | Details sent |
|---|---|---|
| `$pageview` | Page opens | — |
| `start_free` | Any "Start free" click | `where` (section) |
| `book_brandon` | Any Calendly link | `where` |
| `email` | Any email link | `to`, `where` |
| `lifecycle_stop` | Tapping a lifecycle stop | `stage` |
| `hear_chaching` | "Hear it" | — |
| `calc_used` | Moving a calculator slider | `field`, `value` |
| `nav`, `legal` | Menu and footer links | `to` |
| `lang_switch`, `theme_toggle` | Flag and moon/sun buttons | `to` |
| `ask_open`, `ask_question`, `ask_error` | The "Ask Brandon" chat | `turn`, `status` |

Every event also carries `lang`. Clicks that leave the page go out by `sendBeacon`, so they're counted even though the browser navigates away.

## "Ask Brandon" chat

A floating chat where an AI answers in Brandon's words. It always says it's an AI and links to the real Brandon's calendar. The site only renders the widget; the answers come from the Octopus backend (`POST /api/public/ask-brandon`, see `docs/features/ASK-BRANDON.md` in the app repo), which holds the API key, rate limits and the daily spend cap.

Turn it on only after that endpoint is live in production: set `ASK_BRANDON_LIVE = True` in `src/strings.py` and rebuild. With `False`, no chat code or button appears on the page.

## The truth rule

Every claim on this site must be true today. Octopus hasn't launched, so: no customer or load counts, no uptime figures, no "hours saved", and no stock or AI-generated photos of Octopus-branded trucks. A real photo of Brandon with his truck is welcome when there is one.

Dark mode follows the visitor's system setting until they press the moon/sun button. After that, their choice is remembered, and the legal pages follow it too.

Old deep links from the six-card page (`#free`, `#one`, `#boards`, `#track`, `#paper`, `#founder`) still work. They scroll to the matching section (`#founder` is now a real section).
