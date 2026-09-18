#!/usr/bin/env python3
"""Builds octopustms.com from src/.

    python3 src/build.py

Outputs (all committed, GitHub Pages serves the repo as-is):
  index.html            English landing page (pre-rendered, toggle to RU without reload)
  ru/index.html         Russian landing page (same template, RU pre-rendered)
  privacy/, terms/, payment-terms/, refund-policy/
                        legal pages rendered from src/legal/*.md, which mirror
                        docs/legal/*.md in the octopus app repo (the app is canonical)
  sitemap.xml, robots.txt

No dependencies beyond Python 3.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

from strings import CONTACT_EMAIL, DEMO_URL, EN, REGISTER_URL, RU, SITE

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CARD_ORDER = ["free", "one", "boards", "track", "paper", "founder"]
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


def resolve(strings: dict, prefix: str) -> dict:
    """Fill the {placeholders} inside card bodies for a page living at `prefix`."""
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
            return node.format(**ctx) if "{" in node else node
        return node

    return walk(strings)


def json_for_script(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def attr(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- landing page

CSS = r"""
:root{
  --ink:#0E1726;--ink-2:#3A4556;--muted:#69737F;--line:#D9DFE8;--paper:#EEF2F7;--card:#FFFFFF;
  --accent:#0A5BFF;--accent-ink:#0646C7;--accent-soft:#E7EEFF;--money:#0E9F6E;
  --radius:18px;
  --display:'Unbounded','Golos Text',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --body:'Golos Text',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
}
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font-family:var(--body);-webkit-text-size-adjust:100%;font-size:16px}
body{margin:0;min-height:100dvh;display:grid;grid-template-rows:auto auto 1fr auto;background:var(--paper);color:var(--ink);line-height:1.45}
a{color:var(--accent-ink)}
h1,h2,h3{margin:0;font-weight:700}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}

/* ---- top bar */
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:clamp(8px,1.4vh,14px) clamp(16px,3vw,32px)}
.brand{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;font-size:1.05rem;letter-spacing:-.01em;white-space:nowrap}
.brand .logo{width:34px;height:34px;flex:none}
.top-right{display:flex;align-items:center;gap:clamp(10px,1.6vw,22px)}
.lang{display:inline-flex;gap:2px;padding:3px;border:1px solid var(--line);border-radius:999px;background:#fff}
.lang button{border:0;background:transparent;font:inherit;font-weight:600;font-size:.82rem;letter-spacing:.02em;color:var(--muted);padding:6px 10px;border-radius:999px;display:inline-flex;align-items:center;gap:7px;cursor:pointer;transition:background .15s,color .15s}
.lang button:hover{color:var(--ink)}
.lang button[aria-pressed="true"]{background:var(--ink);color:#fff}
.flag{border-radius:2px;flex:none}
.link-demo{font-weight:600;text-decoration:none;color:var(--ink-2);font-size:.95rem;white-space:nowrap}
.link-demo:hover{color:var(--accent-ink)}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--accent);color:#fff;text-decoration:none;font-weight:700;font-size:.95rem;padding:10px 18px;border-radius:999px;white-space:nowrap;transition:transform .15s,background .15s}
.btn:hover{background:var(--accent-ink);transform:translateY(-1px)}
.btn::after{content:"→"}

/* ---- hero */
.hero{width:100%;max-width:1180px;margin:0 auto;padding:clamp(4px,1.6vh,18px) clamp(16px,3vw,32px) clamp(10px,2vh,20px)}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(1.4rem,calc(1vw + 2.2vh),2.6rem);line-height:1.1;letter-spacing:-.015em;text-wrap:balance;max-width:22ch;margin:0 0 clamp(6px,1.2vh,12px)}
.hero .sub{font-size:clamp(.94rem,1.9vh,1.2rem);color:var(--ink-2);max-width:66ch;margin:0 0 clamp(8px,1.6vh,16px);text-wrap:pretty}
.qa{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;border-left:3px solid var(--accent);padding-left:14px;max-width:78ch;font-size:clamp(.88rem,1.7vh,1.05rem)}
.qa .q{font-family:var(--display);font-weight:700;font-size:1.02em;white-space:nowrap;color:var(--ink)}
.qa .a{color:var(--ink-2);flex:1 1 40ch;text-wrap:pretty}

