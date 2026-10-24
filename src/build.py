#!/usr/bin/env python3
"""Builds octopustms.com from src/.

    python3 src/build.py

Outputs (all committed, GitHub Pages serves the repo as-is):
  index.html            English LLMP landing page (pre-rendered, toggle to RU without reload)
  ru/index.html         Russian landing page (same template, RU pre-rendered)
  privacy/, terms/, payment-terms/, refund-policy/
                        legal pages rendered from src/legal/*.md, which mirror
                        docs/legal/*.md in the octopus app repo (the app is canonical)
  learn/<slug>/, ru/learn/<slug>/
                        knowledge articles rendered from src/articles/<slug>.<lang>.md,
                        linked from the landing's "Read more" links
  sitemap.xml, robots.txt

No dependencies beyond Python 3.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

from strings import (ASK_BRANDON_LIVE, ASK_BRANDON_URL, CALC, CONTACT_EMAIL, DEMO_URL, EN, PARTNERS_EMAIL,
                     POSTHOG_HOST, POSTHOG_KEY, PRIVACY_EMAIL, REGISTER_URL, RU, SITE, STAGES, WORKS)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
LEGAL_PAGES = [
    # (output dir, markdown file, page title)
    ("privacy", "Privacy-Policy.md", "Privacy Policy"),
    ("terms", "Terms-of-Service.md", "Terms of Service"),
    ("payment-terms", "Payment-Terms.md", "Payment Terms"),
    ("refund-policy", "Refund-and-Cancellation-Policy.md", "Refund & Cancellation Policy"),
]
TODAY = date.today().isoformat()

# --------------------------------------------------------------------------- assets

LOGO_SVG = """<svg class="logo" viewBox="0 0 100 100" width="34" height="34" aria-hidden="true" focusable="false">
<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#1D4ED8"/><stop offset="100%" stop-color="#7C3AED"/></linearGradient></defs>
<circle cx="50" cy="50" r="46" fill="#fff" stroke="#D7DEE8" stroke-width="2"/>
<text x="50" y="52" font-family="Arial, Helvetica, sans-serif" font-size="60" font-weight="bold" fill="url(#lg)" text-anchor="middle" dominant-baseline="central">O</text>
</svg>"""

FLAG_US = """<svg class="flag" viewBox="0 0 20 14" width="20" height="14" aria-hidden="true" focusable="false"><rect width="20" height="14" rx="2" fill="#fff"/><g fill="#B22234"><rect y="0" width="20" height="1.08"/><rect y="2.15" width="20" height="1.08"/><rect y="4.31" width="20" height="1.08"/><rect y="6.46" width="20" height="1.08"/><rect y="8.62" width="20" height="1.08"/><rect y="10.77" width="20" height="1.08"/><rect y="12.92" width="20" height="1.08"/></g><rect width="8.6" height="7.54" fill="#3C3B6E"/><g fill="#fff"><circle cx="1.6" cy="1.5" r=".45"/><circle cx="4.3" cy="1.5" r=".45"/><circle cx="7" cy="1.5" r=".45"/><circle cx="2.95" cy="3.1" r=".45"/><circle cx="5.65" cy="3.1" r=".45"/><circle cx="1.6" cy="4.7" r=".45"/><circle cx="4.3" cy="4.7" r=".45"/><circle cx="7" cy="4.7" r=".45"/><circle cx="2.95" cy="6.2" r=".45"/><circle cx="5.65" cy="6.2" r=".45"/></g></svg>"""

FLAG_RU = """<svg class="flag" viewBox="0 0 20 14" width="20" height="14" aria-hidden="true" focusable="false"><rect width="20" height="14" rx="2" fill="#fff"/><rect y="4.67" width="20" height="4.67" fill="#0039A6"/><path d="M0 9.33h20V12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2z" fill="#D52B1E"/></svg>"""

# --------------------------------------------------------------------------- helpers


def deep_get(d: dict, dotted: str):
    for part in dotted.split("."):
        d = d[part]
    return d


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def resolve(strings: dict, prefix: str) -> dict:
    """Fill any {placeholders} inside strings for a page living at `prefix`."""
    ctx = {
        "img_prefix": prefix,
        "payment_terms_url": f"{prefix}payment-terms/",
        "refund_url": f"{prefix}refund-policy/",
        "demo_url": DEMO_URL,
        "register_url": REGISTER_URL,
    }

    def walk(node):
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, str):
            # Unknown {placeholders} (the calculator's {diff}, {month}...) are left for the page script.
            return node.format_map(_Keep(ctx)) if "{" in node else node
        return node

    return walk(strings)


def json_for_script(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def attr(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- theme

# Colour tokens. The page and the legal pages share them; dark mode is chosen by
# THEME_INIT (saved choice, else the system setting) before first paint.
TOKENS_LIGHT = """--paper:#EEF2F7;--card:#FFFFFF;--card2:#F3F6FA;--ink:#0E1726;--ink2:#3A4556;--muted:#69737F;--line:#D9DFE8;
  --accent:#0A5BFF;--accent-ink:#0646C7;--accent-soft:#E7EEFF;--money:#0E9F6E;--money-soft:#E3F6EE;
  --glow:rgba(10,91,255,.5);--band:#0E1726;--quote:#F4F7FD;color-scheme:light"""
TOKENS_DARK = """--paper:#0A111E;--card:#121B2C;--card2:#1A2539;--ink:#EEF2F7;--ink2:#B7C1D1;--muted:#8693A7;--line:#243049;
  --accent:#3D7BFF;--accent-ink:#8DB2FF;--accent-soft:rgba(61,123,255,.16);--money:#34D399;--money-soft:rgba(52,211,153,.14);
  --glow:rgba(61,123,255,.45);--band:#050A13;--quote:#1A2539;color-scheme:dark"""
THEME_CSS = (
    ":root{" + TOKENS_LIGHT + "}\n"
    ":root[data-theme=\"dark\"]{" + TOKENS_DARK + "}\n"
    "@media (prefers-color-scheme:dark){:root:not([data-theme]){" + TOKENS_DARK + "}}\n"
)
THEME_INIT = (
    "(function(){var t;try{t=localStorage.getItem('octopus.theme')}catch(e){}"
    "if(t!=='dark'&&t!=='light')t=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';"
    "document.documentElement.setAttribute('data-theme',t)})();"
)
THEME_COLOR = {"light": "#EEF2F7", "dark": "#0A111E"}

ICON_MOON = """<svg class="ic-moon" width="17" height="17" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>"""
ICON_SUN = """<svg class="ic-sun" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>"""

# --------------------------------------------------------------------------- landing page

