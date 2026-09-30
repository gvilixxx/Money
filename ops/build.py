#!/usr/bin/env python3
"""Builds the public site on GitHub Pages from ops/config.json and ops/sites/*.json.

Output (all under docs/):
  index.html, accessibility.html     the brand's own landing page
  demos/<slug>/index.html            a draft or sample site for one business
  demos/<slug>/accessibility.html    its accessibility statement (IS 5568)
  robots.txt, .nojekyll

Usage: python3 ops/build.py                               build everything
       python3 ops/build.py --check                       validate data only
       python3 ops/build.py --live <slug> <outdir> [domain]  production site for a paying client
"""
import html
import json
import shutil
import sys
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "ops"
OUT = ROOT / "docs"
TODAY = date.today()
HEB_MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט",
              "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]


def e(v):
    return html.escape(str(v), quote=True)


def wa_link(e164, text=""):
    digits = "".join(ch for ch in str(e164) if ch.isdigit())
    if not digits:
        return ""
    q = f"?text={urllib.parse.quote(text)}" if text else ""
    return f"https://wa.me/{digits}{q}"


def tel_link(phone):
    digits = "".join(ch for ch in str(phone) if ch.isdigit() or ch == "+")
    return f"tel:{digits}" if digits else ""


def heb_date(d):
    return f"{d.day} ב{HEB_MONTHS[d.month - 1]} {d.year}"


# ----------------------------------------------------------------- themes
THEMES = {
    "trades": {
        "fonts": "family=Secular+One&family=Assistant:wght@400;600;700",
        "display": "'Secular One', 'Assistant', system-ui, sans-serif",
        "body": "'Assistant', system-ui, sans-serif",
        "bg": "#F4F6F9", "surface": "#FFFFFF", "ink": "#13233B", "muted": "#51607A",
        "line": "#DCE2EB", "accent": "#F2A516", "accent_ink": "#13233B", "band": "#13233B",
        "band_ink": "#F4F6F9",
    },
    "clinic": {
        "fonts": "family=Suez+One&family=IBM+Plex+Sans+Hebrew:wght@400;500;600",
        "display": "'Suez One', 'IBM Plex Sans Hebrew', serif",
        "body": "'IBM Plex Sans Hebrew', system-ui, sans-serif",
        "bg": "#F2F6F3", "surface": "#FFFFFF", "ink": "#1D3A33", "muted": "#566B64",
        "line": "#D6E2DA", "accent": "#E7956A", "accent_ink": "#1D3A33", "band": "#1D3A33",
        "band_ink": "#F2F6F3",
    },
}

ICONS = {
    "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/>',
    "wa": '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.2z"/>',
    "check": '<path d="M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6 11-11-1.4-1.4z"/>',
    "star": '<path d="m12 17.3 6.2 3.7-1.6-7 5.4-4.7-7.1-.6L12 2 9.1 8.7 2 9.3l5.4 4.7-1.6 7z"/>',
    "pin": '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/>',
    "clock": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 10.4 3.5 2.1-.8 1.3L11 13V7h2z"/>',
}


def icon(name, size=20):
    return (f'<svg aria-hidden="true" focusable="false" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="currentColor">{ICONS[name]}</svg>')


def base_css(t):
    return f"""
:root{{--bg:{t['bg']};--surface:{t['surface']};--ink:{t['ink']};--muted:{t['muted']};--line:{t['line']};
--accent:{t['accent']};--accent-ink:{t['accent_ink']};--band:{t['band']};--band-ink:{t['band_ink']};
--display:{t['display']};--body:{t['body']};color-scheme:light}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*{{transition:none!important;animation:none!important}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:1.0625rem;line-height:1.65}}
img{{max-width:100%}}
a{{color:inherit}}
:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:6px}}
.skip{{position:absolute;inset-inline-start:1rem;top:-4rem;background:var(--ink);color:var(--bg);padding:.6rem 1rem;border-radius:8px;z-index:50}}
.skip:focus{{top:1rem}}
.wrap{{max-width:68rem;margin-inline:auto;padding-inline:1.25rem}}
h1,h2,h3{{font-family:var(--display);font-weight:400;line-height:1.15;text-wrap:balance;margin:0}}
.btn{{display:inline-flex;align-items:center;gap:.55rem;min-height:3rem;padding:.7rem 1.35rem;border-radius:999px;
font-weight:700;text-decoration:none;border:2px solid transparent;font-size:1.05rem}}
.btn-main{{background:var(--accent);color:var(--accent-ink)}}
.btn-main:hover{{filter:brightness(.95)}}
.btn-ghost{{border-color:currentColor}}
.btn-ghost:hover{{background:color-mix(in srgb,currentColor 8%,transparent)}}
"""


