# octopustms.com

Single-screen landing page for Octopus TMS, served by GitHub Pages straight from this repo (push to `main` deploys).

## Editing

All text lives in **`src/strings.py`** (English and Russian side by side). The page, its Russian twin and the legal pages are generated from it:

```bash
python3 src/build.py      # Python 3 only, no packages needed
```

Then commit the regenerated files together with `src/`.

| Output | Source |
|---|---|
| `index.html`, `ru/index.html` | `src/strings.py` + `src/build.py` (same page, EN/RU pre-rendered; the flag toggle switches language without a reload) |
| `privacy/`, `terms/`, `payment-terms/`, `refund-policy/` | `src/legal/*.md` — copies of `docs/legal/*.md` in the octopus app repo. The app is canonical: when a legal doc changes there, copy it here and rebuild |
| `sitemap.xml`, `robots.txt` | generated |

Links: "Start free" → `https://app.octopustms.com/register`, "Book a 15-min demo" → cal.com. Change them in `src/strings.py` (`REGISTER_URL`, `DEMO_URL`).

Card deep links work: `octopustms.com/#free`, `#one`, `#boards`, `#track`, `#paper`, `#founder`.