CSS = r"""
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font-family:var(--body);-webkit-text-size-adjust:100%;font-size:16px;scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.45;-webkit-font-smoothing:antialiased;transition:background .3s,color .3s;overflow-x:hidden}
:root{--pad:clamp(16px,5.5vw,80px);--display:'Unbounded','Golos Text',system-ui,sans-serif;--body:'Golos Text',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif}
a{color:var(--accent-ink);text-decoration:none}
a:hover{color:var(--accent)}
h1,h2,h3,p{margin:0}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px;border-radius:6px}
.in{max-width:1440px;margin:0 auto;padding-left:var(--pad);padding-right:var(--pad)}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--accent-ink)}
.display{font-family:var(--display)}
svg{max-width:100%}

/* ---- buttons */
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--accent);color:#fff;font-weight:700;font-size:15px;padding:11px 20px;border-radius:999px;white-space:nowrap;transition:transform .15s,filter .15s}
.btn:hover{color:#fff;filter:brightness(1.1);transform:translateY(-1px)}
.btn::after{content:"→"}
.btn .sm{display:none}
.btn-lg{font-size:16px;padding:14px 24px}
.btn-xl{font-size:17px;padding:16px 28px}
.link{font-weight:600;font-size:15px;color:var(--ink2);white-space:nowrap}
.link:hover{color:var(--accent-ink)}
.ctas{display:flex;flex-wrap:wrap;gap:14px 20px;align-items:center}

/* ---- top bar */
.top{height:72px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:19px;font-family:var(--display);letter-spacing:-.01em;color:var(--ink);white-space:nowrap}
.brand:hover{color:var(--ink)}
.brand .logo{width:38px;height:38px;flex:none}
.nav{display:flex;gap:clamp(14px,1.8vw,28px);margin-right:auto;margin-left:clamp(20px,3vw,48px)}
.nav a{font-weight:600;font-size:15px;color:var(--ink2);white-space:nowrap}
.nav a:hover{color:var(--accent-ink)}
.top-right{display:flex;align-items:center;gap:clamp(10px,1.4vw,18px)}
.lang{display:inline-flex;gap:2px;padding:3px;border:1px solid var(--line);border-radius:999px;background:var(--card)}
.lang button{border:0;background:transparent;font:inherit;font-weight:600;font-size:13px;color:var(--muted);padding:6px 11px;border-radius:999px;display:inline-flex;align-items:center;gap:7px;cursor:pointer;transition:background .15s,color .15s}
.lang button:hover{color:var(--ink)}
.lang button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.flag{border-radius:2px;flex:none}
.theme{width:38px;height:38px;flex:none;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer;display:grid;place-items:center;padding:0}
.theme svg{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.theme .ic-sun{display:none}
[data-theme="dark"] .theme .ic-sun{display:block}
[data-theme="dark"] .theme .ic-moon{display:none}

/* ---- hero */
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:64px;align-items:end;padding-top:64px;padding-bottom:36px}
.hero-l{display:flex;flex-direction:column;gap:22px}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(42px,5.6vw,84px);line-height:1;letter-spacing:-.04em;text-wrap:balance}
.tag{align-self:flex-start;display:inline-block;max-width:100%;font-size:14px;font-weight:600;color:var(--ink2);background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 14px}
.tag b{font-family:var(--display);font-weight:800;color:var(--accent-ink);letter-spacing:.03em}
.money{color:var(--money)}
.price{background:var(--card);border:1px solid var(--line);border-radius:24px;padding:clamp(24px,2.5vw,36px);display:flex;flex-direction:column;gap:20px;box-shadow:0 30px 60px -40px var(--glow)}
.price .motto{color:var(--ink);font-family:var(--display);font-weight:800;font-size:clamp(26px,2.4vw,34px);line-height:1.1;letter-spacing:-.02em}
.price p{font-size:19px;line-height:1.55;color:var(--ink2)}
.price p b{font-family:var(--display);font-size:clamp(30px,2.6vw,38px);color:var(--money);letter-spacing:-.02em;display:block;margin-bottom:4px}
.price .refund{font-size:15px;line-height:1.5;color:var(--muted)}
.price .quote{margin:-6px 0 0;padding-left:16px;border-left:3px solid var(--money)}
.price .quote p{font-size:16.5px;line-height:1.5;font-style:italic;color:var(--ink2)}
.price .quote cite{display:block;margin-top:6px;font-style:normal;font-size:13.5px;font-weight:600;color:var(--muted)}
.price .quote cite::before{content:"— "}

/* ---- hero animation: the load comes in from the boards, everything happens inside, the money comes in from the broker */
.hero-anim{display:block;width:100%;max-width:720px;height:auto;overflow:visible;font-family:var(--body);margin-top:4px}
.hero-anim .lbl{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;fill:var(--muted)}
.hero-anim .lbl2{font-size:11.5px;font-weight:600;fill:var(--muted)}
.hero-anim .num{font-size:11px;font-weight:700;fill:var(--ink)}

/* ---- inside the app */
.works{padding-top:0;padding-bottom:60px;display:flex;flex-wrap:wrap;align-items:center;gap:14px 32px}
.works ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px 32px}
.works li{display:flex;flex-direction:column;gap:1px}
.works b{font-family:var(--display);font-weight:700;font-size:17px;letter-spacing:-.01em;color:var(--ink)}
.works span{font-size:12.5px;font-weight:600;color:var(--muted)}
.works li.lead b,.works li.lead span{color:var(--accent-ink)}
.works a.eyebrow::after{content:" →"}

/* ---- lifecycle */
.band{background:var(--band);color:#fff;padding:64px 0 72px;scroll-margin-top:0}
.band-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 24px;margin-bottom:28px}
.band .eyebrow{color:#8DB2FF}
.band .chain{font-size:14px;color:#8693A7}
.spine{display:block;width:100%;height:auto;overflow:visible;font-family:var(--body)}
.stops{list-style:none;margin:8px 0 0;padding:0;display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:12px}
.stop{padding:16px 14px;border-radius:14px;display:flex;flex-direction:column;gap:8px;transition:background .2s}
.stop:hover{background:rgba(255,255,255,.06)}
.stop .name{font-family:var(--display);font-weight:700;font-size:16px}
.stop .desc{font-size:13.5px;line-height:1.5;color:#B7C1D1}
.stop .dot{display:none}
.stop.paid{background:rgba(52,211,153,.12);box-shadow:inset 0 0 0 1.5px #34D399}
.stop.paid .name{font-weight:800;color:#34D399}
.stop.paid .desc{color:#E3F6EE}
.stop.archived .name{color:#B7C1D1}
.stop.archived .desc{color:#8693A7}
.ching{display:none}

/* ---- why */
.why{display:grid;grid-template-columns:260px minmax(0,1fr);gap:64px;padding-top:112px;scroll-margin-top:24px}
.why .eyebrow{padding-top:10px}
.why-body{display:flex;flex-direction:column;gap:26px;max-width:860px}
.why .p1{font-family:var(--display);font-weight:600;font-size:clamp(22px,2.1vw,30px);line-height:1.35;letter-spacing:-.015em;text-wrap:pretty}
.why .p{font-size:clamp(18px,1.5vw,21px);line-height:1.6;color:var(--ink2);text-wrap:pretty}
.why .p4{font-size:clamp(20px,1.7vw,24px);line-height:1.5;font-weight:600}
.sonar{position:relative;height:clamp(280px,26.4vw,380px);display:flex;align-items:center;justify-content:center;overflow:hidden}
.sonar svg{position:absolute;inset:0;width:100%;height:100%}
.sonar p{position:relative;font-family:var(--display);font-weight:800;font-size:clamp(30px,4vw,58px);letter-spacing:-.03em;text-align:center;line-height:1.05;background:var(--paper);padding:10px 24px;border-radius:16px;max-width:calc(100% - 2*var(--pad));text-wrap:balance;transition:background .3s}

/* ---- SASR */
.sasr{padding-top:40px;padding-bottom:104px;scroll-margin-top:24px}
.sasr-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 20px;margin-bottom:36px}
.sasr h2{flex:none;font-family:var(--display);font-weight:800;font-size:clamp(34px,3.1vw,44px);letter-spacing:-.025em;white-space:nowrap}
.sasr h2 span{font-weight:600;font-size:clamp(17px,1.55vw,22px);color:var(--muted);letter-spacing:-.01em}
.rules{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.rule{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:30px;display:flex;flex-direction:column;gap:22px}
.rule-text{display:flex;flex-direction:column;gap:12px;min-width:0}
.rule p{font-size:clamp(19px,1.5vw,21px);line-height:1.4;font-weight:600}
.rule .how{font-size:15px;line-height:1.55;font-weight:400;color:var(--muted);text-wrap:pretty}
.sasr .close{margin-top:44px;font-family:var(--display);font-weight:600;font-size:clamp(21px,2vw,28px);line-height:1.35;letter-spacing:-.015em;max-width:1020px;text-wrap:pretty}
.sasr .more{display:inline-block;margin-top:22px}
.hl{color:var(--accent-ink)}

/* ---- "Read more" into a /learn/ article; the arrow is CSS, like the other links */
a.more{font-weight:700;font-size:15px;align-self:flex-start}
a.more::after{content:" →"}
.band .more{display:inline-block;margin-top:22px;color:#8DB2FF}
.band .more:hover{color:#fff}

/* ---- the standard */
.std{background:var(--card);border-top:1px solid var(--line);border-bottom:1px solid var(--line);scroll-margin-top:0;transition:background .3s}
.std .in{padding-top:96px;padding-bottom:96px;display:grid;grid-template-columns:minmax(0,1fr) 560px;gap:72px;align-items:center}
.std-text{display:flex;flex-direction:column;gap:22px}
.std h2{font-family:var(--display);font-weight:800;font-size:clamp(34px,3.4vw,48px);line-height:1.05;letter-spacing:-.03em}
.std p{font-size:clamp(18px,1.5vw,21px);line-height:1.6;color:var(--ink2);text-wrap:pretty}
.plate{display:block;width:100%;max-width:560px;height:auto;font-family:var(--body);justify-self:center}

/* ---- end + footer */
.end{padding-top:88px;padding-bottom:40px;display:flex;flex-direction:column;align-items:center;gap:30px;text-align:center}
.end p{font-size:clamp(19px,1.7vw,24px);line-height:1.5;font-style:italic;color:var(--ink2);max-width:760px;text-wrap:balance}
.end .ctas{justify-content:center}
.foot{border-top:1px solid var(--line)}
.foot .in{min-height:56px;padding-top:12px;padding-bottom:12px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 16px;font-size:13px;color:var(--muted)}
.foot nav{display:flex;flex-wrap:wrap;gap:6px 16px}
.foot a{color:var(--muted)}
.foot a:hover{color:var(--ink)}

/* ---- lifecycle: interactive */
.band-head .hint{font-size:14px;color:#8DB2FF;font-weight:600}
.band-head .hint::before{content:"👆 "}
.stop-btn{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:8px;cursor:pointer;width:100%}
.stop-btn:focus-visible{outline:3px solid #8DB2FF;outline-offset:8px;border-radius:8px}
.stop{cursor:pointer}
.stop.on{background:rgba(61,123,255,.18);box-shadow:inset 0 0 0 1.5px #3D7BFF}
.stop.paid.on{background:rgba(52,211,153,.22);box-shadow:inset 0 0 0 2px #34D399}
.stop .more{display:none}
.detail{margin-top:20px;border-radius:18px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);padding:24px 28px;display:grid;grid-template-columns:190px minmax(0,1fr) auto;gap:24px;align-items:center;min-height:118px}
.detail h3{font-family:var(--display);font-weight:800;font-size:26px;letter-spacing:-.02em;color:#fff}
.detail.is-paid h3{color:#34D399}
.detail p{font-size:17px;line-height:1.6;color:#D5DCE7;max-width:820px}
.hear{border:0;font:inherit;font-weight:700;font-size:15px;color:#052e16;background:#34D399;border-radius:999px;padding:11px 18px;cursor:pointer;display:none;align-items:center;gap:8px;white-space:nowrap}
.hear:hover{filter:brightness(1.08)}
.hear svg{width:18px;height:18px;fill:currentColor}
.detail.is-paid .hear{display:inline-flex}
.hear.ringing{animation:ring .55s ease-out}
@keyframes ring{0%{transform:none}25%{transform:scale(1.1) rotate(-4deg)}55%{transform:scale(1.05) rotate(4deg)}100%{transform:none}}

/* ---- section headings shared by pricing, who, founder, contact */
.h2{font-family:var(--display);font-weight:800;font-size:clamp(32px,3.2vw,46px);line-height:1.05;letter-spacing:-.03em;text-wrap:balance}
.lead{font-size:clamp(18px,1.4vw,20px);line-height:1.6;color:var(--ink2);text-wrap:pretty}

/* ---- pricing calculator */
.calc{padding-top:104px;padding-bottom:24px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:clamp(36px,5vw,72px);align-items:start;scroll-margin-top:24px}
.calc-text{display:flex;flex-direction:column;gap:18px}
.tiles{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;margin-top:6px}
.tile{border:1px solid var(--line);border-radius:16px;padding:16px 18px;background:var(--card);display:flex;flex-direction:column;gap:6px}
.tile strong{font-size:15.5px}
.tile span{font-size:14.5px;line-height:1.5;color:var(--ink2)}
.tile.us{border-color:var(--money);background:var(--money-soft)}
.tile.us strong{color:var(--money)}
.machine{background:var(--card);border:1px solid var(--line);border-radius:24px;padding:clamp(22px,2.4vw,34px);display:flex;flex-direction:column;gap:20px;box-shadow:0 30px 60px -44px var(--glow)}
.field{display:flex;flex-direction:column;gap:8px}
.field-top{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.field label{font-weight:600;font-size:15px;color:var(--ink2)}
.field output{font-family:var(--display);font-weight:700;font-size:22px;letter-spacing:-.01em}
.field input{width:100%;margin:0;height:28px;background:transparent;cursor:pointer;-webkit-appearance:none;appearance:none;--fill:50%}
.field input::-webkit-slider-runnable-track{height:6px;border-radius:99px;background:linear-gradient(var(--accent),var(--accent)) 0 0/var(--fill) 100% no-repeat,var(--line)}
.field input::-webkit-slider-thumb{-webkit-appearance:none;width:24px;height:24px;border-radius:50%;background:var(--card);border:3px solid var(--accent);margin-top:-9px;box-shadow:0 2px 8px rgba(0,0,0,.18)}
.field input::-moz-range-track{height:6px;border-radius:99px;background:var(--line)}
.field input::-moz-range-progress{height:6px;border-radius:99px;background:var(--accent)}
.field input::-moz-range-thumb{width:18px;height:18px;border-radius:50%;background:var(--card);border:3px solid var(--accent)}
.bars{display:flex;flex-direction:column;gap:12px;padding-top:18px;border-top:1px solid var(--line)}
.bar{display:grid;grid-template-columns:124px minmax(0,1fr) 96px;gap:12px;align-items:center;font-size:15px;font-weight:600}
.bar .track{height:14px;border-radius:99px;background:var(--card2);overflow:hidden}
.bar .fill{display:block;height:100%;border-radius:99px;background:#EF4444;transition:width .3s ease}
.bar.us .fill{background:var(--money)}
.bar b{text-align:right;font-family:var(--display);font-size:18px}
.bar.them b{color:#EF4444}
.bar.us b{color:var(--money)}
.result{font-size:clamp(19px,1.6vw,22px);line-height:1.45;font-weight:600}
.result b{color:var(--money);font-family:var(--display);white-space:nowrap}
.result-month{font-size:16px;line-height:1.55;color:var(--ink2)}
.result-month b{color:var(--ink);white-space:nowrap}
.fine{font-size:13.5px;line-height:1.55;color:var(--muted)}
.mode{display:inline-flex;gap:4px;padding:4px;border:1px solid var(--line);border-radius:999px;background:var(--card2);align-self:flex-start;max-width:100%}
.mode button{border:0;background:transparent;font:inherit;font-weight:700;font-size:14px;color:var(--muted);padding:8px 16px;border-radius:999px;cursor:pointer;white-space:nowrap;transition:background .15s,color .15s}
.mode button:hover{color:var(--ink)}
.mode button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.machine[data-mode="own"] .f-fleet,.machine[data-mode="fleet"] .f-own{display:none}
.machine[data-mode="fleet"] .bar.them .fill{background:var(--ink2)}
.machine[data-mode="fleet"] .bar.them b{color:var(--ink)}
.leased{font-size:15px;line-height:1.55;color:var(--ink2);border-top:1px solid var(--line);padding-top:16px}

/* ---- one load, two screens */
.two{padding-top:88px;padding-bottom:8px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:clamp(32px,5vw,72px);align-items:center;scroll-margin-top:24px}
.two-text{display:flex;flex-direction:column;gap:18px}
.screens{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:14px;align-items:center}
.screen{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:18px 20px 10px;display:flex;flex-direction:column;box-shadow:0 30px 60px -44px var(--glow)}
.screen .role{font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.screen.driver .role{color:var(--money)}
.screen .ld{font-weight:700;font-size:15px;padding-bottom:12px}
.row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:14.5px;color:var(--ink2);padding:9px 0;border-top:1px solid var(--line)}
.row b{font-family:var(--display);font-weight:700;color:var(--ink);white-space:nowrap}
.row.big b{font-size:24px;color:var(--money);letter-spacing:-.02em}
.row .pdf{display:inline-flex;align-items:center;gap:6px}
.row .pdf::before{content:"";width:10px;height:12px;border:1.5px solid var(--muted);border-radius:2px;display:inline-block}
.eq{font-family:var(--display);font-weight:800;font-size:38px;color:var(--money);text-align:center;line-height:1}

/* ---- who it's for */
.who{padding-top:72px;padding-bottom:16px;scroll-margin-top:24px}
.who .eyebrow{display:block;margin-bottom:22px}
.cards{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:28px;display:flex;flex-direction:column;gap:12px}
.card h3{font-family:var(--display);font-weight:700;font-size:22px;letter-spacing:-.02em}
.card p{font-size:16.5px;line-height:1.55;color:var(--ink2);flex:1}
.card a{font-weight:700;font-size:15px}
.card a::after{content:" →"}

/* ---- founder */
.why h2{margin-bottom:4px}
.why .p0{font-size:clamp(18px,1.5vw,21px);line-height:1.6;color:var(--ink)}
.sign{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px;margin-top:6px}
.mono{width:52px;height:52px;border-radius:50%;display:grid;place-items:center;background:var(--ink);color:var(--paper);font-family:var(--display);font-weight:800;font-size:18px;letter-spacing:.02em;flex:none}
.sign strong{font-size:17px}
.sign a{font-weight:700}

/* ---- SASR status note */
.sasr .note{font-size:13.5px;font-weight:600;color:var(--muted);border:1px dashed var(--line);border-radius:999px;padding:5px 12px;white-space:nowrap}

/* ---- contact */
.contact{padding-top:96px;padding-bottom:16px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:clamp(32px,5vw,64px);align-items:start;scroll-margin-top:24px}
.contact-text{display:flex;flex-direction:column;gap:16px}
.lines{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.lines a{display:flex;flex-direction:column;gap:4px;height:100%;padding:18px 20px;border:1px solid var(--line);border-radius:16px;background:var(--card);color:var(--ink);transition:border-color .15s,transform .15s}
.lines a:hover{border-color:var(--accent);color:var(--ink);transform:translateY(-1px)}
.lines strong{font-size:15.5px}
.lines span{font-size:15px;color:var(--accent-ink);font-weight:600;overflow-wrap:anywhere}
.lines .call a{background:var(--accent);border-color:var(--accent);color:#fff}
.lines .call a:hover{color:#fff}
.lines .call span{color:#DCE7FF;font-weight:500}

/* ---- medium screens */
@media (max-width:1180px){
  .std .in{grid-template-columns:1fr;gap:48px}
}
@media (max-width:1180px){
  .nav{display:none}
}
@media (max-width:1080px){
  /* The spine turns vertical: one stop per row, the rail on the left. */
  .spine{display:none}
  .detail{display:none}
  .stop.on .more{display:flex;flex-direction:column;align-items:flex-start;gap:12px;margin-top:10px;font-size:15px;line-height:1.6;color:#D5DCE7}
  .stop.paid.on .hear{display:inline-flex}
  .band .chain{display:none}
  .stops{grid-template-columns:1fr;gap:0;margin:0}
  .stop{position:relative;padding:14px 16px 18px 60px;border-radius:14px}
  .stop .dot{display:grid;place-items:center;position:absolute;left:10px;top:12px;width:28px;height:28px;border-radius:50%;background:var(--band);border:2.5px solid rgba(255,255,255,.4);color:#8DB2FF;font-size:11px;font-weight:700;z-index:1}
  .stop::after{content:"";position:absolute;left:22px;top:40px;bottom:-12px;width:4px;background:#3D7BFF}
  .stop.proven::after{background:linear-gradient(#3D7BFF,#34D399)}
  .stop.paid::after{background:rgba(255,255,255,.16)}
  .stop.archived::after{display:none}
  .stop.paid{margin:6px 0}
  .stop.paid .dot{background:#34D399;border:0;color:#052e16;font-family:var(--display);font-size:15px;font-weight:800;width:34px;height:34px;left:7px;top:10px;box-shadow:0 0 0 6px rgba(52,211,153,.18);animation:ping 3s ease-out infinite}
  .stop.archived .dot{border-style:dashed;border-color:rgba(255,255,255,.25);color:#8693A7}
  .stop .name{display:flex;align-items:baseline;gap:12px}
  .ching{display:inline;font-family:var(--body);font-size:15px;font-style:italic;font-weight:700;color:#34D399;opacity:0;animation:ching 3s ease-out infinite}
}
@keyframes ping{0%{box-shadow:0 0 0 6px rgba(52,211,153,.18),0 0 0 6px rgba(52,211,153,.6)}70%{box-shadow:0 0 0 6px rgba(52,211,153,.18),0 0 0 26px rgba(52,211,153,0)}100%{box-shadow:0 0 0 6px rgba(52,211,153,.18),0 0 0 26px rgba(52,211,153,0)}}
@keyframes ching{0%,8%{opacity:0;transform:translateY(4px)}14%,70%{opacity:1;transform:none}85%,100%{opacity:0}}
@media (max-width:960px){
  .top .link-demo{display:none}
  .hero{grid-template-columns:1fr;gap:36px;padding-top:40px;padding-bottom:28px}
  .works{padding-bottom:48px}
  .calc,.contact{grid-template-columns:1fr;padding-top:80px}
  .two{grid-template-columns:1fr;padding-top:72px}
  .works{gap:10px 20px}
  .works ul{gap:8px 20px}
  .cards{grid-template-columns:1fr}
  .why{grid-template-columns:1fr;gap:18px;padding-top:80px}
  .why .eyebrow{padding-top:0}
  .rules{grid-template-columns:1fr}
  .rule{flex-direction:row;align-items:flex-start;gap:20px;padding:22px}
  .rule svg{flex:none;width:60px;height:60px;margin-top:-4px}
  .sasr{padding-bottom:72px}
  .std .in{padding-top:72px;padding-bottom:72px}
  .end{padding-top:64px}
}
@media (max-width:720px){
  .top .link{display:none}
  .lang button span{display:none}
  .lang button{padding:7px 9px}
  .top .btn{padding:9px 14px;font-size:14px}
  .sasr h2{white-space:normal}
  .sasr h2 span{display:block;margin-top:6px}
  .foot .in{justify-content:center;text-align:center}
  .lines{grid-template-columns:1fr}
  .top .link-demo{display:none}
  .top .btn .sm{display:inline}
  .mode{display:flex;width:100%;align-self:stretch}
  .mode button{flex:1;white-space:normal;padding:8px 8px;font-size:13px;line-height:1.25}
  .foot nav{justify-content:center}
  .hero-anim .sm{display:none}
  /* Zoom the animation to the box; the load and the money arrive from beyond the screen edge. */
  .anim-wrap{overflow:hidden}
  .hero-anim{width:150%;max-width:none;margin-left:-25%}
  .top .btn .lg{display:none}
  .screens{grid-template-columns:1fr;gap:10px}
  .eq{font-size:30px}
  .mode button{padding:8px 12px;font-size:13.5px}
}
@media (max-width:440px){
  .brand{font-size:16px;gap:8px}
  .brand .logo{width:32px;height:32px}
  .theme{display:none}
  .brand .tms{display:none}
  .top .btn{padding:9px 11px;font-size:13.5px}
  .lang button{padding:6px 6px}
}
@media (max-width:400px){
  .top .btn::after{content:none}
  .top-right{gap:6px}
  .lang button{padding:6px 5px}
  .top .btn{padding:9px 10px}
  .tiles{grid-template-columns:1fr}
  .bar{grid-template-columns:76px minmax(0,1fr) 80px;gap:8px}
  .top-right{gap:8px}
  .rule{flex-direction:column;align-items:flex-start}
  .rule svg{margin-top:0}
}
@media (max-width:340px){
  .brand .logo{display:none}
  .top .btn{padding:8px 8px}
}
/* ---- partners */
.partners{padding-top:96px;padding-bottom:16px;scroll-margin-top:24px}
.partners-head{display:flex;flex-direction:column;gap:14px;max-width:860px;margin-bottom:32px}
.pgrid{list-style:none;margin:0;padding:0;display:grid;gap:16px}
.pgrid.big{grid-template-columns:repeat(3,minmax(0,1fr))}
.pgrid.small{grid-template-columns:repeat(4,minmax(0,1fr))}
.hood-head{display:flex;flex-direction:column;gap:10px;max-width:860px;margin:44px 0 20px}
.hood-head .lead{font-size:clamp(17px,1.3vw,19px)}
.pcard{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:26px;display:flex;flex-direction:column;gap:12px}
.pcard.live{border-color:var(--money);box-shadow:0 24px 50px -40px var(--money)}
.mark{font-family:var(--display);font-weight:800;font-size:28px;line-height:1.1;letter-spacing:-.02em;color:var(--ink)}
.mark small{display:block;font-family:var(--body);font-weight:600;font-size:13px;letter-spacing:0;color:var(--muted);margin-top:4px}
.small .mark{font-size:20px}
.small .pcard{padding:22px}
.chip{align-self:flex-start;display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:700;border-radius:999px;padding:5px 11px;background:var(--card2);color:var(--ink2)}
.chip::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor;flex:none}
.chip.live{background:var(--money-soft);color:var(--money)}
.chip.live::before{animation:live 2s ease-in-out infinite}
.chip.prog{background:var(--accent-soft);color:var(--accent-ink)}
.chip.next{background:rgba(245,158,11,.14);color:#B45309}
[data-theme="dark"] .chip.next{color:#FBBF24}
@keyframes live{0%,100%{opacity:1}50%{opacity:.35}}
.pcard p{font-size:15.5px;line-height:1.55;color:var(--ink2)}
.small .pcard p{font-size:14.5px}
.pjoin{margin-top:26px;font-size:17px;font-weight:600}
.pfine{margin-top:12px;font-size:13px;line-height:1.55;color:var(--muted);max-width:900px}
.h2{-webkit-hyphens:auto;hyphens:auto;overflow-wrap:break-word}
@media (max-width:1080px){.pgrid.small{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:960px){.pgrid.big{grid-template-columns:minmax(0,1fr)}.partners{padding-top:80px}}
@media (max-width:440px){
  .pgrid.small{grid-template-columns:minmax(0,1fr)}
  .mark{font-size:24px}
  .pcard,.small .pcard{padding:20px}
  .h2{font-size:28px}
}
@media (max-width:360px){.h2{font-size:25px}.sasr .note{white-space:normal}}
/* Just above the nav's breakpoint the bar is too crowded for the "Talk to Brandon" link; Russian labels are longer. */
@media (max-width:1300px){.top .link-demo{display:none}}
@media (max-width:1439px){html[lang="ru"] .top .link-demo{display:none}}

/* ---- ask brandon (AI chat) */
.ask-fab{position:fixed;right:20px;bottom:20px;z-index:40;display:inline-flex;align-items:center;gap:10px;border:0;border-radius:999px;padding:7px 18px 7px 7px;background:var(--ink);color:var(--paper);font:inherit;font-weight:700;font-size:15px;cursor:pointer;box-shadow:0 18px 40px -16px rgba(14,23,38,.55);transition:transform .15s}
.ask-fab:hover{transform:translateY(-2px)}
.ask-fab .mono{width:38px;height:38px;font-size:13px;background:var(--accent);color:#fff}
.ask-fab[hidden],.ask[hidden]{display:none}
.ask{position:fixed;right:20px;bottom:20px;z-index:41;width:min(400px,calc(100vw - 32px));height:min(620px,calc(100dvh - 40px));background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:22px;box-shadow:0 40px 90px -30px rgba(14,23,38,.55);display:flex;flex-direction:column;overflow:hidden}
.ask-head{display:flex;gap:12px;align-items:flex-start;padding:16px 14px 12px 16px;border-bottom:1px solid var(--line)}
.ask-head .mono{width:40px;height:40px;font-size:14px}
.ask-head strong{display:block;font-size:16px}
.ask-head small{display:block;font-size:12.5px;line-height:1.45;color:var(--muted)}
.ask-x{margin-left:auto;border:0;background:transparent;color:var(--ink2);font-size:22px;line-height:1;width:34px;height:34px;border-radius:50%;cursor:pointer;flex:none}
.ask-x:hover{background:var(--card2)}
.ask-log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;overscroll-behavior:contain}
.msg{max-width:86%;padding:10px 14px;border-radius:16px;font-size:15px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}
.msg.bot{background:var(--card2);border-bottom-left-radius:6px;align-self:flex-start}
.msg.me{background:var(--accent);color:#fff;border-bottom-right-radius:6px;align-self:flex-end}
.msg.err{background:rgba(239,68,68,.1)}
.msg.typing{color:var(--muted);font-style:italic}
.ask-chips{display:flex;flex-wrap:wrap;gap:8px}
.ask-chips button{border:1px solid var(--line);background:var(--card);color:var(--accent-ink);font:inherit;font-size:13.5px;font-weight:600;padding:7px 12px;border-radius:999px;cursor:pointer}
.ask-chips button:hover{border-color:var(--accent)}
.ask-form{display:flex;gap:8px;padding:12px 12px 6px;border-top:1px solid var(--line)}
.ask-form textarea{flex:1;resize:none;border:1px solid var(--line);border-radius:14px;background:var(--paper);color:var(--ink);font:inherit;font-size:16px;line-height:1.4;padding:10px 12px;height:46px;max-height:120px}
.ask-form button{border:0;border-radius:14px;background:var(--accent);color:#fff;font:inherit;font-weight:700;font-size:15px;padding:0 16px;cursor:pointer}
.ask-form button:disabled{opacity:.5;cursor:default}
.ask-note{padding:0 14px 10px;font-size:11.5px;color:var(--muted)}
@media (max-width:520px){
  .ask{right:0;bottom:0;width:100vw;height:88dvh;border-radius:22px 22px 0 0}
  .ask-fab{right:14px;bottom:14px;padding:7px}
  .ask-fab .lbl{display:none}
}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation:none!important;transition:none!important}
  .ching{opacity:1}
}
"""