# ----------------------------------------------------------------- demo site
def render_demo(site, cfg):
    t = THEMES[site.get("niche", "trades")]
    sample = bool(site.get("sample"))
    draft = bool(site.get("draft", True))
    brand = cfg.get("brand", "")
    brand_wa = wa_link(cfg.get("whatsapp_e164", ""), f"היי, ראיתי את האתר לדוגמה של {site['name']} ואשמח לטיוטה לעסק שלי")
    brand_url = cfg.get("site_base_url", "").rstrip("/") + "/"

    if sample:
        call_href = brand_url + "#contact"
        wa_href = brand_wa or call_href
        phone_text = "050-000-0000"
    else:
        call_href = tel_link(site.get("phone", ""))
        wa_href = wa_link(site.get("whatsapp_e164", ""), f"היי, הגעתי דרך האתר של {site['name']}") or call_href
        phone_text = site.get("phone", "")

    banner = ""
    if sample:
        banner = (f'<div class="banner" role="note">אתר לדוגמה. העסק, השמות והמספרים בדויים. '
                  f'<a href="{e(brand_url)}">רוצים אתר כזה לעסק שלכם?</a></div>')
    elif draft:
        banner = (f'<div class="banner" role="note">טיוטה להדגמה שהוכנה עבור {e(site["name"])}. '
                  f'זה עדיין לא האתר הרשמי של העסק.</div>')

    rating = ""
    if site.get("rating"):
        count = f" · {e(site['review_count'])} ביקורות" if site.get("review_count") else ""
        rating = f'<p class="rating">{icon("star", 18)}<span><b>{e(site["rating"])}</b>{count}</span></p>'

    services = "".join(
        f'<li class="svc"><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></li>' for s in site.get("services", []))
    reasons = "".join(f'<li>{icon("check", 22)}<span>{e(r)}</span></li>' for r in site.get("reasons", []))
    reviews = ""
    if site.get("reviews"):
        items = "".join(
            f'<figure class="rev"><blockquote>{e(r["text"])}</blockquote><figcaption>{e(r["author"])}</figcaption></figure>'
            for r in site["reviews"])
        src = e(site.get("reviews_source", "מתוך ביקורות לקוחות"))
        reviews = f'<section class="reviews" aria-labelledby="rev-h"><div class="wrap"><h2 id="rev-h">מה לקוחות אומרים</h2><p class="src">{src}</p><div class="rev-grid">{items}</div></div></section>'
    hours = "".join(f"<tr><th scope='row'>{e(d)}</th><td>{e(h)}</td></tr>" for d, h in site.get("hours", []))
    areas = " · ".join(e(a) for a in site.get("areas", []))
    license_line = f'<p class="lic">{e(site["license"])}</p>' if site.get("license") else ""
    address = f'<p>{icon("pin")}<span>{e(site["address"])}</span></p>' if site.get("address") else ""
    about = f'<p class="about">{e(site["about"])}</p>' if site.get("about") else ""
    contact_note = (f'<p>{icon("clock")}<span>{e(site["contact_note"])}</span></p>'
                    if site.get("contact_note") else f'<p>{icon("pin")}<span>{e(site["city"])} והסביבה</span></p>')
    robots = '<meta name="robots" content="noindex,nofollow">' if (draft or sample) else ""

    css = base_css(t) + """
.banner{background:var(--ink);color:var(--bg);text-align:center;padding:.55rem 1rem;font-size:.95rem}
.banner a{font-weight:700}
header.top{background:var(--surface);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:.9rem;flex-wrap:wrap}
.logo{font-family:var(--display);font-size:1.45rem;text-decoration:none}
.logo small{display:block;font-family:var(--body);font-size:.85rem;color:var(--muted);font-weight:600}
.hero{padding-block:3.2rem 3.6rem}
.hero .wrap{display:grid;gap:2rem;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);align-items:center}
.eyebrow{font-weight:700;color:var(--muted);letter-spacing:.02em;margin:0 0 .6rem}
.hero h1{font-size:clamp(2.1rem,5.5vw,3.5rem)}
.hero p.sub{font-size:1.2rem;color:var(--muted);max-width:34rem;margin:1rem 0 1.6rem}
.cta{display:flex;flex-wrap:wrap;gap:.75rem}
.rating{display:flex;align-items:center;gap:.45rem;margin:1.4rem 0 0;color:var(--ink)}
.rating svg{color:var(--accent)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:1.5rem}
.card h2{font-size:1.35rem;margin-bottom:.8rem}
.card p{display:flex;gap:.6rem;align-items:flex-start;margin:.5rem 0}
.card svg{flex:none;margin-top:.25rem;color:var(--muted)}
.card table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
.card th,.card td{padding:.3rem 0;text-align:start;border-bottom:1px dashed var(--line)}
.card th{font-weight:600;padding-inline-end:1rem}
section{padding-block:3.2rem}
section h2{font-size:clamp(1.7rem,3.6vw,2.4rem);margin-bottom:1.4rem}
.svc-grid{list-style:none;padding:0;margin:0;display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.svc{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:1.3rem 1.3rem 1.1rem}
.svc h3{font-size:1.2rem;margin-bottom:.35rem}
.svc p{margin:0;color:var(--muted)}
.why{background:var(--band);color:var(--band-ink)}
.why ul{list-style:none;padding:0;margin:0;display:grid;gap:1rem 2rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.why li{display:flex;gap:.7rem;align-items:flex-start;font-size:1.1rem}
.why svg{color:var(--accent);flex:none;margin-top:.2rem}
.about{max-width:42rem;font-size:1.15rem;margin:1.6rem 0 0}
.lic{color:color-mix(in srgb,var(--band-ink) 75%,transparent);margin:1rem 0 0;font-size:.95rem}
.src{color:var(--muted);margin:-.8rem 0 1.2rem;font-size:.95rem}
.rev-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.rev{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:1.3rem}
.rev blockquote{margin:0 0 .7rem;font-size:1.08rem}
.rev figcaption{color:var(--muted);font-weight:600}
.contact .wrap{display:grid;gap:1.5rem;grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));align-items:start}
.contact .big{font-family:var(--display);font-size:clamp(1.8rem,4vw,2.6rem);text-decoration:none;display:inline-block;margin:.3rem 0 1rem;font-variant-numeric:tabular-nums}
footer{border-top:1px solid var(--line);padding-block:1.6rem 6rem;color:var(--muted);font-size:.95rem}
footer .wrap{display:flex;flex-wrap:wrap;gap:.6rem 1.5rem;justify-content:space-between}
.dock{position:fixed;inset-inline:0;bottom:0;display:none;gap:.6rem;padding:.6rem 1rem calc(.6rem + env(safe-area-inset-bottom,0px));
background:var(--surface);border-top:1px solid var(--line);z-index:40}
.dock .btn{flex:1;justify-content:center}
@media (max-width:760px){.hero .wrap{grid-template-columns:minmax(0,1fr)}.dock{display:flex}header.top .btn{display:none}.hero{padding-block:2.2rem 2.6rem}}
"""
    title = f"{site['name']} | {site['profession']} ב{site['city']}"
    desc = site.get("subhead", "")
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t['fonts']}&display=swap">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">דלג לתוכן</a>
{banner}
<header class="top"><div class="wrap">
<a class="logo" href="#main">{e(site['name'])}<small>{e(site['profession'])} · {e(site['city'])}</small></a>
<a class="btn btn-main" href="{e(call_href)}">{icon('phone')}<span>{e(phone_text)}</span></a>
</div></header>
<main id="main">
<section class="hero"><div class="wrap">
<div>
<p class="eyebrow">{e(site['profession'])} ב{e(site['city'])} והסביבה</p>
<h1>{e(site['headline'])}</h1>
<p class="sub">{e(site['subhead'])}</p>
<div class="cta">
<a class="btn btn-main" href="{e(wa_href)}" target="_blank" rel="noopener">{icon('wa')}<span>שליחת הודעה בוואטסאפ</span></a>
<a class="btn btn-ghost" href="{e(call_href)}">{icon('phone')}<span>התקשרו עכשיו</span></a>
</div>
{rating}
</div>
<aside class="card" aria-labelledby="info-h">
<h2 id="info-h">שעות פעילות</h2>
<table>{hours}</table>
<p>{icon('pin')}<span>אזורי שירות: {areas}</span></p>
</aside>
</div></section>
<section aria-labelledby="svc-h"><div class="wrap">
<h2 id="svc-h">השירותים שלנו</h2>
<ul class="svc-grid">{services}</ul>
</div></section>
<section class="why" aria-labelledby="why-h"><div class="wrap">
<h2 id="why-h">למה לבחור בנו</h2>
<ul>{reasons}</ul>
{about}
{license_line}
</div></section>
{reviews}
<section class="contact" id="contact" aria-labelledby="c-h"><div class="wrap">
<div>
<h2 id="c-h">דברו איתנו</h2>
<a class="big" href="{e(call_href)}">{e(phone_text)}</a>
<div class="cta"><a class="btn btn-main" href="{e(wa_href)}" target="_blank" rel="noopener">{icon('wa')}<span>וואטסאפ</span></a></div>
</div>
<div class="card">{address}{contact_note}</div>
</div></section>
</main>
<footer><div class="wrap">
<span>© {TODAY.year} {e(site['name'])}</span>
<a href="accessibility.html">הצהרת נגישות</a>
<span>נבנה על ידי <a href="{e(brand_url)}">{e(brand)}</a></span>
</div></footer>
<nav class="dock" aria-label="יצירת קשר מהירה">
<a class="btn btn-main" href="{e(wa_href)}" target="_blank" rel="noopener">{icon('wa')}<span>וואטסאפ</span></a>
<a class="btn btn-ghost" href="{e(call_href)}">{icon('phone')}<span>חיוג</span></a>
</nav>
</body>
</html>
"""


def render_accessibility(name, contact_phone, contact_email, theme_key, home="index.html"):
    t = THEMES[theme_key]
    css = base_css(t) + """
