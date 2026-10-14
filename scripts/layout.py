"""Page shell: <head>, header, navigation, language menu and footer."""

from __future__ import annotations

import json

from site_lib import (
    BASE,
    ORIGIN,
    PAGES,
    PROMO_URL,
    REPO_URL,
    esc,
    fmt_time_utc,
    json_ld,
    page_url,
    star_svg,
)

FONT_URL = "https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900{extra}&display=swap"
NAV_ORDER = ["download", "weapons", "maps", "modes", "guide", "news", "charts"]
CURRENT_LANG = ' aria-current="true"'
CURRENT_PAGE = ' aria-current="page"'
GLOBE = (
    '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
    'stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>'
)


def head(ctx: dict, page: str, extra_ld: list[str]) -> str:
    lang, langs = ctx["lang"], ctx["langs"]
    copy = lang["pages"][page]
    canonical = page_url(lang, page, absolute=True)
    alternates = "".join(
        f'<link rel="alternate" hreflang="{esc(l["meta"]["hreflang"])}" href="{esc(page_url(l, page, True))}">'
        for l in langs.values()
    )
    alternates += f'<link rel="alternate" hreflang="x-default" href="{esc(page_url(langs["en"], page, True))}">'
    og_alt = "".join(
        f'<meta property="og:locale:alternate" content="{esc(l["meta"]["og_locale"])}">'
        for code, l in langs.items()
        if code != lang["meta"]["lang"]
    )
    extra_font = "&family=Oswald:wght@600;700" if lang["meta"]["lang"] == "ru" else ""
    image = ctx["og_image"]
    return f"""<!doctype html>
<html lang="{esc(lang['meta']['html_lang'])}" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(copy['title'])}</title>
<meta name="description" content="{esc(copy['description'])}">
<link rel="canonical" href="{esc(canonical)}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(lang['site']['name'])}">
<meta property="og:title" content="{esc(copy['title'])}">
<meta property="og:description" content="{esc(copy['description'])}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:locale" content="{esc(lang['meta']['og_locale'])}">
{og_alt}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1f2328">
<meta name="color-scheme" content="dark">
<link rel="icon" href="{BASE}/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://shared.akamai.steamstatic.com" crossorigin>
<link rel="stylesheet" href="{esc(FONT_URL.format(extra=extra_font))}">
<link rel="stylesheet" href="{BASE}/assets/style.css?v={ctx['asset_version']}">
{''.join(extra_ld)}
</head>"""


def lang_menu(ctx: dict, page: str) -> str:
    lang, langs = ctx["lang"], ctx["langs"]
    items = "".join(
        f'<li><a href="{esc(page_url(l, page))}" hreflang="{esc(l["meta"]["hreflang"])}" lang="{esc(l["meta"]["html_lang"])}"'
        f'{CURRENT_LANG if code == lang["meta"]["lang"] else ""} data-lang="{esc(code)}">{esc(l["meta"]["name"])}</a></li>'
        for code, l in langs.items()
    )
    return (
        f'<details class="lang-menu"><summary aria-label="{esc(lang["site"]["lang_label"])}">{GLOBE}'
        f'<span>{esc(lang["meta"]["name"])}</span></summary><ul>{items}</ul></details>'
    )


def header(ctx: dict, page: str) -> str:
    lang = ctx["lang"]
    site = lang["site"]
    links = "".join(
        f'<li><a href="{esc(page_url(lang, p))}"{CURRENT_PAGE if p == page else ""}>{esc(site["nav"][p])}</a></li>'
        for p in NAV_ORDER
    )
    return f"""<body data-page="{page}">
<a class="skip" href="#main">{esc(site['skip'])}</a>
<header class="top">
  <div class="wrap top-row">
    <a class="brand" href="{esc(page_url(lang, 'home'))}">{star_svg(22)}<span>{esc(site['short'])}</span></a>
    {lang_menu(ctx, page)}
  </div>
  <nav class="wrap nav" aria-label="{esc(site['menu'])}"><ul>{links}</ul></nav>
  <div class="stripes{' stripes-thin' if page != 'home' else ''}" aria-hidden="true"></div>
</header>
<div class="lang-suggest" id="lang-suggest" hidden></div>"""


def suggest_payload(ctx: dict, page: str) -> str:
    data = {
        code: {
            "name": l["meta"]["name"],
            "html": l["meta"]["html_lang"],
            "url": page_url(l, page),
            "suggest": l["site"]["suggest"],
            "go": l["site"]["suggest_go"],
            "close": l["site"]["suggest_close"],
        }
        for code, l in ctx["langs"].items()
    }
    payload = json.dumps({"current": ctx["lang"]["meta"]["lang"], "langs": data}, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")
    return f'<script type="application/json" id="lang-data">{payload}</script>'


def footer(ctx: dict, page: str) -> str:
    lang, langs, steam = ctx["lang"], ctx["langs"], ctx["steam"]
    site, promo = lang["site"], ctx["promo"]
    nav = "".join(
        f'<li><a href="{esc(page_url(lang, p))}">{esc(site["nav"][p])}</a></li>' for p, _ in PAGES
    )
    other_langs = "".join(
        f'<li><a href="{esc(page_url(l, "home"))}" hreflang="{esc(l["meta"]["hreflang"])}" lang="{esc(l["meta"]["html_lang"])}">{esc(l["meta"]["name"])}</a></li>'
        for l in langs.values()
    )
    fetched = steam.get("fetched_at")
    updated = (
        f'<p class="updated">{esc(site["updated"])}: <time datetime="{esc(fetched)}" data-rel>{esc(fmt_time_utc(fetched, lang))} UTC</time></p>'
        if fetched
        else ""
    )
    return f"""<footer class="foot">
  <div class="stripes stripes-thin" aria-hidden="true"></div>
  <div class="wrap foot-grid">
    <div>
      <p class="foot-brand">{star_svg(18)} {esc(site['name'])}</p>
      <p>{esc(site['footer_about'])}</p>
      <p>{esc(site['footer_data'])}</p>
      {updated}
      <p><a class="promo-link" href="{PROMO_URL}" rel="noopener">{esc(promo['footer'])}</a></p>
    </div>
    <ul class="foot-links">{nav}</ul>
    <ul class="foot-links foot-langs">{other_langs}</ul>
  </div>
  <div class="wrap foot-meta">
    <a href="{REPO_URL}" rel="noopener">{esc(site['footer_repo'])}</a>
    <a href="{REPO_URL}/issues/new" rel="noopener">{esc(site['footer_report'])}</a>
  </div>
</footer>
{suggest_payload(ctx, page)}
<script src="{BASE}/assets/app.js?v={ctx['asset_version']}" defer></script>
</body>
</html>
"""


def breadcrumb(ctx: dict, page: str) -> tuple[str, str]:
    """Return (visible breadcrumb html, BreadcrumbList JSON-LD)."""
    lang = ctx["lang"]
    site = lang["site"]
    home_url, here_url = page_url(lang, "home"), page_url(lang, page)
    html_out = (
        f'<nav class="crumbs" aria-label="{esc(site["breadcrumb"])}"><ol>'
        f'<li><a href="{esc(home_url)}">{esc(site["nav"]["home"])}</a></li>'
        f'<li aria-current="page">{esc(site["nav"][page])}</li></ol></nav>'
    )
    ld = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": site["nav"]["home"], "item": f"{ORIGIN}{home_url}"},
                {"@type": "ListItem", "position": 2, "name": site["nav"][page], "item": f"{ORIGIN}{here_url}"},
            ],
        }
    )
    return html_out, ld