JS = r"""
(function(){
  var STR = JSON.parse(document.getElementById('i18n').textContent);
  var root = document.documentElement;
  var lang = root.lang === 'ru' ? 'ru' : 'en';
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  var COLORS = __THEME_COLORS__;

  function t(key, l){ return key.split('.').reduce(function(o,k){ return o == null ? o : o[k]; }, STR[l]); }
  function tpl(key, vars){ return String(t(key, lang) || '').replace(/\{(\w+)\}/g, function(m, k){ return vars[k] != null ? vars[k] : m; }); }
  function setHTML(id, v){ var el = document.getElementById(id); if (el) el.innerHTML = v; }
  var REDUCED = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  // ---- cha-ching: synthesized on the spot (no audio file), only ever after a tap.
  var ac = null;
  function chaChing(){
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) {
        ac = ac || new AC();
        if (ac.state === 'suspended') ac.resume();
        var now = ac.currentTime + .02, out = ac.createGain();
        out.gain.value = .9; out.connect(ac.destination);
        // "cha": a short bright burst, like a register drawer
        var len = Math.floor(ac.sampleRate * .07), buf = ac.createBuffer(1, len, ac.sampleRate), d = buf.getChannelData(0);
        for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2);
        var nz = ac.createBufferSource(), hp = ac.createBiquadFilter(), ng = ac.createGain();
        nz.buffer = buf; hp.type = 'highpass'; hp.frequency.value = 2500; ng.gain.value = .35;
        nz.connect(hp); hp.connect(ng); ng.connect(out); nz.start(now);
        // "ching": two bell strikes, each a tone plus a bright overtone
        [[1568, .09], [2093, .2]].forEach(function(note){
          [[1, .24, 1.2], [2.76, .07, .4]].forEach(function(part){
            var o = ac.createOscillator(), g = ac.createGain(), t0 = now + note[1];
            o.type = 'sine'; o.frequency.value = note[0] * part[0];
            g.gain.setValueAtTime(.0001, t0);
            g.gain.exponentialRampToValueAtTime(part[1], t0 + .008);
            g.gain.exponentialRampToValueAtTime(.0001, t0 + part[2]);
            o.connect(g); g.connect(out); o.start(t0); o.stop(t0 + part[2] + .05);
          });
        });
      }
    } catch (e) {}
    document.querySelectorAll('.hear').forEach(function(b){ b.classList.remove('ringing'); void b.offsetWidth; b.classList.add('ringing'); });
  }
  document.querySelectorAll('.hear').forEach(function(b){
    b.addEventListener('click', function(e){ e.stopPropagation(); chaChing(); });
  });

  // ---- lifecycle: tap a stop to read what happens there. Until the first tap, it walks itself.
  var stops = Array.prototype.slice.call(document.querySelectorAll('.stop[data-stage]'));
  var detail = document.getElementById('detail');
  var current = 'found', timer = null, touched = false, visible = false;
  function select(key){
    current = key;
    stops.forEach(function(li){
      var on = li.getAttribute('data-stage') === key;
      li.classList.toggle('on', on);
      var b = li.querySelector('.stop-btn'); if (b) b.setAttribute('aria-expanded', String(on));
    });
    if (detail) {
      detail.classList.toggle('is-paid', key === 'paid');
      setHTML('detail-name', t('life.' + key + '.0', lang));
      setHTML('detail-text', t('life.' + key + '.2', lang));
    }
  }
  function stopWalk(){ if (timer) { clearInterval(timer); timer = null; } }
  function walk(){
    if (timer || touched || REDUCED || !visible) return;
    timer = setInterval(function(){
      var i = stops.findIndex(function(li){ return li.getAttribute('data-stage') === current; });
      select(stops[(i + 1) % stops.length].getAttribute('data-stage'));
    }, 3600);
  }
  stops.forEach(function(li){
    var b = li.querySelector('.stop-btn');
    if (!b) return;
    b.addEventListener('click', function(){
      touched = true; stopWalk();
      var key = li.getAttribute('data-stage');
      select(key);
      if (key === 'paid') chaChing();
    });
  });
  var band = document.getElementById('lifecycle');
  if (band && 'IntersectionObserver' in window) {
    new IntersectionObserver(function(es){
      visible = es[0].isIntersecting;
      if (visible) walk(); else stopWalk();
    }, {threshold: .35}).observe(band);
  }

  // ---- pricing, live. Two ways to read it:
  //   own   — your own authority: a dispatch/umbrella percentage vs our $20 on the same load
  //   fleet — trucks under your MC: what Octopus costs a month next to what the trucks bring in
  var CALC = __CALC__;
  var money = function(n){ return '$' + Math.round(n).toLocaleString('en-US'); };
  var machine = document.getElementById('machine');
  var mode = 'own';
  var inRate = document.getElementById('c-rate'), inPct = document.getElementById('c-pct'), inLoads = document.getElementById('c-loads'),
      inTrucks = document.getElementById('c-trucks'), inPer = document.getElementById('c-per');
  var sliders = [inRate, inPct, inLoads, inTrucks, inPer];
  function fill(el){ if (el) el.style.setProperty('--fill', ((el.value - el.min) / (el.max - el.min) * 100) + '%'); }
  function width(part, whole){ var fu = document.getElementById('f-us'); if (fu) fu.style.width = Math.max(2, Math.min(100, part / whole * 100)) + '%'; }
  function calc(){
    if (!inRate) return;
    var r = +inRate.value, c = +inPct.value, n = +inLoads.value, tr = +inTrucks.value, per = +inPer.value, us = CALC.fee;
    sliders.forEach(fill);
    setHTML('o-rate', money(r)); setHTML('o-pct', c + '%'); setHTML('o-loads', String(n)); setHTML('o-trucks', String(tr)); setHTML('o-per', String(per));
    if (mode === 'fleet') {
      var loads = tr * per, rev = r * loads, cost = us * loads;
      var share = (us / r * 100).toLocaleString(lang === 'ru' ? 'ru-RU' : 'en-US', {maximumFractionDigits: 1}) + '%';
      setHTML('l-them', t('calc.rev', lang)); setHTML('b-them', money(rev)); setHTML('b-us', money(cost)); width(cost, rev);
      setHTML('r-keep', tpl('calc.fleet_cost', {cost: money(cost), share: share}));
      setHTML('r-month', t('calc.fleet_zero', lang));
      setHTML('c-fine', t('calc.fine_fleet', lang));
    } else {
      var them = r * c / 100, diff = Math.max(0, them - us);
      setHTML('l-them', t('calc.them', lang)); setHTML('b-them', money(them)); setHTML('b-us', money(us)); width(us, them);
      setHTML('r-keep', tpl('calc.keep', {diff: money(diff)}));
      setHTML('r-month', tpl('calc.month', {month: money(diff * n), year: money(diff * n * 12)}));
      setHTML('c-fine', t('calc.fine_own', lang));
    }
  }
  sliders.forEach(function(el){ if (el) el.addEventListener('input', calc); });
  document.querySelectorAll('.mode button').forEach(function(b){
    b.addEventListener('click', function(){
      mode = b.getAttribute('data-mode') === 'fleet' ? 'fleet' : 'own';
      if (machine) machine.setAttribute('data-mode', mode);
      document.querySelectorAll('.mode button').forEach(function(x){ x.setAttribute('aria-pressed', String(x === b)); });
      calc();
    });
  });
  calc();

  // ---- language: both dictionaries are embedded, so switching needs no reload.
  function apply(l){
    lang = l;
    root.lang = l;
    document.querySelectorAll('[data-i18n]').forEach(function(el){
      var v = t(el.getAttribute('data-i18n'), l); if (v != null) el.innerHTML = v;
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function(el){
      el.getAttribute('data-i18n-attr').split(',').forEach(function(pair){
        var p = pair.split(':'); var v = t(p[1], l); if (v != null) el.setAttribute(p[0], v);
      });
    });
    // "Read more" links point at the article in the chosen language (/learn/... or /ru/learn/...).
    document.querySelectorAll('[data-href-en]').forEach(function(el){
      var v = el.getAttribute('data-href-' + l); if (v) el.setAttribute('href', v);
    });
    document.title = t('meta.title', l);
    select(current); calc();
    document.querySelectorAll('.lang button').forEach(function(b){ b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === l)); });
    try { localStorage.setItem('octopus.lang', l); } catch (e) {}
    try {
      if (/^https?:$/.test(location.protocol)) {
        var want = l === 'ru' ? '/ru/' : '/';
        if (location.pathname !== want) history.replaceState(null, '', want + location.search + location.hash);
      }
    } catch (e) {}
  }
  document.querySelectorAll('.lang button').forEach(function(b){
    b.addEventListener('click', function(){ apply(b.getAttribute('data-lang')); });
  });
  // An explicit earlier choice wins; otherwise a Russian browser gets Russian.
  var saved = null;
  try { saved = localStorage.getItem('octopus.lang'); } catch (e) {}
  var wanted = (saved === 'ru' || saved === 'en') ? saved
             : ((navigator.language || '').toLowerCase().indexOf('ru') === 0 ? 'ru' : lang);
  if (wanted !== lang) apply(wanted);

  // ---- theme: the head script already set data-theme; the button flips and remembers it.
  function setTheme(th, remember){
    root.setAttribute('data-theme', th);
    if (themeMeta) themeMeta.setAttribute('content', COLORS[th]);
    if (remember) { try { localStorage.setItem('octopus.theme', th); } catch (e) {} }
  }
  setTheme(root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light', false);
  document.getElementById('theme').addEventListener('click', function(){
    setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
  });
  // With no saved choice, follow the system setting live.
  if (window.matchMedia) {
    var mq = matchMedia('(prefers-color-scheme: dark)');
    var follow = function(e){
      var s = null; try { s = localStorage.getItem('octopus.theme'); } catch (x) {}
      if (s !== 'dark' && s !== 'light') setTheme(e.matches ? 'dark' : 'light', false);
    };
    if (mq.addEventListener) mq.addEventListener('change', follow); else if (mq.addListener) mq.addListener(follow);
  }

  // ---- reduced motion: freeze each looping SVG on its most telling frame.
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('svg[data-still]').forEach(function(svg){
      try { svg.pauseAnimations(); svg.setCurrentTime(parseFloat(svg.getAttribute('data-still'))); } catch (e) {}
    });
  }

  // ---- click counting (PostHog when configured; a no-op otherwise). Named events, no autocapture.
  // Clicks that leave the page go out by sendBeacon so navigation can't cut them off.
  function track(ev, props, leaving){
    try {
      if (window.posthog && typeof posthog.capture === 'function')
        posthog.capture(ev, Object.assign({lang: lang}, props || {}), leaving ? {transport: 'sendBeacon'} : undefined);
    } catch (e) {}
  }
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest ? e.target.closest('a,button') : null;
    if (!a) return;
    var sec = a.closest('section,header,footer,.ask');
    var p = {where: sec ? (sec.id || sec.className.split(' ').pop()) : 'page'};
    var href = a.getAttribute('href') || '', ev = null;
    if (href.indexOf(__REG__) === 0) ev = 'open_account';
    else if (href.indexOf('calendly.com') >= 0) ev = 'book_brandon';
    else if (href.indexOf('mailto:') === 0) { ev = 'email'; p.to = href.slice(7); }
    else if (a.getAttribute('data-lang')) { ev = 'lang_switch'; p.to = a.getAttribute('data-lang'); }
    else if (a.id === 'theme') ev = 'theme_toggle';
    else if (a.classList.contains('stop-btn')) { ev = 'lifecycle_stop'; p.stage = a.closest('.stop').getAttribute('data-stage'); }
    else if (a.classList.contains('hear')) ev = 'hear_chaching';
    else if (href.charAt(0) === '#') { ev = 'nav'; p.to = href.slice(1); }
    else if (href.indexOf('/learn/') >= 0) { ev = 'read_more'; p.to = href; }
    else if (href.charAt(0) === '/') { ev = 'legal'; p.to = href; }
    if (ev) track(ev, p, /^(https?:|mailto:|\/)/.test(href));
  }, true);
  sliders.forEach(function(el){
    if (el) el.addEventListener('change', function(){ track('calc_used', {field: el.id, value: +el.value, mode: mode}); });
  });
  document.querySelectorAll('.mode button').forEach(function(b){
    b.addEventListener('click', function(){ track('calc_mode', {mode: b.getAttribute('data-mode')}); });
  });

  // ---- ask brandon: an AI that answers in Brandon's words (rendered only when ASK_BRANDON_LIVE).
  var ASK = __ASK__;
  var askBox = document.getElementById('ask');
  if (ASK.live && askBox) {
    var fab = document.getElementById('ask-fab'), log = document.getElementById('ask-log');
    var form = document.getElementById('ask-form'), input = document.getElementById('ask-input'), sendB = document.getElementById('ask-send');
    var hist = [], busy = false, greeted = false;
    var bubble = function(text, cls){
      var d = document.createElement('div'); d.className = 'msg ' + cls; d.textContent = text;
      log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
    };
    var chips = function(){
      var c = document.createElement('div'); c.className = 'ask-chips';
      (t('ask.chips', lang) || []).forEach(function(q){
        var b = document.createElement('button'); b.type = 'button'; b.textContent = q;
        b.addEventListener('click', function(){ c.remove(); ask(q); }); c.appendChild(b);
      });
      log.appendChild(c);
    };
    var offline = function(key){
      var d = bubble(t(key, lang), 'bot err');
      if (key === 'ask.offline') {
        var a = document.createElement('a'); a.href = ASK.demo; a.textContent = ' ' + t('ask.real', lang) + ' →';
        d.appendChild(a);
      }
    };
    var openChat = function(){
      askBox.hidden = false; fab.hidden = true;
      if (!greeted) { greeted = true; bubble(t('ask.hello', lang), 'bot'); chips(); }
      input.focus(); track('ask_open');
    };
    var closeChat = function(){ askBox.hidden = true; fab.hidden = false; fab.focus(); };
    var ask = function(q){
      q = String(q || '').trim().slice(0, 1000);
      if (!q || busy) return;
      busy = true; sendB.disabled = true;
      bubble(q, 'me');
      hist.push({role: 'user', content: q});
      while (hist.length > 12 || (hist.length && hist[0].role !== 'user')) hist.shift();
      var typing = bubble(t('ask.thinking', lang), 'bot typing');
      track('ask_question', {turn: hist.length});
      var ctl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function(){ if (ctl) ctl.abort(); }, 25000);
      fetch(ASK.url, {method: 'POST', headers: {'Content-Type': 'application/json'},
                      body: JSON.stringify({messages: hist, lang: lang}), signal: ctl ? ctl.signal : undefined})
        .then(function(r){ return r.json().catch(function(){ return {}; }).then(function(j){ return {ok: r.ok, status: r.status, j: j}; }); })
        .then(function(res){
          typing.remove();
          if (res.ok && res.j && typeof res.j.reply === 'string' && res.j.reply) {
            bubble(res.j.reply, 'bot');
            hist.push({role: 'assistant', content: res.j.reply.slice(0, 1000)});
          } else {
            hist.pop(); offline(res.status === 429 ? 'ask.rate' : 'ask.offline'); track('ask_error', {status: res.status});
          }
        })
        .catch(function(){ typing.remove(); hist.pop(); offline('ask.offline'); track('ask_error', {status: 0}); })
        .then(function(){ clearTimeout(timer); busy = false; sendB.disabled = false; input.focus(); });
    };
    fab.addEventListener('click', openChat);
    document.getElementById('ask-x').addEventListener('click', closeChat);
    askBox.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeChat(); });
    form.addEventListener('submit', function(e){ e.preventDefault(); var q = input.value; input.value = ''; ask(q); });
    input.addEventListener('keydown', function(e){
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); }
    });
  }

  // ---- old deep links from the six-card page (#free, #one, ...) land on the matching section.
  var OLD = {free:'pricing', one:'lifecycle', boards:'lifecycle', track:'lifecycle', paper:'lifecycle', why:'founder'};
  var h = (location.hash || '').slice(1);
  if (OLD[h]) {
    var el = document.getElementById(OLD[h]);
    if (el) setTimeout(function(){ el.scrollIntoView(); }, 0);
  }
})();
"""