main{padding-block:2.5rem 4rem}
main .wrap{max-width:44rem}
h1{font-size:2.2rem;margin-bottom:1rem}
h2{font-size:1.4rem;margin:2rem 0 .5rem}
ul{padding-inline-start:1.2rem}
"""
    contact = e(contact_phone) if contact_phone else "דרך פרטי יצירת הקשר באתר"
    email = f"<li>דוא\"ל: {e(contact_email)}</li>" if contact_email else ""
    return f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>הצהרת נגישות | {e(name)}</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t['fonts']}&display=swap">
<style>{css}</style></head>
<body><main id="main"><div class="wrap">
<p><a href="{e(home)}">חזרה לאתר</a></p>
<h1>הצהרת נגישות</h1>
<p>{e(name)} רואה חשיבות רבה במתן שירות שוויוני לכל הלקוחות, ובכלל זה לאנשים עם מוגבלות. האתר נבנה כך שיעמוד בדרישות תקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), התשע"ג-2013, ובתקן הישראלי ת"י 5568, המבוסס על הנחיות WCAG 2.0 ברמה AA.</p>
<h2>מה עשינו באתר</h2>
<ul>
<li>מבנה כותרות היררכי וסימון סמנטי של אזורי העמוד.</li>
<li>ניווט מלא במקלדת, עם סימון ברור של הרכיב שבפוקוס וקישור לדילוג לתוכן.</li>
<li>ניגודיות צבעים מספקת בין טקסט לרקע.</li>
<li>התאמה לצפייה בנייד ולהגדלת טקסט עד 200% בלי אובדן תוכן.</li>
<li>תיאור טקסטואלי לרכיבים גרפיים, והסתרת סמלים דקורטיביים מקוראי מסך.</li>
<li>כיבוד הגדרת "הפחתת תנועה" של מערכת ההפעלה.</li>
</ul>
<h2>נתקלתם בבעיה?</h2>
<p>אם מצאתם רכיב שאינו נגיש, נשמח לשמוע ולתקן. פנו אלינו:</p>
<ul><li>טלפון: {contact}</li>{email}</ul>
<p>תאריך עדכון ההצהרה: {heb_date(TODAY)}</p>
</div></main></body></html>
"""


