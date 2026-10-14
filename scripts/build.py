"""Build the multilingual static site into _site/.

Usage: python3 scripts/build.py
Env: SITE_ORIGIN, SITE_BASE, SITE_OUT (see site_lib.py).
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import datetime, timezone

from layout import breadcrumb, footer, head, header
from pages_data import render_charts, render_news
from pages_guides import render_guide, render_maps, render_modes, render_weapons
from pages_home import render_download, render_home
from site_lib import BASE, DATA, I18N, ORIGIN, OUT, PAGES, ROOT, esc, load_json, load_langs, page_url

RENDERERS = {
    "download": render_download,
    "weapons": render_weapons,
    "maps": render_maps,
    "modes": render_modes,
    "guide": render_guide,
    "news": render_news,
    "charts": render_charts,
}


def asset_version() -> str:
    digest = hashlib.sha256()
    for path in sorted((ROOT / "assets").glob("*")):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


def render_page(ctx: dict, page: str) -> str:
    if page == "home":
        body, ld = render_home(ctx)
    else:
        crumbs, crumb_ld = breadcrumb(ctx, page)
        body, ld = RENDERERS[page](ctx, crumbs)
        ld = [crumb_ld, *ld]
    return f'{head(ctx, page, ld)}\n{header(ctx, page)}\n<main id="main">\n{body}\n</main>\n{footer(ctx, page)}'


def write(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sitemap(langs: dict, lastmod: str) -> str:
    urls = []
    for page, _ in PAGES:
        alternates = "".join(
            f'<xhtml:link rel="alternate" hreflang="{l["meta"]["hreflang"]}" href="{page_url(l, page, True)}"/>'
            for l in langs.values()
        )
        alternates += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url(langs["en"], page, True)}"/>'
        for lang in langs.values():
            urls.append(
                f"<url><loc>{page_url(lang, page, True)}</loc><lastmod>{lastmod}</lastmod>{alternates}</url>"
            )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def not_found(ctx: dict) -> str:
    lang = ctx["lang"]
    site = lang["site"]
    body = (
        f'<div class="intro wrap"><h1>{esc(site["not_found_title"])}</h1><p class="lede">{esc(site["not_found_body"])}</p>'
        f'<p><a class="btn btn-ghost" href="{esc(page_url(lang, "home"))}">{esc(site["not_found_home"])}</a></p></div>'
    )
    page_html = f'{head(ctx, "home", [])}\n{header(ctx, "home")}\n<main id="main">{body}</main>\n{footer(ctx, "home")}'
    return page_html.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)


def main() -> int:
    langs = load_langs()
    if "en" not in langs:
        print("error: i18n/en.json missing", file=sys.stderr)
        return 1
    game = load_json(DATA / "game.json")
    steam = load_json(DATA / "steam.json", {})
    history = load_json(DATA / "history.json", [])
    promo = load_json(I18N / "promo.json", {})
    details = steam.get("details") or {}
    shots = [s for s in details.get("screenshots") or [] if s.get("full")]
    og_image = shots[0]["full"] if shots else (details.get("header") or "")
    today = datetime.now(timezone.utc).date().isoformat()

    if OUT == ROOT or ROOT not in OUT.parents:
        print(f"error: refusing to build into {OUT}", file=sys.stderr)
        return 1
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    version = asset_version()

    count = 0
    for code, lang in langs.items():
        ctx = {
            "lang": lang,
            "langs": langs,
            "game": game,
            "steam": steam,
            "history": history,
            "promo": promo.get(code) or promo["en"],
            "og_image": og_image,
            "asset_version": version,
            "today_iso": today,
        }
        for page, slug in PAGES:
            prefix = lang["meta"]["path"]
            target = OUT / prefix / slug / "index.html" if prefix else OUT / slug / "index.html"
            write(target, render_page(ctx, page))
            count += 1
        if code == "en":
            write(OUT / "404.html", not_found(ctx))

    write(OUT / "sitemap.xml", sitemap(langs, today))
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}{BASE}/sitemap.xml\n")
    write(OUT / ".nojekyll", "")
    print(f"built {count} pages in {len(langs)} languages -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