def jsonld(lang: str, strings: dict, canonical: str) -> str:
    graph = [
        {
            "@type": "SoftwareApplication",
            "@id": f"{SITE}/#app",
            "name": "Octopus TMS",
            "alternateName": "LLMP — Load Lifecycle Management and Payments",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": canonical,
            "inLanguage": ["en", "ru"],
            "description": strings["meta"]["description"],
            "offers": [
                {"@type": "Offer", "price": "20.00", "priceCurrency": "USD", "name": "Per load",
                 "description": "$20 per load. No subscription. No seats. No load, no fee."},
            ],
            "publisher": {"@id": f"{SITE}/#org"},
        },
        {
            "@type": "Organization",
            "@id": f"{SITE}/#org",
            "name": "Digital Ronin LLC",
            "alternateName": "Octopus TMS",
            "url": SITE,
            "logo": f"{SITE}/octopus-logo.svg",
            "email": CONTACT_EMAIL,
            "founder": {"@type": "Person", "name": "Brandon Hay", "jobTitle": "Founder"},
            "contactPoint": [
                {"@type": "ContactPoint", "contactType": "customer support", "email": CONTACT_EMAIL, "availableLanguage": ["English", "Russian"]},
                {"@type": "ContactPoint", "contactType": "partnerships", "email": PARTNERS_EMAIL},
                {"@type": "ContactPoint", "contactType": "privacy", "email": PRIVACY_EMAIL},
            ],
        },
    ]
    return json_for_script({"@context": "https://schema.org", "@graph": graph})