# ----------------------------------------------------------------- landing page
def render_landing(cfg, samples):
    brand = cfg.get("brand", "אתר ביום")
    owner = cfg.get("owner_name", "")
    phone = cfg.get("phone_display", "")
    wa = wa_link(cfg.get("whatsapp_e164", ""), "היי, אשמח לטיוטה חינם לאתר לעסק שלי. שם העסק: ")
    configured = bool(wa)
    setup = f"{cfg.get('price_setup', 1490):,}"
    monthly = cfg.get("price_monthly", 99)
    cta_href = wa if configured else "#contact"
    robots = "" if configured else '<meta name="robots" content="noindex">'
    sample_cards = "".join(
        f'<a class="sample" href="demos/{e(s["slug"])}/"><span class="tag">{e(s["profession"])}</span>'
        f'<b>{e(s["name"])}</b><span class="go">לצפייה באתר לדוגמה</span></a>' for s in samples)
    contact_block = (
        f'<a class="btn-wa" href="{e(wa)}" target="_blank" rel="noopener">{icon("wa", 22)}<span>שלחו לנו שם של עסק בוואטסאפ</span></a>'
        f'<p class="num">{e(phone)}</p>' if configured else
        '<p class="soon">פרטי יצירת הקשר יתעדכנו כאן בקרוב.</p>')
    owner_line = f"<p class=\"sig\">{e(owner)}, {e(brand)}</p>" if owner else ""
    biz_id = f" · עוסק {e(cfg['business_id'])}" if cfg.get("business_id") else ""

    css = """
:root{--paper:#F6F8F7;--card:#FFFFFF;--ink:#0F1D2B;--muted:#526170;--line:#DDE4E1;--green:#0B7A4E;--green-soft:#DFF3E9;
--bubble-out:#D9F7C9;--bubble-in:#FFFFFF;--chat:#EAE3D6;
--display:'Karantina','Assistant',system-ui,sans-serif;--body:'Assistant',system-ui,sans-serif;color-scheme:light}
/* layout: one strong headline beside a real WhatsApp exchange; everything after is a short, scannable sequence */
*{box-sizing:border-box}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:1.0625rem;line-height:1.6}
a{color:inherit}
:focus-visible{outline:3px solid var(--green);outline-offset:3px;border-radius:6px}
.wrap{max-width:70rem;margin-inline:auto;padding-inline:1.25rem}
h1,h2{font-family:var(--display);font-weight:700;line-height:.95;margin:0;text-wrap:balance;letter-spacing:.01em}
.top{display:flex;justify-content:space-between;align-items:center;padding-block:1.1rem}
.mark{font-family:var(--display);font-size:2rem;font-weight:700;text-decoration:none}
.mark i{font-style:normal;color:var(--green)}
.top a.small{font-weight:700;text-decoration:none;border-bottom:2px solid var(--green)}
.hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:2.5rem;align-items:center;padding-block:1.5rem 3.5rem}
.hero h1{font-size:clamp(3.4rem,9vw,6.4rem)}
.hero h1 em{font-style:normal;color:var(--green)}
.lede{font-size:1.25rem;color:var(--muted);max-width:32rem;margin:1.2rem 0 1.8rem}
.btn-wa{display:inline-flex;align-items:center;gap:.6rem;background:var(--green);color:#fff;text-decoration:none;font-weight:700;
font-size:1.12rem;padding:.9rem 1.5rem;border-radius:999px;min-height:3.2rem}
.btn-wa:hover{filter:brightness(1.08)}
.fine{color:var(--muted);font-size:.95rem;margin:.8rem 0 0}
.phone{background:var(--chat);border-radius:28px;padding:1.1rem;border:8px solid var(--ink);max-width:22rem;justify-self:center;width:100%}
.phone .who{display:flex;align-items:center;gap:.6rem;font-weight:700;margin-bottom:.9rem}
.phone .who span{width:2.1rem;height:2.1rem;border-radius:50%;background:var(--green);color:#fff;display:grid;place-items:center;font-size:.95rem}
.msg{max-width:85%;padding:.55rem .8rem;border-radius:14px;margin:.45rem 0;font-size:.98rem;line-height:1.45;box-shadow:0 1px 0 rgba(15,29,43,.08)}
.out{background:var(--bubble-out);margin-inline-start:auto;border-end-end-radius:4px}
.in{background:var(--bubble-in);border-end-start-radius:4px}
.linkcard{display:block;background:var(--card);border-radius:10px;overflow:hidden;margin-top:.4rem;font-size:.9rem}
.linkcard b{display:block;padding:.45rem .6rem 0}
.linkcard small{display:block;padding:0 .6rem .5rem;color:var(--muted)}
.linkcard .shot{display:block;height:4.2rem;background:linear-gradient(135deg,#13233B 0 55%,#F2A516 55% 100%)}
.msg time{display:block;text-align:end;font-size:.72rem;color:var(--muted)}
section{padding-block:3.5rem;border-top:1px solid var(--line)}
section h2{font-size:clamp(2.4rem,6vw,3.6rem);margin-bottom:1.6rem}
.steps{list-style:none;counter-reset:s;padding:0;margin:0;display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.steps li{counter-increment:s;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.4rem}
.steps li::before{content:counter(s);font-family:var(--display);font-size:3rem;line-height:1;color:var(--green);display:block;margin-bottom:.4rem}
.steps b{display:block;font-size:1.15rem;margin-bottom:.3rem}
.steps p{margin:0;color:var(--muted)}
.incl{display:grid;gap:.7rem 2rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));list-style:none;padding:0;margin:0}
.incl li{display:flex;gap:.6rem;align-items:flex-start}
.incl svg{color:var(--green);flex:none;margin-top:.2rem}
.price{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1.2rem;align-items:stretch}
.tier{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.5rem}
.tier.main{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.tier .amt{font-family:var(--display);font-size:3.6rem;line-height:1;font-variant-numeric:tabular-nums}
.tier .amt small{font-family:var(--body);font-size:1rem;font-weight:600}
.tier p{margin:.6rem 0 0}
.samples{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.sample{display:flex;flex-direction:column;gap:.3rem;text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.3rem}
.sample:hover{border-color:var(--green)}
.sample .tag{font-size:.85rem;font-weight:700;color:var(--green);letter-spacing:.02em}
.sample b{font-size:1.3rem}
.sample .go{color:var(--muted);text-decoration:underline}
details{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1rem 1.2rem;margin-bottom:.7rem}
summary{font-weight:700;cursor:pointer}
details p{margin:.6rem 0 0;color:var(--muted)}
#contact{text-align:center}
#contact h2{margin-bottom:1rem}
.num{font-family:var(--display);font-size:2.4rem;margin:.8rem 0 0;font-variant-numeric:tabular-nums}
.soon{color:var(--muted)}
.sig{color:var(--muted);margin-top:1rem}
footer{padding-block:1.5rem 2.5rem;color:var(--muted);font-size:.92rem;border-top:1px solid var(--line)}
footer .wrap{display:flex;gap:.5rem 1.5rem;flex-wrap:wrap;justify-content:space-between}
@media (max-width:820px){.hero{grid-template-columns:minmax(0,1fr)}}
"""
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(brand)} | אתר לעסק שלך, טיוטה מוכנה תוך 24 שעות</title>
<meta name="description" content="אתר מקצועי לעסקים קטנים. שולחים שם של עסק, מקבלים טיוטה מוכנה תוך 24 שעות, ומשלמים רק אם אוהבים.">
{robots}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Karantina:wght@700&family=Assistant:wght@400;600;700&display=swap">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header class="top"><a class="mark" href="#">{e(brand)}<i>.</i></a><a class="small" href="#contact">בקשת טיוטה</a></header>
<main>
<div class="hero">
<div>
<h1>האתר של העסק שלך. <em>מוכן לפני שמשלמים.</em></h1>
<p class="lede">שולחים לנו את שם העסק, ותוך 24 שעות מקבלים קישור לטיוטה של אתר מקצועי. אוהבים? עולים לאוויר. לא מתאים? לא משלמים שקל.</p>
<a class="btn-wa" href="{e(cta_href)}" {'target="_blank" rel="noopener"' if configured else ''}>{icon('wa', 22)}<span>אני רוצה טיוטה חינם</span></a>
<p class="fine">בלי התחייבות ובלי פרטי אשראי.</p>
</div>
<div class="phone" role="img" aria-label="דוגמה לשיחת וואטסאפ: שולחים שם של עסק, מקבלים קישור לטיוטה, ומחליטים">
<p class="who"><span aria-hidden="true">א</span>{e(brand)}</p>
<p class="msg out">היי, יש לי עסק לתיקוני חשמל בפתח תקווה. אפשר טיוטה?<time>09:12</time></p>
<p class="msg in">בשמחה. הטיוטה תהיה אצלך מחר בבוקר.<time>09:14</time></p>
<div class="msg in"><span class="linkcard"><span class="shot"></span><b>הטיוטה שלך מוכנה</b><small>מותאם לנייד · כפתור וואטסאפ · הצהרת נגישות</small></span><time>08:40</time></div>
<p class="msg out">וואו, זה נראה מעולה. איך מעלים?<time>08:52</time></p>
</div>
</div>