/* ---- card grid */
.grid{width:100%;max-width:1180px;margin:0 auto;padding:0 clamp(16px,3vw,32px) clamp(10px,1.6vh,16px);display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:minmax(0,1fr);gap:clamp(10px,1.4vw,16px);min-height:0}
.card{position:relative;display:flex;flex-direction:column;gap:clamp(4px,.9vh,10px);min-height:0;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:clamp(12px,2vh,22px) clamp(14px,1.6vw,22px);cursor:pointer;transition:transform .18s,border-color .18s,box-shadow .18s}
.card:hover,.card:has(button:focus-visible){transform:translateY(-2px);border-color:var(--accent);box-shadow:0 18px 34px -22px rgba(10,91,255,.55)}
.card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.more{margin-top:auto;padding-top:8px;display:none;align-items:center;justify-content:space-between;gap:10px;font-size:.8rem;font-weight:600;color:var(--accent-ink);letter-spacing:.01em}
.eyebrow{font-size:.7rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.plus{width:28px;height:28px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;color:var(--accent);font-weight:600;font-size:1.05rem;line-height:1;flex:none;transition:background .15s,color .15s,transform .18s}
.card:hover .plus,.card:has(button:focus-visible) .plus{background:var(--accent);color:#fff;border-color:var(--accent);transform:rotate(90deg)}
.card h2{font-family:var(--display);font-weight:700;font-size:clamp(.98rem,calc(.4vw + 1.35vh),1.6rem);line-height:1.2;letter-spacing:-.01em;text-wrap:balance}
.card h2 button{all:unset;cursor:pointer;color:inherit;font:inherit;display:block}
.card h2 button::before{content:"";position:absolute;inset:0;border-radius:var(--radius)}
.card h2 button:focus-visible{outline:none}
.card:has(button:focus-visible){outline:3px solid var(--accent);outline-offset:2px}
.teaser{margin:0;color:var(--ink-2);font-size:clamp(.84rem,calc(.1vw + 1.55vh),1.1rem);line-height:1.55;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;text-wrap:pretty}
.card-body{display:none}

/* ---- footer */
.foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 16px;padding:clamp(8px,1.2vh,12px) clamp(16px,3vw,32px);font-size:.8rem;color:var(--muted)}
.foot nav{display:flex;flex-wrap:wrap;gap:4px 14px}
.foot a{color:var(--muted);text-decoration:none}
.foot a:hover{color:var(--ink)}
.foot .foot-demo{display:none}

/* ---- expanded card */
.panel{border:0;border-radius:24px;padding:0;width:min(760px,94vw);max-height:min(88dvh,940px);background:#fff;color:var(--ink);box-shadow:0 40px 90px -30px rgba(14,23,38,.55);display:none;flex-direction:column;overflow:hidden;margin:auto}
.panel[open]{display:flex}
.panel::backdrop{background:rgba(14,23,38,.5);backdrop-filter:blur(6px)}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;padding:26px 28px 6px}
.panel-hook{font-family:var(--display);font-weight:700;font-size:clamp(1.15rem,2.2vw,1.55rem);line-height:1.15;letter-spacing:-.01em;margin-top:6px;text-wrap:balance}
.close{all:unset;cursor:pointer;width:38px;height:38px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;font-size:1.3rem;line-height:1;color:var(--ink-2);flex:none}
.close:hover{background:var(--paper);color:var(--ink)}
.panel-body{padding:6px 28px 18px;overflow:auto;overscroll-behavior:contain;font-size:.98rem;line-height:1.6;color:var(--ink-2)}
.panel-body h3{color:var(--ink);font-size:1rem;margin:18px 0 6px}
.panel-body p{margin:0 0 12px}
.panel-body em{font-style:normal;font-weight:600;color:var(--ink)}
.panel-body strong{color:var(--ink)}
.panel-body .fine{font-size:.86rem;color:var(--muted);margin-top:14px}
.panel-body .motto{font-family:var(--display);font-weight:700;color:var(--ink);font-size:1.05rem;margin:18px 0 6px}
.panel-body .photo{display:block;width:100%;height:auto;border-radius:14px;margin:4px 0 16px}
.checks{list-style:none;padding:0;margin:0 0 12px;display:grid;gap:8px}
.checks li{position:relative;padding-left:26px}
.checks li::before{content:"";position:absolute;left:0;top:.55em;width:14px;height:8px;border-left:2.5px solid var(--money);border-bottom:2.5px solid var(--money);transform:rotate(-45deg)}
.steps{list-style:none;counter-reset:step;padding:0;margin:8px 0 6px;display:grid;gap:10px}
.steps li{display:grid;grid-template-columns:32px 1fr;grid-template-rows:auto auto;column-gap:12px;align-items:start}
.steps li::before{counter-increment:step;content:counter(step);grid-row:1/3;width:32px;height:32px;border-radius:50%;background:var(--accent-soft);color:var(--accent-ink);display:grid;place-items:center;font-weight:700;font-size:.9rem;font-variant-numeric:tabular-nums}
.steps li strong{color:var(--ink)}
.steps li span{grid-column:2;font-size:.93rem}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0 12px}
.compare-item{border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:grid;gap:4px;font-size:.92rem}
.compare-item strong{color:var(--ink)}
.compare-item.is-us{border-color:var(--money);background:#F1FBF6}
.callout{background:var(--accent-soft);color:var(--ink);border-radius:14px;padding:16px 18px;margin:0 0 6px;font-size:1rem;line-height:1.55}
.trust{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0 6px}
.trust div{border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:grid;gap:2px}
.trust strong{font-family:var(--display);font-size:1.05rem;color:var(--ink);font-variant-numeric:tabular-nums}
.trust span{font-size:.82rem;color:var(--muted)}
.panel-foot{display:flex;align-items:center;gap:16px;padding:14px 28px 22px;border-top:1px solid var(--line)}

@keyframes pop{from{opacity:0;transform:translateY(14px) scale(.985)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
.panel[open]{animation:pop .22s cubic-bezier(.2,.8,.2,1)}
.panel[open]::backdrop{animation:fade .22s ease}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* ---- the no-scroll lock: one screen, no scrolling, on real desktops */
@media (min-width:1000px) and (min-height:760px), (max-width:999px){
  .more{display:flex}
  .plus-top{display:none}
}
@media (min-width:1000px) and (min-height:600px){
  html,body{height:100dvh;overflow:hidden}
}
@media (max-width:999px){
  .grid{grid-template-columns:repeat(2,minmax(0,1fr));grid-auto-rows:auto}
  .card{min-height:150px}
  .teaser{-webkit-line-clamp:unset;display:block}
}
@media (max-width:640px){
  .grid{grid-template-columns:1fr}
  .link-demo{display:none}
  .foot .foot-demo{display:inline}
  .foot{justify-content:center;text-align:center}
  .lang button span{display:none}
  .lang button{padding:7px 9px}
  .compare,.trust{grid-template-columns:1fr}
  .panel-head,.panel-body,.panel-foot{padding-left:18px;padding-right:18px}
  .panel{width:100vw;max-width:100vw;max-height:92dvh;margin:auto 0 0;border-radius:22px 22px 0 0}
  .btn{padding:9px 14px;font-size:.9rem}
}
@media (max-width:420px){
  .brand span{display:none}
}
"""

JS = r"""
(function(){
  var STR = JSON.parse(document.getElementById('i18n').textContent);
  var root = document.documentElement;
  var lang = root.lang === 'ru' ? 'ru' : 'en';
  var panel = document.getElementById('panel');
  var current = null, opener = null;

  function t(key, l){ return key.split('.').reduce(function(o,k){ return o == null ? o : o[k]; }, STR[l]); }

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
    document.title = t('meta.title', l);
    document.querySelectorAll('.lang button').forEach(function(b){ b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === l)); });
    try { localStorage.setItem('octopus.lang', l); } catch (e) {}
    try {
      if (/^https?:$/.test(location.protocol)) {
        var want = l === 'ru' ? '/ru/' : '/';
        if (location.pathname !== want) history.replaceState(null, '', want + location.search + location.hash);
      }
    } catch (e) {}
    if (panel.open && current) fill(current);
  }

  function fill(card){
    document.getElementById('panel-eyebrow').innerHTML = t('cards.' + card + '.eyebrow', lang);
    document.getElementById('panel-title').innerHTML = t('cards.' + card + '.hook', lang);
    document.getElementById('panel-body').innerHTML = t('cards.' + card + '.body', lang);
  }

  function open(card, from){
    current = card; opener = from || null;
    fill(card);
    document.getElementById('panel-body').scrollTop = 0;
    if (typeof panel.showModal === 'function') { if (!panel.open) panel.showModal(); }
    else panel.setAttribute('open', '');
    try { history.replaceState(null, '', location.pathname + location.search + '#' + card); } catch (e) {}
  }

  function close(){
    if (panel.open) panel.close(); else panel.removeAttribute('open');
  }

  panel.addEventListener('close', function(){
    try { if (location.hash) history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    if (opener && opener.focus) opener.focus();
    current = null;
  });
  panel.addEventListener('click', function(e){ if (e.target === panel) close(); });
  document.getElementById('panel-close').addEventListener('click', close);

  document.querySelectorAll('.card').forEach(function(card){
    var id = card.getAttribute('data-card');
    var btn = card.querySelector('h2 button');
    card.addEventListener('click', function(e){
      if (e.target.closest('a')) return;
      open(id, btn);
    });
  });

  document.querySelectorAll('.lang button').forEach(function(b){
    b.addEventListener('click', function(){ apply(b.getAttribute('data-lang')); });
  });

  // Initial language: an explicit earlier choice wins; otherwise a Russian browser gets Russian.
  var saved = null;
  try { saved = localStorage.getItem('octopus.lang'); } catch (e) {}
  var wanted = (saved === 'ru' || saved === 'en') ? saved
             : ((navigator.language || '').toLowerCase().indexOf('ru') === 0 ? 'ru' : lang);
  if (wanted !== lang) apply(wanted);

  // Deep link: octopustms.com/#free opens that card.
  var h = (location.hash || '').replace('#', '');
  if (h && STR.en.cards[h]) open(h, document.querySelector('.card[data-card="' + h + '"] h2 button'));
})();
"""


def jsonld(lang: str, strings: dict, canonical: str) -> str:
    graph = [
        {
            "@type": "SoftwareApplication",
            "@id": f"{SITE}/#app",
            "name": "Octopus TMS",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": canonical,
            "inLanguage": ["en", "ru"],
            "description": strings["meta"]["description"],
            "offers": [
                {"@type": "Offer", "price": "0", "priceCurrency": "USD", "name": "Free plan",
                 "description": "One truck, one driver, up to 10 booked loads a month. No card required."},
                {"@type": "Offer", "price": "20.00", "priceCurrency": "USD", "name": "Partnership plan",
                 "description": "$20 per booked load, refunded automatically if the load is cancelled before transport. No monthly fee."},
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
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": strings["faq"]["q"],
                "acceptedAnswer": {"@type": "Answer", "text": strings["faq"]["a"]},
            }],
        },
    ]
    return json_for_script({"@context": "https://schema.org", "@graph": graph})


def card_html(card: str, s: dict) -> str:
    c = s["cards"][card]
    return f"""
  <article class="card" data-card="{card}">
    <div class="card-top"><span class="eyebrow" data-i18n="cards.{card}.eyebrow">{c["eyebrow"]}</span><span class="plus plus-top" aria-hidden="true">+</span></div>
    <h2><button type="button" aria-haspopup="dialog" aria-controls="panel" data-i18n="cards.{card}.hook">{c["hook"]}</button></h2>
    <p class="teaser" data-i18n="cards.{card}.teaser">{c["teaser"]}</p>
    <span class="more" aria-hidden="true"><span data-i18n="ui.open">{s["ui"]["open"]}</span><span class="plus">+</span></span>
    <div class="card-body" hidden data-i18n="cards.{card}.body">{c["body"].strip()}</div>
  </article>"""


def landing(lang: str, prefix: str) -> str:
    strings = {"en": resolve(EN, prefix), "ru": resolve(RU, prefix)}
    s = strings[lang]
    canonical = f"{SITE}/ru/" if lang == "ru" else f"{SITE}/"
    cards = "".join(card_html(c, s) for c in CARD_ORDER)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
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
<meta name="theme-color" content="#EEF2F7">
<link rel="icon" href="{prefix}octopus-logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;800&family=Golos+Text:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{jsonld(lang, s, canonical)}</script>
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <a class="brand" href="{prefix if prefix else './'}">{LOGO_SVG}<span data-i18n="ui.brand">{s["ui"]["brand"]}</span></a>
  <div class="top-right">
    <div class="lang" role="group" aria-label="Language / Язык">
      <button type="button" data-lang="en" lang="en" aria-pressed="{'true' if lang == 'en' else 'false'}" aria-label="English">{FLAG_US}<span>EN</span></button>
      <button type="button" data-lang="ru" lang="ru" aria-pressed="{'true' if lang == 'ru' else 'false'}" aria-label="Русский">{FLAG_RU}<span>RU</span></button>
    </div>
    <a class="link-demo" href="{DEMO_URL}" data-i18n="ui.demo">{s["ui"]["demo"]}</a>
    <a class="btn" href="{REGISTER_URL}" data-i18n="ui.start">{s["ui"]["start"]}</a>
  </div>
</header>

<section class="hero">
  <h1 data-i18n="hero.h1">{s["hero"]["h1"]}</h1>
  <p class="sub" data-i18n="hero.sub">{s["hero"]["sub"]}</p>
  <div class="qa"><span class="q" data-i18n="hero.q">{s["hero"]["q"]}</span><span class="a" data-i18n="hero.a">{s["hero"]["a"]}</span></div>
</section>

<main class="grid" id="cards">{cards}
</main>

<footer class="foot">
  <span data-i18n="ui.footer_rights">{s["ui"]["footer_rights"]}</span>
  <nav aria-label="Legal">
    <a href="{prefix}privacy/" data-i18n="ui.privacy">{s["ui"]["privacy"]}</a>
    <a href="{prefix}terms/" data-i18n="ui.terms">{s["ui"]["terms"]}</a>
    <a href="{prefix}payment-terms/" data-i18n="ui.payment_terms">{s["ui"]["payment_terms"]}</a>
    <a href="{prefix}refund-policy/" data-i18n="ui.refund_policy">{s["ui"]["refund_policy"]}</a>
    <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
    <a class="foot-demo" href="{DEMO_URL}" data-i18n="ui.demo">{s["ui"]["demo"]}</a>
  </nav>
</footer>

<dialog class="panel" id="panel" aria-labelledby="panel-title">
  <div class="panel-head">
    <div><span class="eyebrow" id="panel-eyebrow"></span><h2 class="panel-hook" id="panel-title"></h2></div>
    <button type="button" class="close" id="panel-close" data-i18n-attr="aria-label:ui.close" aria-label="{attr(s["ui"]["close"])}">×</button>
  </div>
  <div class="panel-body" id="panel-body"></div>
  <div class="panel-foot"><a class="btn" href="{REGISTER_URL}" data-i18n="ui.panel_cta">{s["ui"]["panel_cta"]}</a></div>
</dialog>

<script id="i18n" type="application/json">{json_for_script(strings)}</script>
<script>{JS}</script>
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
:root{--ink:#0E1726;--ink-2:#3A4556;--muted:#69737F;--line:#D9DFE8;--paper:#EEF2F7;--accent:#0A5BFF;--accent-ink:#0646C7;
  --display:'Unbounded','Golos Text',system-ui,sans-serif;--body:'Golos Text',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif}
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:16px}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.6}
a{color:var(--accent-ink)}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px clamp(16px,3vw,32px);max-width:1180px;margin:0 auto}
.brand{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;font-size:1.05rem}
.brand .logo{width:34px;height:34px}
.back{font-weight:600;text-decoration:none;color:var(--ink-2);font-size:.95rem}
.back:hover{color:var(--accent-ink)}
main{background:#fff;border:1px solid var(--line);border-radius:24px;max-width:840px;margin:8px auto 32px;padding:clamp(22px,4vw,48px)}
h1{font-family:var(--display);font-weight:700;font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.15;letter-spacing:-.015em;margin:0 0 8px}
h2{font-size:1.25rem;margin:32px 0 10px;letter-spacing:-.01em}
h3{font-size:1.02rem;margin:22px 0 8px}
p,li{color:var(--ink-2);max-width:72ch}
p{margin:0 0 12px}
.doc-meta{color:var(--muted);font-size:.92rem;line-height:1.7}
ul,ol{padding-left:22px;margin:0 0 14px}
li{margin:0 0 6px}
strong{color:var(--ink)}
blockquote{margin:16px 0;padding:14px 18px;border-left:3px solid var(--accent);background:#F4F7FD;border-radius:0 12px 12px 0}
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
"""


def legal_page(out_dir: str, md_file: str, page_title: str) -> str:
    md = (SRC / "legal" / md_file).read_text(encoding="utf-8")
    title, body = md_to_html(md)
    title = title or page_title
    canonical = f"{SITE}/{out_dir}/"
    others = " ".join(
        f'<a href="../{d}/">{t}</a>' for d, _, t in LEGAL_PAGES if d != out_dir
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{attr(title)} — Octopus TMS</title>
<meta name="description" content="{attr(title)} for Octopus TMS, the carrier partner platform by Digital Ronin LLC.">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{attr(title)} — Octopus TMS">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<link rel="icon" href="../octopus-logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700&family=Golos+Text:wght@400;600;700&display=swap" rel="stylesheet">
<style>{LEGAL_CSS}</style>
</head>
<body>
<header class="top">
  <a class="brand" href="../">{LOGO_SVG}<span>Octopus TMS</span></a>
  <a class="back" href="../">← Back to octopustms.com</a>
</header>
<main>
<h1>{inline(title)}</h1>
{body}
</main>
<footer class="foot">
  <span>© {date.today().year} Digital Ronin LLC · <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></span>
  <nav>{others}</nav>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- sitemap / robots


def sitemap() -> str:
    urls = [
        (f"{SITE}/", "1.0", True),
        (f"{SITE}/ru/", "0.9", True),
    ] + [(f"{SITE}/{d}/", "0.3", False) for d, _, _ in LEGAL_PAGES]
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, prio, alternates in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{loc}</loc>")
        if alternates:
            parts.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/>')
            parts.append(f'    <xhtml:link rel="alternate" hreflang="ru" href="{SITE}/ru/"/>')
            parts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>')
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
    write(ROOT / "sitemap.xml", sitemap())
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