def i18n(key: str, value: str, tag: str = "span", cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-i18n="{key}">{value}</{tag}>'


def article_url(slug: str, lang: str) -> str:
    return f"/ru/learn/{slug}/" if lang == "ru" else f"/learn/{slug}/"


def more_link(s: dict, slug: str, lang: str) -> str:
    """A "Read more" link into the /learn/ article; the href follows the language toggle through data-href-*."""
    return (f'<a class="more" href="{article_url(slug, lang)}" data-href-en="{article_url(slug, "en")}" '
            f'data-href-ru="{article_url(slug, "ru")}" data-i18n="ui.more">{s["ui"]["more"]}</a>')


def spine_svg(s: dict) -> str:
    """The horizontal lifecycle: eight stops, a load sliding Found → Paid, Paid flashing with cha-ching."""
    xs = [80 + 160 * i for i in range(8)]
    rings = "".join(f'<circle cx="{x}" cy="72" r="13"/>' for x in xs[:6])
    nums = "".join(f'<text x="{x}" y="76">{i + 1}</text>' for i, x in enumerate(xs[:6]))
    return f"""<svg class="spine" viewBox="0 0 1280 132" aria-hidden="true" focusable="false" data-still="4.4">
      <defs><linearGradient id="sp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3D7BFF"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs>
      <path d="M80,72 H1200" style="stroke:rgba(255,255,255,.16);stroke-width:4;stroke-linecap:round"/>
      <path d="M80,72 H1040" stroke-dasharray="960" stroke-dashoffset="960" style="fill:none;stroke:url(#sp);stroke-width:4;stroke-linecap:round"><animate attributeName="stroke-dashoffset" values="960;0;0;960" keyTimes="0;.7;.96;1" dur="6s" repeatCount="indefinite"/></path>
      <g style="fill:#0E1726;stroke:rgba(255,255,255,.4);stroke-width:2.5">{rings}</g>
      <g style="fill:#8DB2FF;font-size:11px;font-weight:700" text-anchor="middle">{nums}</g>
      <circle cx="1200" cy="72" r="13" style="fill:#0E1726;stroke:rgba(255,255,255,.25);stroke-width:2.5" stroke-dasharray="4 4"/><text x="1200" y="76" text-anchor="middle" style="fill:#8693A7;font-size:11px;font-weight:700">8</text>
      <circle cx="1040" cy="72" r="24" style="fill:none;stroke:#34D399;stroke-width:3" opacity="0"><animate attributeName="r" values="24;24;60" keyTimes="0;.7;1" dur="6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;.9;0" keyTimes="0;.69;.7;1" dur="6s" repeatCount="indefinite"/></circle>
      <circle cx="1040" cy="72" r="26" style="fill:rgba(52,211,153,.18)"/>
      <circle cx="1040" cy="72" r="20" style="fill:#34D399"/>
      <text x="1040" y="80" text-anchor="middle" style="fill:#052e16;font-family:var(--display);font-size:20px;font-weight:800">$</text>
      <text x="1040" y="26" text-anchor="middle" style="fill:#34D399;font-size:17px;font-weight:700;font-style:italic" opacity="0" data-i18n="life.chaching">{s["life"]["chaching"]}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.7;.74;.93;1" dur="6s" repeatCount="indefinite"/></text>
      <g><rect x="-11" y="-8" width="22" height="16" rx="4" style="fill:#fff"/><rect x="-7" y="-4" width="9" height="2.5" rx="1" style="fill:#0A5BFF"/><rect x="-7" y="1" width="14" height="2.5" rx="1" style="fill:#0A5BFF"/><animateMotion path="M80,72 H1040" keyPoints="0;1;1" keyTimes="0;.7;1" calcMode="linear" dur="6s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.7;.72;1" dur="6s" repeatCount="indefinite"/></g>
    </svg>"""


def hero_svg(s: dict) -> str:
    """The hero picture: an octopus inside the app pulls a load in from the boards (left, outside),
    the load passes six lit stops inside, then the octopus pulls the money in from the broker (right, outside).
    One 9-second loop in SMIL; colours that animate are literal, the rest follow the theme tokens."""
    h = s["hero"]
    D = "9s"
    # Stops inside the box: six process stops, then the paid stop.
    xs = [160 + 60 * i for i in range(6)]
    PAID_X = 540
    # Timeline (fractions of the loop). See the comments next to each element.
    t_pull0, t_pull1, t_walk1 = .10, .20, .56     # card pulled in, then walks the stops
    f_left, f_right = .3434, .4079               # straight part of each tentacle, as a fraction of its length
    stops = ""
    for i, x in enumerate(xs):
        ti = t_pull1 + (t_walk1 - t_pull1) * i / 5
        stops += (f'<circle cx="{x}" cy="200" r="13" style="fill:var(--card2);stroke:var(--line);stroke-width:2"/>'
                  f'<circle cx="{x}" cy="200" r="13" fill="#3D7BFF" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{ti:.3f};{ti + .02:.3f};.92;1" dur="{D}" repeatCount="indefinite"/></circle>'
                  f'<text class="num" x="{x}" y="204" text-anchor="middle">{i + 1}</text>')
    return f"""<svg class="hero-anim" viewBox="0 0 720 280" role="img" data-i18n-attr="aria-label:hero.anim_aria" aria-label="{attr(h["anim_aria"])}" data-still="3.6">
      <defs><linearGradient id="og" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1D4ED8"/><stop offset="1" stop-color="#7C3AED"/></linearGradient></defs>
      <rect x="120" y="28" width="480" height="224" rx="24" style="fill:var(--card);stroke:var(--line);stroke-width:1.5"/>
      <text class="lbl" x="360" y="246" text-anchor="middle" data-i18n="hero.anim_inside">{h["anim_inside"]}</text>
      <text class="lbl sm" x="60" y="158" text-anchor="middle" data-i18n="hero.anim_in">{h["anim_in"]}</text>
      <text class="lbl2 sm" x="60" y="176" text-anchor="middle" data-i18n="hero.anim_boards">{h["anim_boards"]}</text>
      <text class="lbl sm" x="660" y="158" text-anchor="middle" data-i18n="hero.anim_money">{h["anim_money"]}</text>
      <text class="lbl2 sm" x="660" y="176" text-anchor="middle" data-i18n="hero.anim_broker">{h["anim_broker"]}</text>
      <!-- the octopus: head, eyes, four swaying tentacles -->
      <g style="fill:none;stroke:url(#og);stroke-width:7;stroke-linecap:round">
        <path d="M338,116 C320,150 300,150 296,176"><animateTransform attributeName="transform" type="rotate" values="0 360 116;3 360 116;0 360 116;-3 360 116;0 360 116" dur="3.4s" repeatCount="indefinite"/></path>
        <path d="M352,120 C348,150 340,160 336,180"><animateTransform attributeName="transform" type="rotate" values="0 360 116;-2 360 116;0 360 116;2 360 116;0 360 116" dur="3.9s" repeatCount="indefinite"/></path>
        <path d="M368,120 C372,150 380,160 384,180"><animateTransform attributeName="transform" type="rotate" values="0 360 116;2 360 116;0 360 116;-2 360 116;0 360 116" dur="4.3s" repeatCount="indefinite"/></path>
        <path d="M382,116 C400,150 420,150 424,176"><animateTransform attributeName="transform" type="rotate" values="0 360 116;-3 360 116;0 360 116;3 360 116;0 360 116" dur="3.7s" repeatCount="indefinite"/></path>
      </g>
      <!-- left arm: reaches out of the box to the load, then pulls it in to stop 1 -->
      <path d="M336,118 C300,150 240,200 160,200 H56" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" style="fill:none;stroke:url(#og);stroke-width:7;stroke-linecap:round"><animate attributeName="stroke-dashoffset" values="1;1;0;0;{f_left};1;1" keyTimes="0;.01;{t_pull0};{t_pull0 + .005};{t_pull1};.30;1" dur="{D}" repeatCount="indefinite"/></path>
      <!-- right arm: reaches out to the money and pulls it in to the paid stop -->
      <path d="M384,118 C420,150 480,200 540,200 H664" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" style="fill:none;stroke:url(#og);stroke-width:7;stroke-linecap:round"><animate attributeName="stroke-dashoffset" values="1;1;0;0;{f_right};1;1" keyTimes="0;.58;.66;.665;.74;.82;1" dur="{D}" repeatCount="indefinite"/></path>
      <ellipse cx="360" cy="92" rx="34" ry="30" fill="url(#og)"/>
      <circle cx="348" cy="96" r="6.5" fill="#fff"/><circle cx="372" cy="96" r="6.5" fill="#fff"/>
      <circle cx="349.5" cy="97" r="3.2" fill="#0E1726"/><circle cx="373.5" cy="97" r="3.2" fill="#0E1726"/>
      <!-- the stops -->
      {stops}
      <circle cx="{PAID_X}" cy="200" r="16" style="fill:var(--card2);stroke:var(--line);stroke-width:2" stroke-dasharray="4 4"/>
      <circle cx="{PAID_X}" cy="200" r="16" fill="#34D399" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.74;.76;.95;.99;1" dur="{D}" repeatCount="indefinite"/></circle>
      <text x="{PAID_X}" y="207" text-anchor="middle" style="fill:#052e16;font-family:var(--display);font-size:17px;font-weight:800" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.74;.76;.95;.99;1" dur="{D}" repeatCount="indefinite"/>$</text>
      <circle cx="{PAID_X}" cy="200" r="16" style="fill:none;stroke:#34D399;stroke-width:3" opacity="0"><animate attributeName="r" values="16;16;64" keyTimes="0;.74;.9" dur="{D}" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="0;.735;.74;.9;1" dur="{D}" repeatCount="indefinite"/></circle>
      <text x="{PAID_X}" y="160" text-anchor="middle" style="fill:#34D399;font-size:16px;font-weight:700;font-style:italic" opacity="0" data-i18n="life.chaching">{s["life"]["chaching"]}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.74;.77;.93;.97;1" dur="{D}" repeatCount="indefinite"/></text>
      <!-- the load: a rate-con card, pulled in from the left, walking the stops, gone once proven -->
      <g><rect x="-12" y="-9" width="24" height="18" rx="4" style="fill:#fff;stroke:#D7DEE8;stroke-width:1"/><rect x="-7" y="-4" width="9" height="2.5" rx="1" style="fill:#0A5BFF"/><rect x="-7" y="1" width="14" height="2.5" rx="1" style="fill:#0A5BFF"/>
        <animateMotion path="M56,200 H460" keyPoints="0;0;.2574;1;1" keyTimes="0;{t_pull0};{t_pull1};{t_walk1};1" calcMode="linear" dur="{D}" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{t_walk1};{t_walk1 + .05};.99;1" dur="{D}" repeatCount="indefinite"/></g>
      <!-- the money: a coin from outside, pulled in to the paid stop -->
      <g opacity="0"><circle r="13" fill="#34D399"/><text y="5" text-anchor="middle" style="fill:#052e16;font-family:var(--display);font-size:14px;font-weight:800">$</text>
        <animateMotion path="M664,200 H{PAID_X}" keyPoints="0;0;1;1" keyTimes="0;.66;.74;1" calcMode="linear" dur="{D}" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.63;.65;.76;.78;1" dur="{D}" repeatCount="indefinite"/></g>
    </svg>"""


def works_html(s: dict) -> str:
    w = s["works"]
    items = ""
    for name, key, lead in WORKS:
        cls = ' class="lead"' if lead else ""
        items += f'<li{cls}><b>{name}</b><span data-i18n="works.{key}">{w[key]}</span></li>'
    return f"""<section class="in works" aria-label="{attr(w["eyebrow"])}">
  <a class="eyebrow" href="#partners" data-i18n="works.eyebrow">{w["eyebrow"]}</a>
  <ul>{items}</ul>
</section>"""


def two_html(s: dict, lang: str) -> str:
    k = s["two"]
    return f"""<section class="in two" id="two-screens" aria-labelledby="two-h">
  <div class="two-text">
    {i18n("two.eyebrow", k["eyebrow"], "span", "eyebrow")}
    <h2 class="h2" id="two-h" data-i18n="two.h2">{k["h2"]}</h2>
    {i18n("two.p", k["p"], "p", "lead")}
    {more_link(s, "two-screens", lang)}
  </div>
  <div class="screens">
    <div class="screen owner">
      <span class="role" data-i18n="two.owner">{k["owner"]}</span>
      <span class="ld" data-i18n="two.load">{k["load"]}</span>
      <div class="row big"><span data-i18n="two.ratecon">{k["ratecon"]}</span><b>$3,000</b></div>
      <div class="row"><span data-i18n="two.pay">{k["pay"]}</span><b>$900</b></div>
      <div class="row"><span data-i18n="two.fee">{k["fee"]}</span><b>$20</b></div>
    </div>
    <div class="eq" aria-hidden="true">=</div>
    <div class="screen driver">
      <span class="role" data-i18n="two.driver">{k["driver"]}</span>
      <span class="ld" data-i18n="two.load">{k["load"]}</span>
      <div class="row big"><span data-i18n="two.ratecon">{k["ratecon"]}</span><b>$3,000</b></div>
      <div class="row"><span data-i18n="two.your_pay">{k["your_pay"]}</span><b>$900</b></div>
      <div class="row"><span class="pdf" data-i18n="two.pdf">{k["pdf"]}</span></div>
    </div>
  </div>
</section>"""


ICON_BELL = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5.5-6.84V3.5a1.5 1.5 0 0 0-3 0v.66A7 7 0 0 0 5 11v5l-2 2v1h18v-1z"/></svg>"""


def hear_btn(s: dict, extra: str = "") -> str:
    return f'<button type="button" class="hear{extra}">{ICON_BELL}<span data-i18n="life.hear">{s["life"]["hear"]}</span></button>'


def stops_html(s: dict) -> str:
    out = []
    for i, key in enumerate(STAGES):
        name, short, long = s["life"][key]
        dot = "$" if key == "paid" else str(i + 1)
        ching = f' <span class="ching" aria-hidden="true" data-i18n="life.chaching">{s["life"]["chaching"]}</span>' if key == "paid" else ""
        hear = hear_btn(s) if key == "paid" else ""
        on = " on" if key == "found" else ""
        out.append(
            f'<li class="stop {key}{on}" data-stage="{key}"><span class="dot" aria-hidden="true">{dot}</span>'
            f'<button type="button" class="stop-btn" aria-expanded="{"true" if on else "false"}" aria-controls="detail">'
            f'<span class="name"><span data-i18n="life.{key}.0">{name}</span>{ching}</span>'
            f'<span class="desc" data-i18n="life.{key}.1">{short}</span></button>'
            f'<div class="more"><span data-i18n="life.{key}.2">{long}</span>{hear}</div></li>'
        )
    return "\n      ".join(out)


def money(n: float) -> str:
    return f"${round(n):,}"


def calc_html(s: dict, lang: str) -> str:
    c, k = CALC, s["calc"]
    them = c["rate"] * c["pct"] / 100
    diff = max(0, them - c["fee"])
    keep = k["keep"].format(diff=money(diff))
    month = k["month"].format(month=money(diff * c["loads"]), year=money(diff * c["loads"] * 12))

    def field(fid, key, value, lo, hi, step, shown, only=""):
        pct = (value - lo) / (hi - lo) * 100
        cls = f" f-{only}" if only else ""
        return (f'<div class="field{cls}"><div class="field-top"><label for="c-{fid}" data-i18n="calc.{key}">{k[key]}</label>'
                f'<output id="o-{fid}" for="c-{fid}">{shown}</output></div>'
                f'<input type="range" id="c-{fid}" min="{lo}" max="{hi}" step="{step}" value="{value}" style="--fill:{pct:.1f}%"></div>')

    # Pre-rendered in "own authority" mode; the script re-renders the mode-dependent parts (no data-i18n on those).
    return f"""<section class="in calc" id="pricing" aria-labelledby="calc-h">
  <div class="calc-text">
    {i18n("calc.eyebrow", k["eyebrow"], "span", "eyebrow")}
    <h2 class="h2" id="calc-h" data-i18n="calc.h2">{k["h2"]}</h2>
    {i18n("calc.p", k["p"], "p", "lead")}
    <div class="tiles">
      <div class="tile"><strong data-i18n="calc.sub_t">{k["sub_t"]}</strong><span data-i18n="calc.sub_d">{k["sub_d"]}</span></div>
      <div class="tile us"><strong data-i18n="calc.oct_t">{k["oct_t"]}</strong><span data-i18n="calc.oct_d">{k["oct_d"]}</span></div>
    </div>
    {i18n("calc.leased", k["leased"], "p", "leased")}
    {more_link(s, "no-load-no-fee", lang)}
  </div>
  <div class="machine" id="machine" data-mode="own">
    <div class="mode" role="group" aria-label="Pricing view">
      <button type="button" data-mode="own" aria-pressed="true" data-i18n="calc.mode_own">{k["mode_own"]}</button>
      <button type="button" data-mode="fleet" aria-pressed="false" data-i18n="calc.mode_fleet">{k["mode_fleet"]}</button>
    </div>
    {field("rate", "rate", c["rate"], c["rate_min"], c["rate_max"], c["rate_step"], money(c["rate"]))}
    {field("pct", "pct", c["pct"], c["pct_min"], c["pct_max"], 1, f'{c["pct"]}%', "own")}
    {field("loads", "loads", c["loads"], c["loads_min"], c["loads_max"], 1, str(c["loads"]), "own")}
    {field("trucks", "trucks", c["trucks"], c["trucks_min"], c["trucks_max"], 1, str(c["trucks"]), "fleet")}
    {field("per", "per", c["per"], c["per_min"], c["per_max"], 1, str(c["per"]), "fleet")}
    <div class="bars" aria-live="polite">
      <div class="bar them"><span id="l-them">{k["them"]}</span><span class="track"><span class="fill" style="width:100%"></span></span><b id="b-them">{money(them)}</b></div>
      <div class="bar us"><span data-i18n="calc.us">{k["us"]}</span><span class="track"><span class="fill" id="f-us" style="width:{max(2, c["fee"] / them * 100):.1f}%"></span></span><b id="b-us">{money(c["fee"])}</b></div>
    </div>
    <p class="result" id="r-keep">{keep}</p>
    <p class="result-month" id="r-month">{month}</p>
    <p class="fine" id="c-fine">{k["fine_own"]}</p>
  </div>
</section>"""


def who_html(s: dict) -> str:
    w, ui = s["who"], s["ui"]
    cards = [
        ("oo", REGISTER_URL, "ui.start", ui["start"]),
        ("fl", DEMO_URL, "ui.demo_long", ui["demo_long"]),
        ("pa", f"mailto:{PARTNERS_EMAIL}", None, PARTNERS_EMAIL),
    ]
    items = ""
    for c, href, lk, lv in cards:
        link_i18n = f' data-i18n="{lk}"' if lk else ""
        items += (f'\n    <li class="card"><h3 data-i18n="who.{c}_t">{w[c + "_t"]}</h3><p data-i18n="who.{c}_d">{w[c + "_d"]}</p>'
                  f'<a href="{href}"{link_i18n}>{lv}</a></li>')
    return f"""<section class="in who" id="who" aria-labelledby="who-h">
  <h2 class="eyebrow" id="who-h" data-i18n="who.eyebrow">{w["eyebrow"]}</h2>
  <ul class="cards">{items}
  </ul>
</section>"""


PARTNERS = [
    # (key, card class, chip class, wordmark): statuses live in strings.py and must match reality
    ("lb", "live", "live", "123Loadboard"),
    ("dat", "", "prog", "DAT"),
    ("og", "", "next", "Outgo<small>by DAT</small>"),
]
UNDER_THE_HOOD = [
    ("st", "", "", "Stripe"),
    ("qb", "", "live", "QuickBooks"),
    ("cl", "", "", "Claude<small>by Anthropic</small>"),
    ("aws", "", "", "AWS"),
]


def partners_html(s: dict) -> str:
    pt = s["partners"]

    def cards(rows):
        return "".join(
            f'\n    <li class="pcard {cls}"><span class="mark">{mark}</span>'
            f'<span class="chip {chip}" data-i18n="partners.{k}_s">{pt[k + "_s"]}</span>'
            f'<p data-i18n="partners.{k}_d">{pt[k + "_d"]}</p></li>'
            for k, cls, chip, mark in rows
        )

    return f"""<section class="in partners" id="partners" aria-labelledby="partners-h">
  <div class="partners-head">
    {i18n("partners.eyebrow", pt["eyebrow"], "span", "eyebrow")}
    <h2 class="h2" id="partners-h" data-i18n="partners.h2">{pt["h2"]}</h2>
    {i18n("partners.lead", pt["lead"], "p", "lead")}
  </div>
  <ul class="pgrid big">{cards(PARTNERS)}
  </ul>
  <div class="hood-head">
    {i18n("partners.hood", pt["hood"], "span", "eyebrow")}
    {i18n("partners.hood_lead", pt["hood_lead"], "p", "lead")}
  </div>
  <ul class="pgrid small">{cards(UNDER_THE_HOOD)}
  </ul>
  <p class="pjoin"><span data-i18n="partners.join">{pt["join"]}</span> <a href="mailto:{PARTNERS_EMAIL}">{PARTNERS_EMAIL}</a></p>
  {i18n("partners.fine", pt["fine"], "p", "pfine")}
</section>"""


def ask_html(s: dict) -> str:
    """The floating "Ask Brandon" chat. Always discloses that it is an AI."""
    if not ASK_BRANDON_LIVE:
        return ""
    a = s["ask"]
    return f"""
<button type="button" class="ask-fab" id="ask-fab" aria-controls="ask"><span class="mono" aria-hidden="true">BH</span><span class="lbl" data-i18n="ask.open">{a["open"]}</span></button>
<section class="ask" id="ask" role="dialog" aria-labelledby="ask-title" hidden>
  <div class="ask-head">
    <span class="mono" aria-hidden="true">BH</span>
    <div><strong id="ask-title" data-i18n="ask.title">{a["title"]}</strong>
    <small><span data-i18n="ask.disclose">{a["disclose"]}</span> <a href="{DEMO_URL}" data-i18n="ask.real">{a["real"]}</a></small></div>
    <button type="button" class="ask-x" id="ask-x" data-i18n-attr="aria-label:ask.close" aria-label="{attr(a["close"])}">×</button>
  </div>
  <div class="ask-log" id="ask-log" aria-live="polite"></div>
  <form class="ask-form" id="ask-form">
    <textarea id="ask-input" rows="1" maxlength="1000" data-i18n-attr="placeholder:ask.placeholder,aria-label:ask.placeholder" placeholder="{attr(a["placeholder"])}" aria-label="{attr(a["placeholder"])}"></textarea>
    <button type="submit" id="ask-send" data-i18n="ask.send">{a["send"]}</button>
  </form>
  {i18n("ask.note", a["note"], "p", "ask-note")}
</section>"""


def posthog_snippet() -> str:
    """PostHog's loader, cookieless (memory persistence), named events only, no session recording."""
    if not POSTHOG_KEY:
        return ""
    cfg = json.dumps({"api_host": POSTHOG_HOST, "persistence": "memory", "autocapture": False,
                      "capture_pageview": True, "disable_session_recording": True,
                      "respect_dnt": True, "person_profiles": "identified_only"})
    return (
        "<script>!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){"
        "var o=e.split(\".\");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call("
        "arguments,0)))}}(p=t.createElement(\"script\")).type=\"text/javascript\",p.crossOrigin=\"anonymous\",p.async=!0,"
        "p.src=s.api_host.replace(\".i.posthog.com\",\"-assets.i.posthog.com\")+\"/static/array.js\",(r=t.getElementsByTagName("
        "\"script\")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a=\"posthog\",u.people=u.people||[],"
        "u.toString=function(t){var e=\"posthog\";return\"posthog\"!==a&&(e+=\".\"+a),t||(e+=\" (stub)\"),e},"
        "u.people.toString=function(){return u.toString(1)+\".people (stub)\"},o=\"capture identify alias people.set "
        "people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing "
        "opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags "
        "group\".split(\" \"),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);"
        f"posthog.init({json.dumps(POSTHOG_KEY)},{cfg});</script>\n"
    )


def contact_html(s: dict) -> str:
    c = s["contact"]
    return f"""<section class="in contact" id="contact" aria-labelledby="contact-h">
  <div class="contact-text">
    {i18n("contact.eyebrow", c["eyebrow"], "span", "eyebrow")}
    <h2 class="h2" id="contact-h" data-i18n="contact.h2">{c["h2"]}</h2>
  </div>
  <ul class="lines">
    <li class="call"><a href="{DEMO_URL}"><strong data-i18n="contact.call_t">{c["call_t"]}</strong><span data-i18n="contact.call_d">{c["call_d"]}</span></a></li>
    <li><a href="mailto:{PARTNERS_EMAIL}"><strong data-i18n="contact.partners_t">{c["partners_t"]}</strong><span>{PARTNERS_EMAIL}</span></a></li>
    <li><a href="mailto:{CONTACT_EMAIL}"><strong data-i18n="contact.ask_t">{c["ask_t"]}</strong><span>{CONTACT_EMAIL}</span></a></li>
    <li><a href="mailto:{PRIVACY_EMAIL}"><strong data-i18n="contact.privacy_t">{c["privacy_t"]}</strong><span>{PRIVACY_EMAIL}</span></a></li>
  </ul>
</section>"""


SONAR_SVG = """<svg viewBox="0 0 1440 380" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" data-still="1.2">
      <circle cx="720" cy="190" r="40" style="fill:none;stroke:var(--accent);stroke-width:2"><animate attributeName="r" values="40;420" dur="4.5s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="4.5s" repeatCount="indefinite"/></circle>
      <circle cx="720" cy="190" r="40" style="fill:none;stroke:var(--accent);stroke-width:2"><animate attributeName="r" values="40;420" dur="4.5s" begin="-1.5s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="4.5s" begin="-1.5s" repeatCount="indefinite"/></circle>
      <circle cx="720" cy="190" r="40" style="fill:none;stroke:var(--accent);stroke-width:2"><animate attributeName="r" values="40;420" dur="4.5s" begin="-3s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="4.5s" begin="-3s" repeatCount="indefinite"/></circle>
      <circle cx="1010" cy="120" r="5" style="fill:var(--money)"><animate attributeName="opacity" values="0;0;1;0" keyTimes="0;.62;.66;1" dur="4.5s" repeatCount="indefinite"/></circle>
      <circle cx="430" cy="270" r="5" style="fill:var(--money)"><animate attributeName="opacity" values="0;0;1;0" keyTimes="0;.6;.64;1" dur="4.5s" begin="-1.5s" repeatCount="indefinite"/></circle>
    </svg>"""

RULE_ICONS = [
    # an approved phone
    """<svg width="72" height="72" viewBox="0 0 72 72" aria-hidden="true" focusable="false"><rect x="20" y="6" width="32" height="60" rx="7" style="fill:var(--card2);stroke:var(--ink);stroke-width:2.5"/><rect x="31" y="11" width="10" height="2.5" rx="1.2" style="fill:var(--ink)"/><circle cx="36" cy="37" r="11" style="fill:var(--money-soft)"/><path d="M30.5,37 L34.5,41 L42,33" style="fill:none;stroke:var(--money);stroke-width:3;stroke-linecap:round;stroke-linejoin:round"/></svg>""",
    # a face scan
    """<svg width="72" height="72" viewBox="0 0 72 72" aria-hidden="true" focusable="false" data-still="0.6"><g style="fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linecap:round"><path d="M8,22 V14 a6,6 0 0 1 6,-6 H22"/><path d="M50,8 H58 a6,6 0 0 1 6,6 V22"/><path d="M64,50 V58 a6,6 0 0 1 -6,6 H50"/><path d="M22,64 H14 a6,6 0 0 1 -6,-6 V50"/><path d="M27,28 V31 M45,28 V31 M36,30 V40 H33 M28,47 C32,51 40,51 44,47"/></g><rect x="8" y="10" width="56" height="2.5" rx="1.2" style="fill:var(--accent)"><animate attributeName="y" values="10;60;10" dur="2.4s" repeatCount="indefinite"/></rect></svg>""",
    # a key that breaks apart
    """<svg width="72" height="72" viewBox="0 0 72 72" aria-hidden="true" focusable="false" data-still="2.0"><circle cx="22" cy="36" r="11" style="fill:none;stroke:var(--ink);stroke-width:2.5"/><g><path d="M33,36 H62 M52,36 V45 M60,36 V43" style="fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linecap:round"/><animateTransform attributeName="transform" type="translate" values="0 0;0 0;8 -6;8 -6;0 0" keyTimes="0;.45;.55;.9;1" dur="3s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.6;.9;1" dur="3s" repeatCount="indefinite"/></g><path d="M36,26 L44,46" style="stroke:#EF4444;stroke-width:2.5;stroke-linecap:round" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.42;.46;.9;1" dur="3s" repeatCount="indefinite"/></path></svg>""",
]


def plate_svg(s: dict) -> str:
    """One plate number drawing lines out to everything connected to it."""
    boxes = [
        (10, "std.load", s["std"]["load"], "#4821", "var(--line)", ".3;.34"),
        (150, "std.truck", s["std"]["truck"], "#104", "var(--line)", ".35;.39"),
        (290, "std.driver", s["std"]["driver"], "B. Hay ✓", "var(--money)", ".4;.44"),
        (430, "std.docs", s["std"]["docs"], "BOL · POD", "var(--line)", ".45;.49"),
    ]
    groups = "".join(
        f'<g opacity=".35"><animate attributeName="opacity" values=".35;.35;1;1;.35" keyTimes="0;{kt};.92;1" dur="5s" repeatCount="indefinite"/>'
        f'<rect x="{x}" y="214" width="120" height="74" rx="14" style="fill:var(--card);stroke:{stroke};stroke-width:1.5"/>'
        f'<text x="{x + 14}" y="242" style="fill:var(--muted);font-size:12px;font-weight:600" data-i18n="{key}">{label}</text>'
        f'<text x="{x + 14}" y="266" style="fill:var(--ink);font-size:14px;font-weight:700">{val}</text></g>'
        for x, key, label, val, stroke, kt in boxes
    )
    return f"""<svg class="plate" viewBox="0 0 560 330" role="img" data-i18n-attr="aria-label:std.aria" aria-label="{attr(s["std"]["aria"])}" data-still="3">
      <rect x="150" y="14" width="260" height="56" rx="28" style="fill:var(--card2);stroke:var(--ink);stroke-width:2"/>
      <circle cx="184" cy="42" r="9" style="fill:none;stroke:var(--muted);stroke-width:2.2"/><path d="M190.5,48.5 L196,54" style="stroke:var(--muted);stroke-width:2.2;stroke-linecap:round"/>
      <text x="292" y="50" text-anchor="middle" style="fill:var(--ink);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:22px;font-weight:700;letter-spacing:.08em">TX 4821 KJ</text>
      <rect x="374" y="30" width="2.5" height="24" style="fill:var(--accent)"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
      <g style="fill:none;stroke:var(--accent);stroke-width:2" stroke-dasharray="1" stroke-dashoffset="1">
        <path d="M280,70 C280,140 70,140 70,214" pathLength="1"><animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="0;.1;.3;.92;1" dur="5s" repeatCount="indefinite"/></path>
        <path d="M280,70 C280,140 210,150 210,214" pathLength="1"><animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="0;.15;.35;.92;1" dur="5s" repeatCount="indefinite"/></path>
        <path d="M280,70 C280,150 350,150 350,214" pathLength="1"><animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="0;.2;.4;.92;1" dur="5s" repeatCount="indefinite"/></path>
        <path d="M280,70 C280,140 490,140 490,214" pathLength="1"><animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="0;.25;.45;.92;1" dur="5s" repeatCount="indefinite"/></path>
      </g>
      {groups}
    </svg>"""


def landing(lang: str, prefix: str) -> str:
    strings = {"en": resolve(EN, prefix), "ru": resolve(RU, prefix)}
    s = strings[lang]
    canonical = f"{SITE}/ru/" if lang == "ru" else f"{SITE}/"
    ui = s["ui"]
    # The top-bar button carries both labels; CSS shows the short one on phones.
    start = (f'<a class="btn" href="{REGISTER_URL}"><span class="lg" data-i18n="ui.start">{ui["start"]}</span>'
             f'<span class="sm" data-i18n="ui.start_short">{ui["start_short"]}</span></a>')
    demo = f'<a class="link" href="{DEMO_URL}" data-i18n="ui.demo_long">{ui["demo_long"]}</a>'
    rules = "".join(
        f'\n      <li class="rule">{icon}<div class="rule-text"><p data-i18n="sasr.r{i + 1}">{s["sasr"][f"r{i + 1}"]}</p>'
        f'<p class="how" data-i18n="sasr.e{i + 1}">{s["sasr"][f"e{i + 1}"]}</p></div></li>'
        for i, icon in enumerate(RULE_ICONS)
    )
    ask_cfg = {"live": ASK_BRANDON_LIVE, "url": ASK_BRANDON_URL, "demo": DEMO_URL}
    js = (JS.replace("__THEME_COLORS__", json.dumps(THEME_COLOR)).replace("__CALC__", json.dumps(CALC))
          .replace("__REG__", json.dumps(REGISTER_URL)).replace("__ASK__", json.dumps(ask_cfg)))
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<script>{THEME_INIT}</script>
<title>{attr(s["meta"]["title"])}</title>
<meta name="description" content="{attr(s["meta"]["description"])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{SITE}/">
<link rel="alternate" hreflang="ru" href="{SITE}/ru/">
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Octopus TMS">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{attr(s["meta"]["og_title"])}">
<meta property="og:description" content="{attr(s["meta"]["og_description"])}">
<meta property="og:image" content="{SITE}/images/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'ru_RU' if lang == 'ru' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{THEME_COLOR['light']}">
<link rel="icon" href="/octopus-logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600;700;800&family=Golos+Text:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{jsonld(lang, s, canonical)}</script>
{posthog_snippet()}<style>{THEME_CSS}{CSS}</style>
</head>
<body>
<header class="in top" id="top">
  <a class="brand" href="#top">{LOGO_SVG}<span data-i18n="ui.brand">{ui["brand"]}</span></a>
  <nav class="nav" aria-label="Sections">
    <a href="#lifecycle" data-i18n="ui.nav_how">{ui["nav_how"]}</a>
    <a href="#pricing" data-i18n="ui.nav_pricing">{ui["nav_pricing"]}</a>
    <a href="#founder" data-i18n="ui.nav_founder">{ui["nav_founder"]}</a>
    <a href="#partners" data-i18n="ui.nav_partners">{ui["nav_partners"]}</a>
  </nav>
  <div class="top-right">
    <div class="lang" role="group" aria-label="Language / Язык">
      <button type="button" data-lang="en" lang="en" aria-pressed="{'true' if lang == 'en' else 'false'}" aria-label="English">{FLAG_US}<span>EN</span></button>
      <button type="button" data-lang="ru" lang="ru" aria-pressed="{'true' if lang == 'ru' else 'false'}" aria-label="Русский">{FLAG_RU}<span>RU</span></button>
    </div>
    <button type="button" class="theme" id="theme" data-i18n-attr="aria-label:ui.theme,title:ui.theme" aria-label="{attr(ui["theme"])}" title="{attr(ui["theme"])}">{ICON_MOON}{ICON_SUN}</button>
    <a class="link link-demo" href="{DEMO_URL}" data-i18n="ui.demo">{ui["demo"]}</a>
    {start}
  </div>
</header>

<main>
<section class="in hero">
  <div class="hero-l">
    {i18n("hero.tag", s["hero"]["tag"], "p", "tag")}
    <h1 data-i18n="hero.h1">{s["hero"]["h1"]}</h1>
    <div class="anim-wrap">{hero_svg(s)}</div>
  </div>
  <div class="price">
    {i18n("hero.motto", s["hero"]["motto"], "p", "motto")}
    <blockquote class="quote"><p data-i18n="hero.quote">{s["hero"]["quote"]}</p><cite data-i18n="hero.quote_by">{s["hero"]["quote_by"]}</cite></blockquote>
    {i18n("hero.price", s["hero"]["price"], "p")}
    {i18n("hero.refund", s["hero"]["refund"], "p", "refund")}
    <div class="ctas"><a class="btn btn-lg" href="{REGISTER_URL}" data-i18n="ui.start">{ui["start"]}</a>{demo}</div>
  </div>
</section>

{works_html(s)}

<section class="band" id="lifecycle" aria-labelledby="life-h">
  <div class="in">
    <div class="band-head"><h2 class="eyebrow" id="life-h" data-i18n="life.eyebrow">{s["life"]["eyebrow"]}</h2>{i18n("life.hint", s["life"]["hint"], "span", "hint")}{i18n("life.chain", s["life"]["chain"], "span", "chain")}</div>
    {spine_svg(s)}
    <ol class="stops">
      {stops_html(s)}
    </ol>
    <div class="detail" id="detail" aria-live="polite">
      <h3 id="detail-name">{s["life"]["found"][0]}</h3>
      <p id="detail-text">{s["life"]["found"][2]}</p>
      {hear_btn(s)}
    </div>
    {more_link(s, "llmp", lang)}
  </div>
</section>

{calc_html(s, lang)}

{two_html(s, lang)}

{who_html(s)}

<section class="in why" id="founder" aria-labelledby="why-h">
  {i18n("why.eyebrow", s["why"]["eyebrow"], "span", "eyebrow")}
  <div class="why-body">
    <h2 class="h2" id="why-h" data-i18n="why.h2">{s["why"]["h2"]}</h2>
    {i18n("why.p0", s["why"]["p0"], "p", "p0")}
    {i18n("why.p1", s["why"]["p1"], "p", "p1")}
    {i18n("why.p2", s["why"]["p2"], "p", "p")}
    {i18n("why.p3", s["why"]["p3"], "p", "p")}
    {i18n("why.p4", s["why"]["p4"], "p", "p4")}
    <div class="sign"><span class="mono" aria-hidden="true">BH</span><strong data-i18n="why.sign">{s["why"]["sign"]}</strong><a href="{DEMO_URL}" data-i18n="why.talk">{s["why"]["talk"]}</a></div>
  </div>
</section>
<div class="sonar" id="why">
  {SONAR_SVG}
  {i18n("why.sonar", s["why"]["sonar"], "p")}
</div>

<section class="in sasr" id="security" aria-labelledby="sasr-h">
  <div class="sasr-head">{i18n("sasr.eyebrow", s["sasr"]["eyebrow"], "span", "eyebrow")}<h2 id="sasr-h">{s["sasr"]["title"]} {i18n("sasr.full", s["sasr"]["full"])}</h2>{i18n("sasr.note", s["sasr"]["note"], "span", "note")}</div>
  <ul class="rules">{rules}
  </ul>
  {i18n("sasr.close", s["sasr"]["close"], "p", "close")}
  {more_link(s, "sasr", lang)}
</section>

<section class="std" id="standard" aria-labelledby="std-h">
  <div class="in">
    <div class="std-text">
      {i18n("std.eyebrow", s["std"]["eyebrow"], "span", "eyebrow")}
      <h2 id="std-h" data-i18n="std.h2">{s["std"]["h2"]}</h2>
      {i18n("std.p", s["std"]["p"], "p")}
      {more_link(s, "llmp", lang)}
    </div>
    {plate_svg(s)}
  </div>
</section>

{partners_html(s)}

{contact_html(s)}

<section class="in end">
  {i18n("end.byline", s["end"]["byline"], "p")}
  <div class="ctas"><a class="btn btn-xl" href="{REGISTER_URL}" data-i18n="ui.start">{ui["start"]}</a>{demo}</div>
</section>
</main>
{ask_html(s)}
<footer class="foot">
  <div class="in">
    <span data-i18n="ui.footer_rights">{ui["footer_rights"]}</span>
    <nav aria-label="Legal">
      <a href="/privacy/" data-i18n="ui.privacy">{ui["privacy"]}</a>
      <a href="/terms/" data-i18n="ui.terms">{ui["terms"]}</a>
      <a href="/payment-terms/" data-i18n="ui.payment_terms">{ui["payment_terms"]}</a>
      <a href="/refund-policy/" data-i18n="ui.refund_policy">{ui["refund_policy"]}</a>
      <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
    </nav>
  </div>
</footer>

<script id="i18n" type="application/json">{json_for_script(strings)}</script>
<script>{js}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- legal pages (markdown -> html)

INLINE_RULES = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])"), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), r'<a href="\2">\1</a>'),
]


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    for rx, rep in INLINE_RULES:
        out = rx.sub(rep, out)
    return out