<section aria-labelledby="how-h">
<h2 id="how-h">איך זה עובד</h2>
<ol class="steps">
<li><b>שולחים שם של עסק</b><p>הודעת וואטסאפ אחת עם שם העסק, או קישור לדף שלו בגוגל או באינסטגרם.</p></li>
<li><b>מקבלים טיוטה תוך 24 שעות</b><p>אתר מלא עם השירותים, שעות הפעילות וכפתורי חיוג ווואטסאפ, בקישור שאפשר לפתוח בנייד.</p></li>
<li><b>מחליטים</b><p>אוהבים? מחברים דומיין ועולים לאוויר באותו יום. לא מתאים? מוחקים את הטיוטה, בלי עלות.</p></li>
</ol>
</section>

<section aria-labelledby="inc-h">
<h2 id="inc-h">מה יש באתר</h2>
<ul class="incl">
<li>{icon('check', 22)}<span>עיצוב מותאם לנייד, כי שם נמצאים רוב הלקוחות שלכם</span></li>
<li>{icon('check', 22)}<span>כפתור וואטסאפ וכפתור חיוג בכל מסך</span></li>
<li>{icon('check', 22)}<span>שירותים, שעות פעילות ואזורי שירות</span></li>
<li>{icon('check', 22)}<span>ביקורות של לקוחות אמיתיים</span></li>
<li>{icon('check', 22)}<span>הצהרת נגישות לפי תקן 5568, כפי שהחוק מחייב</span></li>
<li>{icon('check', 22)}<span>טעינה מהירה ומבנה שגוגל מבין</span></li>
</ul>
</section>

