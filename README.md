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
| `REGISTER_URL` | app.octopustms.com/register | "Open your account" |
| `DEMO_URL` | Brandon's Calendly (30 min) | "Talk to Brandon", "Book 30 min with Brandon" |
| `CONTACT_EMAIL` | ask@octopustms.com | Questions, billing, footer |
| `PARTNERS_EMAIL` | partners@octopustms.com | Partnerships, investors |
| `PRIVACY_EMAIL` | privacy@octopustms.com | Privacy and data requests |

The pricing calculator's defaults (load rate, cut %, loads a month, trucks, loads per truck, the $20 fee) are in `CALC`. The names in the "inside the app" strip are in `WORKS` (text only, no third-party logos).

## The truth rule

Every claim on this site must be true today. Octopus hasn't launched, so: no customer or load counts, no uptime figures, no "hours saved", and no stock or AI-generated photos of Octopus-branded trucks. A real photo of Brandon with his truck is welcome when there is one. No "start free" lures either: the account is free to open, the price is "$20 per load, no load no fee", and the free plan's exact limits are never quoted here because they are set in the app's admin catalog.

Dark mode follows the visitor's system setting until they press the moon/sun button. After that, their choice is remembered, and the legal pages follow it too.

Old deep links from the six-card page (`#free`, `#one`, `#boards`, `#track`, `#paper`, `#founder`) still work. They scroll to the matching section (`#founder` is now a real section).