def md_to_html(md: str) -> tuple[str, str]:
    """Tiny converter for the legal docs' markdown subset. Returns (title, body_html)."""
    lines = md.splitlines()
    out: list[str] = []
    title = ""
    i = 0
    para: list[str] = []

    def flush_para():
        if para:
            lines_ = [x.strip() for x in para]
            # A block of short "**Label:** value" lines is a header block: keep the line breaks.
            if len(lines_) > 1 and all(x.startswith("**") for x in lines_):
                out.append("<p class=\"doc-meta\">" + "<br>".join(inline(x) for x in lines_) + "</p>")
            else:
                out.append(f"<p>{inline(' '.join(lines_))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para(); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1)); text = m.group(2).strip()
            if level == 1 and not title:
                title = text
            else:
                slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
                out.append(f'<h{level} id="{slug}">{inline(text)}</h{level}>')
            i += 1; continue
        if stripped in ("---", "***"):
            flush_para(); out.append("<hr>"); i += 1; continue
        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip()); i += 1
            text = " ".join(quote)
            if "Mirror of the shipped document" in text:
                continue  # repo-internal note, not part of the document
            out.append(f"<blockquote><p>{inline(text)}</p></blockquote>")
            continue
        if stripped.startswith("|"):
            flush_para()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            header, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c or "-") for c in r)]
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        para.append(line); i += 1
    flush_para()
    return title, "\n".join(out)