<section aria-labelledby="price-h">
<h2 id="price-h">כמה זה עולה</h2>
<div class="price">
<div class="tier main"><p class="amt">{setup} ₪ <small>פעם אחת</small></p><p>בניית האתר, חיבור לדומיין שלכם והעלאה לאוויר. משלמים רק אחרי שראיתם את הטיוטה.</p></div>
<div class="tier"><p class="amt">{monthly} ₪ <small>לחודש</small></p><p>אחסון, גיבוי, עדכוני תוכן ותמיכה. אפשר לבטל בכל חודש.</p></div>
</div>
</section>

<section aria-labelledby="ex-h">
<h2 id="ex-h">אתרים לדוגמה</h2>
<div class="samples">{sample_cards}</div>
</section>

<section aria-labelledby="faq-h">
<h2 id="faq-h">שאלות נפוצות</h2>
<details><summary>מה אם אין לי דומיין?</summary><p>נעזור לכם לרכוש דומיין בשם העסק. העלות היא בדרך כלל 50 עד 100 ₪ לשנה, והדומיין רשום על שמכם.</p></details>
<details><summary>אפשר לשנות דברים בטיוטה?</summary><p>כן. שולחים בוואטסאפ מה לשנות, ואנחנו מעדכנים. שינויים שוטפים כלולים במנוי החודשי.</p></details>
<details><summary>של מי האתר?</summary><p>שלכם. הדומיין רשום על שמכם, ואם תעזבו נעביר לכם את כל הקבצים.</p></details>
<details><summary>למה צריך הצהרת נגישות?</summary><p>החוק בישראל מחייב אתרים של עסקים להיות נגישים ולפרסם הצהרת נגישות. כל אתר שלנו נבנה לפי התקן וכולל אותה.</p></details>
</section>

