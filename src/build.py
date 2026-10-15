#!/usr/bin/env python3
"""Builds octopustms.com from src/.

    python3 src/build.py

Outputs (all committed, GitHub Pages serves the repo as-is):
  index.html            English LLMP landing page (pre-rendered, toggle to RU without reload)
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

from strings import CONTACT_EMAIL, DEMO_URL, EN, REGISTER_URL, RU, SITE, STAGES

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
            return node.format(**ctx) if "{" in node else node
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
.btn-lg{font-size:16px;padding:14px 24px}
.btn-xl{font-size:17px;padding:16px 28px}
.link{font-weight:600;font-size:15px;color:var(--ink2);white-space:nowrap}
.link:hover{color:var(--accent-ink)}
.ctas{display:flex;flex-wrap:wrap;gap:14px 20px;align-items:center}

/* ---- top bar */
.top{height:72px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:inline-flex;align-items:center;gap:10px;font-weight:700;font-size:17px;letter-spacing:-.01em;color:var(--ink);white-space:nowrap}
.brand:hover{color:var(--ink)}
.brand .logo{width:34px;height:34px;flex:none}
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
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:64px;align-items:end;padding-top:64px;padding-bottom:72px}
.hero-l{display:flex;flex-direction:column;gap:22px}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(84px,12.8vw,184px);line-height:.86;letter-spacing:-.05em}
.hero h3{font-family:var(--display);font-weight:600;font-size:clamp(20px,2vw,28px);line-height:1.2;letter-spacing:-.015em;color:var(--accent-ink)}
.hero .sub{font-size:clamp(18px,1.55vw,22px);line-height:1.5;color:var(--ink2);max-width:640px;text-wrap:pretty}
.hero .sub em{white-space:nowrap;font-style:italic;color:var(--money);font-weight:600}
.price{background:var(--card);border:1px solid var(--line);border-radius:24px;padding:clamp(24px,2.5vw,36px);display:flex;flex-direction:column;gap:20px;box-shadow:0 30px 60px -40px var(--glow)}
.price .motto{color:var(--ink);font-family:var(--display);font-weight:800;font-size:clamp(26px,2.4vw,34px);line-height:1.1;letter-spacing:-.02em}
.price p{font-size:19px;line-height:1.55;color:var(--ink2)}
.price p b{font-family:var(--display);font-size:26px;color:var(--money);letter-spacing:-.02em}

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
.sasr h2{flex:1;font-family:var(--display);font-weight:800;font-size:clamp(34px,3.1vw,44px);letter-spacing:-.025em;white-space:nowrap}
.sasr h2 span{font-weight:600;font-size:clamp(17px,1.55vw,22px);color:var(--muted);letter-spacing:-.01em}
.rules{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.rule{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:30px;display:flex;flex-direction:column;gap:22px}
.rule p{font-size:clamp(19px,1.5vw,21px);line-height:1.4;font-weight:600}
.sasr .close{margin-top:44px;font-family:var(--display);font-weight:600;font-size:clamp(21px,2vw,28px);line-height:1.35;letter-spacing:-.015em;max-width:1020px;text-wrap:pretty}
.hl{color:var(--accent-ink)}

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

/* ---- medium screens */
@media (max-width:1180px){
  .std .in{grid-template-columns:1fr;gap:48px}
}
@media (max-width:1080px){
  /* The spine turns vertical: one stop per row, the rail on the left. */
  .spine{display:none}
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
  .hero{grid-template-columns:1fr;gap:36px;padding-top:40px;padding-bottom:56px}
  .why{grid-template-columns:1fr;gap:18px;padding-top:80px}
  .why .eyebrow{padding-top:0}
  .rules{grid-template-columns:1fr}
  .rule{flex-direction:row;align-items:center;gap:20px;padding:22px}
  .rule svg{flex:none;width:60px;height:60px}
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
  .foot nav{justify-content:center}
}
@media (max-width:440px){
  .brand span{display:none}
  .top-right{gap:8px}
  .rule{flex-direction:column;align-items:flex-start}
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
    document.title = t('meta.title', l);
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

  // ---- old deep links from the six-card page (#free, #one, ...) land on the matching section.
  var OLD = {free:'top', one:'lifecycle', boards:'lifecycle', track:'lifecycle', paper:'lifecycle', founder:'why'};
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
        },
    ]
    return json_for_script({"@context": "https://schema.org", "@graph": graph})


def i18n(key: str, value: str, tag: str = "span", cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-i18n="{key}">{value}</{tag}>'


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


def stops_html(s: dict) -> str:
    out = []
    for i, key in enumerate(STAGES):
        name, desc = s["life"][key]
        dot = "$" if key == "paid" else str(i + 1)
        ching = f' <span class="ching" aria-hidden="true" data-i18n="life.chaching">{s["life"]["chaching"]}</span>' if key == "paid" else ""
        out.append(
            f'<li class="stop {key}"><span class="dot" aria-hidden="true">{dot}</span>'
            f'<span class="name"><span data-i18n="life.{key}.0">{name}</span>{ching}</span>'
            f'<span class="desc" data-i18n="life.{key}.1">{desc}</span></li>'
        )
    return "\n      ".join(out)


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
    start = f'<a class="btn" href="{REGISTER_URL}" data-i18n="ui.start">{ui["start"]}</a>'
    demo = f'<a class="link" href="{DEMO_URL}" data-i18n="ui.demo">{ui["demo"]}</a>'
    rules = "".join(
        f'\n      <li class="rule">{icon}<p data-i18n="sasr.r{i + 1}">{s["sasr"][f"r{i + 1}"]}</p></li>'
        for i, icon in enumerate(RULE_ICONS)
    )
    js = JS.replace("__THEME_COLORS__", json.dumps(THEME_COLOR))
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
<style>{THEME_CSS}{CSS}</style>
</head>
<body>
<header class="in top" id="top">
  <a class="brand" href="#top">{LOGO_SVG}<span data-i18n="ui.brand">{ui["brand"]}</span></a>
  <div class="top-right">
    <div class="lang" role="group" aria-label="Language / Язык">
      <button type="button" data-lang="en" lang="en" aria-pressed="{'true' if lang == 'en' else 'false'}" aria-label="English">{FLAG_US}<span>EN</span></button>
      <button type="button" data-lang="ru" lang="ru" aria-pressed="{'true' if lang == 'ru' else 'false'}" aria-label="Русский">{FLAG_RU}<span>RU</span></button>
    </div>
    <button type="button" class="theme" id="theme" data-i18n-attr="aria-label:ui.theme,title:ui.theme" aria-label="{attr(ui["theme"])}" title="{attr(ui["theme"])}">{ICON_MOON}{ICON_SUN}</button>
    {demo}
    {start}
  </div>
</header>

<main>
<section class="in hero">
  <div class="hero-l">
    <h1>{s["hero"]["h1"]}</h1>
    {i18n("hero.h3", s["hero"]["h3"], "h3")}
    {i18n("hero.sub", s["hero"]["sub"], "p", "sub")}
  </div>
  <div class="price">
    {i18n("hero.motto", s["hero"]["motto"], "p", "motto")}
    {i18n("hero.price", s["hero"]["price"], "p")}
    <div class="ctas"><a class="btn btn-lg" href="{REGISTER_URL}" data-i18n="ui.start">{ui["start"]}</a>{demo}</div>
  </div>
</section>

<section class="band" id="lifecycle" aria-labelledby="life-h">
  <div class="in">
    <div class="band-head"><h2 class="eyebrow" id="life-h" data-i18n="life.eyebrow">{s["life"]["eyebrow"]}</h2>{i18n("life.chain", s["life"]["chain"], "span", "chain")}</div>
    {spine_svg(s)}
    <ol class="stops">
      {stops_html(s)}
    </ol>
  </div>
</section>

<section class="in why" id="why" aria-labelledby="why-h">
  <h2 class="eyebrow" id="why-h" data-i18n="why.eyebrow">{s["why"]["eyebrow"]}</h2>
  <div class="why-body">
    {i18n("why.p1", s["why"]["p1"], "p", "p1")}
    {i18n("why.p2", s["why"]["p2"], "p", "p")}
    {i18n("why.p3", s["why"]["p3"], "p", "p")}
    {i18n("why.p4", s["why"]["p4"], "p", "p4")}
  </div>
</section>
<div class="sonar">
  {SONAR_SVG}
  {i18n("why.sonar", s["why"]["sonar"], "p")}
</div>

<section class="in sasr" id="security" aria-labelledby="sasr-h">
  <div class="sasr-head">{i18n("sasr.eyebrow", s["sasr"]["eyebrow"], "span", "eyebrow")}<h2 id="sasr-h">{s["sasr"]["title"]} {i18n("sasr.full", s["sasr"]["full"])}</h2></div>
  <ul class="rules">{rules}
  </ul>
  {i18n("sasr.close", s["sasr"]["close"], "p", "close")}
</section>

<section class="std" id="standard" aria-labelledby="std-h">
  <div class="in">
    <div class="std-text">
      {i18n("std.eyebrow", s["std"]["eyebrow"], "span", "eyebrow")}
      <h2 id="std-h" data-i18n="std.h2">{s["std"]["h2"]}</h2>
      {i18n("std.p", s["std"]["p"], "p")}
    </div>
    {plate_svg(s)}
  </div>
</section>

<section class="in end">
  {i18n("end.byline", s["end"]["byline"], "p")}
  <div class="ctas"><a class="btn btn-xl" href="{REGISTER_URL}" data-i18n="ui.start">{ui["start"]}</a>{demo}</div>
</section>
</main>

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
.brand{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;font-size:1.05rem}
.brand .logo{width:34px;height:34px}
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
<script>{THEME_INIT}</script>
<style>{THEME_CSS}{LEGAL_CSS}</style>
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