LEGAL_CSS = r"""
:root{--display:'Unbounded','Golos Text',system-ui,sans-serif;--body:'Golos Text',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif}
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:16px}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.6}
a{color:var(--accent-ink)}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px clamp(16px,3vw,32px);max-width:1180px;margin:0 auto}
.brand{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;font-size:1.05rem;white-space:nowrap}
.brand .logo{width:34px;height:34px;flex:none}
.back{font-weight:600;text-decoration:none;color:var(--ink2);font-size:.95rem}
.back:hover{color:var(--accent-ink)}
main{background:var(--card);border:1px solid var(--line);border-radius:24px;max-width:840px;margin:8px auto 32px;padding:clamp(22px,4vw,48px)}
h1{font-family:var(--display);font-weight:700;font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.15;letter-spacing:-.015em;margin:0 0 8px}
h2{font-size:1.25rem;margin:32px 0 10px;letter-spacing:-.01em}
h3{font-size:1.02rem;margin:22px 0 8px}
p,li{color:var(--ink2);max-width:72ch}
p{margin:0 0 12px}
.doc-meta{color:var(--muted);font-size:.92rem;line-height:1.7}
ul,ol{padding-left:22px;margin:0 0 14px}
li{margin:0 0 6px}
strong{color:var(--ink)}
blockquote{margin:16px 0;padding:14px 18px;border-left:3px solid var(--accent);background:var(--quote);border-radius:0 12px 12px 0}
blockquote p{margin:0;max-width:none}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em;background:var(--paper);padding:1px 5px;border-radius:5px}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
.table-wrap{overflow-x:auto;margin:0 0 16px}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink);font-weight:600}
.foot{max-width:1180px;margin:0 auto;padding:0 clamp(16px,3vw,32px) 28px;font-size:.8rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:space-between}
.foot a{color:var(--muted);text-decoration:none}
.foot a:hover{color:var(--ink)}
.foot nav{display:flex;flex-wrap:wrap;gap:6px 14px}
.top{flex-wrap:wrap;row-gap:8px}
.top-links{display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;justify-content:flex-end;margin-left:auto}
.back,.switch{white-space:nowrap}
.switch{font-weight:600;text-decoration:none;font-size:.95rem;border:1px solid var(--line);border-radius:999px;padding:5px 12px;color:var(--ink2);background:var(--card)}
.switch:hover{color:var(--accent-ink);border-color:var(--accent)}
/* /learn/ articles: a little more air and type than a legal document */
.article h1{font-size:clamp(1.7rem,3.6vw,2.5rem);margin-bottom:18px}
.article .eyebrow{display:block;font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--accent-ink);margin-bottom:12px}
.article p,.article li{font-size:1.06rem;line-height:1.65}
.article p.lead{font-size:1.2rem;line-height:1.55;color:var(--ink)}
.article h2{font-family:var(--display);font-weight:700;font-size:1.2rem;letter-spacing:-.01em;margin-top:38px}
.article ol li,.article ul li{margin-bottom:8px}
.ctas{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin-top:34px;padding-top:24px;border-top:1px solid var(--line)}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--accent);color:#fff;font-weight:700;font-size:15px;padding:11px 20px;border-radius:999px;text-decoration:none;white-space:nowrap}
.btn::after{content:"→"}
.btn:hover{filter:brightness(1.1)}
.link{font-weight:600;font-size:15px;color:var(--ink2);text-decoration:none}
.link:hover{color:var(--accent-ink)}
"""