<section id="contact" aria-labelledby="ct-h">
<h2 id="ct-h">רוצים לראות את האתר שלכם?</h2>
{contact_block}
{owner_line}
</section>
</main>
</div>
<footer><div class="wrap"><span>© {TODAY.year} {e(brand)}{biz_id}</span><a href="accessibility.html">הצהרת נגישות</a></div></footer>
</body>
</html>
"""


# ----------------------------------------------------------------- build
REQUIRED = ["slug", "niche", "name", "profession", "city", "headline", "subhead", "services", "reasons", "hours", "areas"]


def load_sites():
    sites = []
    for p in sorted((OPS / "sites").glob("*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED if not s.get(k)]
        if missing:
            raise SystemExit(f"{p.name}: missing {missing}")
        if s["niche"] not in THEMES:
            raise SystemExit(f"{p.name}: unknown niche {s['niche']}")
        if not s.get("sample") and not (s.get("phone") or s.get("whatsapp_e164")):
            raise SystemExit(f"{p.name}: a real business needs phone or whatsapp_e164")
        sites.append(s)
    return sites


def build_live(slug, outdir, domain=""):
    """Production build for a paying client: no draft banner, indexable, own folder."""
    cfg = json.loads((OPS / "config.json").read_text(encoding="utf-8"))
    site = next((s for s in load_sites() if s["slug"] == slug), None)
    if not site:
        raise SystemExit(f"no site with slug {slug}")
    site = dict(site, draft=False, sample=False)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    page = render_demo(site, cfg)
    if domain:
        page = page.replace("</title>", f"</title>\n<link rel=\"canonical\" href=\"https://{e(domain)}/\">", 1)
        (out / "CNAME").write_text(domain + "\n", encoding="utf-8")
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "accessibility.html").write_text(
        render_accessibility(site["name"], site.get("phone", ""), site.get("email", ""), site["niche"]), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"live build for {slug} in {out}" + (f" (domain {domain})" if domain else ""))


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--live":
        build_live(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        return
    cfg = json.loads((OPS / "config.json").read_text(encoding="utf-8"))
    sites = load_sites()
    if "--check" in sys.argv:
        print(f"ok: {len(sites)} sites")
        return
    demos = OUT / "demos"
    if demos.exists():
        shutil.rmtree(demos)
    demos.mkdir(parents=True)
    for s in sites:
        d = demos / s["slug"]
        d.mkdir()
        (d / "index.html").write_text(render_demo(s, cfg), encoding="utf-8")
        contact = cfg.get("phone_display", "") if s.get("sample") else s.get("phone", "")
        (d / "accessibility.html").write_text(
            render_accessibility(s["name"], contact, "", s["niche"]), encoding="utf-8")
    samples = [s for s in sites if s.get("sample")]
    (OUT / "index.html").write_text(render_landing(cfg, samples), encoding="utf-8")
    (OUT / "accessibility.html").write_text(
        render_accessibility(cfg.get("brand", ""), cfg.get("phone_display", ""), cfg.get("email", ""), "trades"),
        encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /Money/demos/\nDisallow: /demos/\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    real = len(sites) - len(samples)
    print(f"built landing + {len(samples)} samples + {real} drafts")
    if not wa_link(cfg.get("whatsapp_e164", "")):
        print("WARNING: config.whatsapp_e164 is empty, landing page has no contact button and is noindex")


if __name__ == "__main__":
    main()
