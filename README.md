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

Links: "Start free" goes to `https://app.octopustms.com/register` and "Book a 15-min demo" goes to cal.com. Change them in `src/strings.py` (`REGISTER_URL`, `DEMO_URL`).

Dark mode follows the visitor's system setting until they press the moon/sun button. After that, their choice is remembered, and the legal pages follow it too.

Old deep links from the six-card page (`#free`, `#one`, `#boards`, `#track`, `#paper`, `#founder`) still work. They scroll to the matching section.