def doc_page(*, lang: str, title: str, body: str, canonical: str, description: str, depth: int,
             back_href: str, back_label: str, nav: str, head_extra: str = "", top_extra: str = "",
             main_class: str = "", before_h1: str = "", after_body: str = "") -> str:
    """The shared document template: legal pages and /learn/ articles. `depth` is how many folders
    deep the page lives, so the brand link and the icon stay relative and work on file:// too."""
    root = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{attr(title)} — Octopus TMS</title>
<meta name="description" content="{attr(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{attr(title)} — Octopus TMS">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
{head_extra}<link rel="icon" href="{root}octopus-logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700&family=Golos+Text:wght@400;600;700&display=swap" rel="stylesheet">
<script>{THEME_INIT}</script>
<style>{THEME_CSS}{LEGAL_CSS}</style>
</head>
<body>
<header class="top">
  <a class="brand" href="{root}">{LOGO_SVG}<span>Octopus TMS</span></a>
  <nav class="top-links"><a class="back" href="{back_href}">{back_label}</a>{top_extra}</nav>
</header>
<main{f' class="{main_class}"' if main_class else ""}>
{before_h1}<h1>{inline(title)}</h1>
{body}{after_body}
</main>
<footer class="foot">
  <span>© {date.today().year} Digital Ronin LLC · <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></span>
  <nav>{nav}</nav>
</footer>
</body>
</html>
"""


def legal_page(out_dir: str, md_file: str, page_title: str) -> str:
    md = (SRC / "legal" / md_file).read_text(encoding="utf-8")
    title, body = md_to_html(md)
    title = title or page_title
    others = "".join(f'<a href="../{d}/">{t}</a>' for d, _, t in LEGAL_PAGES if d != out_dir)
    return doc_page(lang="en", title=title, body=body, canonical=f"{SITE}/{out_dir}/",
                    description=f"{title} for Octopus TMS, the carrier partner platform by Digital Ronin LLC.",
                    depth=1, back_href="../", back_label="← Back to octopustms.com", nav=others)


# --------------------------------------------------------------------------- /learn/ articles

# Slugs of the knowledge articles. Each has src/articles/<slug>.en.md and <slug>.ru.md and is rendered to
# /learn/<slug>/ and /ru/learn/<slug>/. The landing's "Read more" links point here (see more_link()).
ARTICLES = ["sasr", "llmp", "no-load-no-fee", "two-screens"]


def article_source(slug: str, lang: str) -> tuple[str, str]:
    """(title, body_html) of one article. The first paragraph becomes the lead and the meta description."""
    md = (SRC / "articles" / f"{slug}.{lang}.md").read_text(encoding="utf-8")
    title, body = md_to_html(md)
    body = body.replace("<p>", '<p class="lead">', 1)
    return title, body


def plain_text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def article_page(slug: str, lang: str) -> str:
    s = EN if lang == "en" else RU
    ln, ui = s["learn"], s["ui"]
    title, body = article_source(slug, lang)
    lead = re.search(r'<p class="lead">(.*?)</p>', body, re.S)
    description = plain_text(lead.group(1)) if lead else title
    canonical = SITE + article_url(slug, lang)
    other = "en" if lang == "ru" else "ru"
    head_extra = (
        f'<link rel="alternate" hreflang="en" href="{SITE}{article_url(slug, "en")}">\n'
        f'<link rel="alternate" hreflang="ru" href="{SITE}{article_url(slug, "ru")}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{SITE}{article_url(slug, "en")}">\n'
        f'<meta property="og:description" content="{attr(description)}">\n'
        f'<meta property="og:image" content="{SITE}/images/og.jpg">\n'
        f'<meta property="og:locale" content="{"ru_RU" if lang == "ru" else "en_US"}">\n'
        '<script type="application/ld+json">' + json_for_script({
            "@context": "https://schema.org", "@type": "Article", "headline": title, "inLanguage": lang,
            "description": description, "mainEntityOfPage": canonical,
            "author": {"@type": "Person", "name": "Brandon Hay"}, "publisher": {"@id": f"{SITE}/#org"},
        }) + "</script>\n"
    )
    switch = (f' <a class="switch" href="{article_url(slug, other)}" lang="{other}" hreflang="{other}">'
              f'{ln["other_lang"]}</a>')
    nav = f'<span>{ln["more"]}:</span>' + "".join(
        f'<a href="{article_url(o, lang)}">{article_source(o, lang)[0]}</a>' for o in ARTICLES if o != slug
    )
    ctas = (f'\n<div class="ctas"><a class="btn" href="{REGISTER_URL}">{ui["start"]}</a>'
            f'<a class="link" href="{DEMO_URL}">{ui["demo_long"]}</a></div>')
    return doc_page(lang=lang, title=title, body=body, canonical=canonical, description=description,
                    depth=3 if lang == "ru" else 2, back_href="/ru/" if lang == "ru" else "/", back_label=ln["back"],
                    nav=nav, head_extra=head_extra, top_extra=switch, main_class="article",
                    before_h1=f'<span class="eyebrow">{ln["eyebrow"]}</span>\n', after_body=ctas)


# --------------------------------------------------------------------------- sitemap / robots


def sitemap() -> str:
    # (loc, priority, English twin) — a page with a twin lists both languages as alternates.
    urls = [(f"{SITE}/", "1.0", f"{SITE}/"), (f"{SITE}/ru/", "0.9", f"{SITE}/")]
    for slug in ARTICLES:
        en = SITE + article_url(slug, "en")
        urls += [(en, "0.6", en), (SITE + article_url(slug, "ru"), "0.5", en)]
    urls += [(f"{SITE}/{d}/", "0.3", None) for d, _, _ in LEGAL_PAGES]
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, prio, en in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{loc}</loc>")
        if en:
            ru = en.replace(f"{SITE}/", f"{SITE}/ru/", 1)
            parts.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>')
            parts.append(f'    <xhtml:link rel="alternate" hreflang="ru" href="{ru}"/>')
            parts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>')
        parts.append(f"    <lastmod>{TODAY}</lastmod>")
        parts.append(f"    <priority>{prio}</priority>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------- main


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(content.encode('utf-8')) // 1024} KB)")


def main() -> None:
    write(ROOT / "index.html", landing("en", ""))
    write(ROOT / "ru" / "index.html", landing("ru", "../"))
    for out_dir, md_file, page_title in LEGAL_PAGES:
        write(ROOT / out_dir / "index.html", legal_page(out_dir, md_file, page_title))
    for slug in ARTICLES:
        write(ROOT / "learn" / slug / "index.html", article_page(slug, "en"))
        write(ROOT / "ru" / "learn" / slug / "index.html", article_page(slug, "ru"))
    write(ROOT / "sitemap.xml", sitemap())
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
