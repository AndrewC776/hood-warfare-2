"""Home page and download/price page."""

from __future__ import annotations

from blocks import (
    buy_button,
    bullets,
    common_values,
    faq,
    faq_ld,
    gloss,
    local_prices,
    page_intro,
    paras,
    section,
    sources,
)
from news_util import news_entries
from site_lib import (
    ORIGIN,
    PROMO_URL,
    badge,
    esc,
    fill,
    fmt_date,
    fmt_int,
    fmt_pct,
    json_ld,
    page_url,
    star_path,
)


def live_line(ctx: dict) -> str:
    lang, steam, game = ctx["lang"], ctx["steam"], ctx["game"]
    copy = lang["pages"]["home"]
    parts = []
    players = steam.get("players")
    if players:
        parts.append(
            f'<li><span class="dot" aria-hidden="true"></span><strong>{fmt_int(players["count"], lang)}</strong> '
            f'{esc(lang["site"]["players_now"])}</li>'
        )
    reviews = steam.get("reviews")
    if reviews:
        pct = round(100 * reviews["positive"] / reviews["total"])
        parts.append(
            f'<li><strong>{fmt_pct(pct, lang)}</strong> '
            f'{esc(fill(copy["reviews_label"], total=fmt_int(reviews["total"], lang)))}</li>'
        )
    parts.append(
        f'<li><strong>{esc(fmt_date(game["release_date"], lang))}</strong> {esc(copy["release_label"])}</li>'
    )
    return f'<ul class="live">{"".join(parts)}</ul>'


def hero(ctx: dict) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["home"]
    shots = (ctx["steam"].get("details") or {}).get("screenshots") or []
    art = (
        f'<img class="hero-art" src="{esc(shots[0]["full"])}" alt="" width="1920" height="1080" fetchpriority="high">'
        if shots
        else ""
    )
    return f"""<section class="hero">
  {art}
  <div class="wrap hero-in">
    <h1 class="hero-title">{esc(copy['h1'])}</h1>
    <p class="lede">{esc(copy['lede'])}</p>
    <div class="cta-row">{buy_button(ctx)}<a class="btn btn-ghost" href="{esc(page_url(lang, 'guide'))}">{esc(copy['cta_guide'])}</a></div>
    {live_line(ctx)}
  </div>
</section>"""


def flag_band(ctx: dict) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["home"]
    stars = "".join(
        f"""<li class="flag-star">
  <svg viewBox="0 0 100 100" aria-hidden="true"><path d="{star_path(50, 50, 48)}"/></svg>
  <span class="flag-kills">{esc(fill(copy['streak_kills'], n=k['kills']))}</span>
  <span class="flag-name">{esc(k['name'])}</span>{gloss(ctx, 'killstreaks', k['id'])}
</li>"""
        for k in ctx["game"]["killstreaks"]
    )
    return f"""<section class="flag" aria-labelledby="streaks-h">
  <div class="flag-stripe" aria-hidden="true"></div>
  <div class="flag-white">
    <div class="wrap">
      <h2 id="streaks-h" class="flag-title">{esc(copy['streaks_title'])} {badge('community', lang)}</h2>
      <ol class="flag-stars">{stars}</ol>
      <p class="flag-note">{esc(copy['streaks_note'])} <a href="{esc(page_url(lang, 'weapons'))}#streaks">{esc(lang['site']['nav']['weapons'])}</a></p>
    </div>
  </div>
  <div class="flag-stripe" aria-hidden="true"></div>
</section>"""


def quick_facts(ctx: dict) -> str:
    lang, game = ctx["lang"], ctx["game"]
    f = lang["pages"]["home"]["facts"]
    prices = local_prices(ctx)
    price = " / ".join(f'{esc(p["final"])}' for _, p in prices[:2]) or "-"
    rows = [
        (f["release"], esc(fmt_date(game["release_date"], lang))),
        (f["developer"], esc(game["developer"])),
        (f["platform"], esc(f["platform_value"])),
        (f["price"], f'{price} <a href="{esc(page_url(lang, "download"))}">{esc(lang["site"]["nav"]["download"])}</a>'),
        (f["engine"], esc(game["engine"])),
        (f["content"], esc(f["content_value"])),
        (f["anti_cheat"], esc(game["facts"]["anti_cheat"])),
        (f["languages"], esc(f["languages_value"])),
        (f["version"], f'<a href="{esc(page_url(lang, "news"))}">{esc(game["facts"]["latest_version"])}</a>'),
    ]
    body = "".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f'<dl class="facts">{body}</dl>'


def guide_index(ctx: dict) -> str:
    lang = ctx["lang"]
    blurbs = lang["pages"]["home"]["sections"]
    items = "".join(
        f'<li><a href="{esc(page_url(lang, p))}"><span class="gi-title">{esc(lang["site"]["nav"][p])}</span>'
        f'<span class="gi-text">{esc(blurbs[p])}</span></a></li>'
        for p in ["download", "weapons", "maps", "modes", "guide", "news", "charts"]
    )
    return f'<ul class="guide-index">{items}</ul>'


def latest_news(ctx: dict) -> str:
    lang = ctx["lang"]
    items = "".join(
        f'<li><time datetime="{esc(n["date"])}">{esc(fmt_date(n["date"], lang))}</time>'
        f'<a href="{esc(page_url(lang, "news"))}#n{esc(n["gid"])}">{esc(n["title"])}</a></li>'
        for n in news_entries(ctx)[:3]
    )
    more = f'<p><a href="{esc(page_url(lang, "news"))}">{esc(lang["pages"]["home"]["news_all"])}</a></p>'
    return f'<ol class="news-mini">{items}</ol>{more}'


def media(ctx: dict) -> str:
    copy = ctx["lang"]["pages"]["home"]
    details = ctx["steam"].get("details") or {}
    trailer = details.get("trailer")
    player = ""
    if trailer and trailer.get("hls"):
        player = (
            f'<div class="trailer" data-hls="{esc(trailer["hls"])}">'
            f'<img src="{esc(trailer["poster"])}" alt="" width="600" height="337" loading="lazy">'
            f'<button type="button" class="play"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>'
            f'<span>{esc(copy["trailer_play"])}</span></button></div>'
            f'<p class="muted small">{esc(copy["trailer_note"])}</p>'
        )
    shots = "".join(
        f'<li><a href="{esc(s["full"])}" rel="noopener"><img src="{esc(s["thumb"])}" alt="Hood Warfare 2 screenshot {i + 1}" '
        f'width="600" height="338" loading="lazy"></a></li>'
        for i, s in enumerate((details.get("screenshots") or [])[1:9])
    )
    return f'{player}<ul class="shots">{shots}</ul>'


def promo(ctx: dict) -> str:
    p = ctx["promo"]
    return (
        f'<aside class="promo wrap" aria-labelledby="promo-h"><div class="promo-in">'
        f'<h2 id="promo-h">{esc(p["title"])}</h2><p>{esc(p["body"])}</p>'
        f'<a class="btn btn-ghost" href="{PROMO_URL}" rel="noopener">{esc(p["cta"])}</a></div></aside>'
    )


def video_game_ld(ctx: dict) -> str:
    lang, game, steam = ctx["lang"], ctx["game"], ctx["steam"]
    us = steam.get("prices", {}).get("us")
    data = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game["name"],
        "url": game["steam_url"],
        "description": lang["pages"]["home"]["description"],
        "image": ctx["og_image"],
        "genre": ["First-person shooter", "Action"],
        "gamePlatform": "PC",
        "operatingSystem": "Windows",
        "applicationCategory": "Game",
        "playMode": ["MultiPlayer", "SinglePlayer"],
        "datePublished": game["release_date"],
        "author": {"@type": "Organization", "name": game["developer"]},
        "publisher": {"@type": "Organization", "name": game["publisher"]},
        "inLanguage": "en",
    }
    if us:
        data["offers"] = {
            "@type": "Offer",
            "price": us["final"].replace("$", ""),
            "priceCurrency": "USD",
            "url": game["steam_url"],
            "availability": "https://schema.org/InStock",
        }
    site = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": lang["site"]["name"],
        "url": f"{ORIGIN}{page_url(lang, 'home')}",
        "inLanguage": lang["meta"]["html_lang"],
    }
    return json_ld(data) + json_ld(site)


def render_home(ctx: dict) -> tuple[str, list[str]]:
    lang = ctx["lang"]
    copy = lang["pages"]["home"]
    values = common_values(ctx)
    body = f"""{hero(ctx)}
{flag_band(ctx)}
<div class="wrap cols">
  {section('what', copy['what_title'], paras(copy['what']))}
  {section('facts', copy['facts_title'], quick_facts(ctx))}
</div>
<div class="wrap">
  {section('guides', copy['sections_title'], guide_index(ctx))}
  <div class="cols">
    {section('latest', copy['news_title'], latest_news(ctx))}
    {section('media', copy['media_title'], media(ctx))}
  </div>
</div>
{promo(ctx)}
<div class="wrap narrow">{section('faq', copy['faq_title'], faq(ctx, copy['faq'], values))}</div>
{sources(ctx, ['steam-store', 'steam-news', 'dexerto', 'insider-gaming', 'hw2org-steamdb'])}"""
    return body, [video_game_ld(ctx), json_ld(faq_ld(copy["faq"], values))]


def price_table(ctx: dict) -> str:
    copy = ctx["lang"]["pages"]["download"]
    rows = "".join(
        f'<tr><th scope="row">{esc(p["currency"])}</th><td>{esc(p["initial"])}</td>'
        f'<td><strong>{esc(p["final"])}</strong>'
        + (f' <span class="tag">{esc(fill(copy["price_discount"], n=p["discount"]))}</span>' if p["discount"] else "")
        + "</td></tr>"
        for _, p in local_prices(ctx)
    )
    return (
        f'<table class="tbl price"><thead><tr><th scope="col"></th><th scope="col">{esc(copy["price_regular"])}</th>'
        f'<th scope="col">{esc(copy["price_now"])}</th></tr></thead><tbody>{rows}</tbody></table>'
        f'<p class="muted small">{esc(copy["price_note"])}</p><p>{buy_button(ctx)}</p>'
    )


def req_table(ctx: dict) -> str:
    copy = ctx["lang"]["pages"]["download"]
    req = ctx["game"]["sysreq"]
    rows = "".join(
        f'<tr><th scope="row">{esc(label)}</th><td>{esc(req["min"][key])}</td><td>{esc(req["rec"][key])}</td></tr>'
        for key, label in copy["req_rows"].items()
    )
    return (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col"></th><th scope="col">{esc(copy["req_min"])}</th>'
        f'<th scope="col">{esc(copy["req_rec"])}</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p class="muted small">{esc(copy["req_note"])} {badge("official", ctx["lang"])}</p>'
    )


def platforms(ctx: dict) -> str:
    rows = "".join(
        f'<tr><th scope="row">{esc(p["k"])}</th><td>{esc(p["v"])}</td><td>{badge(p["conf"], ctx["lang"])}</td></tr>'
        for p in ctx["lang"]["pages"]["download"]["platforms"]
    )
    return f'<div class="tbl-wrap"><table class="tbl"><tbody>{rows}</tbody></table></div>'


def render_download(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    copy = ctx["lang"]["pages"]["download"]
    values = common_values(ctx)
    steps = "<ol class=\"steps\">" + "".join(f"<li>{fill(s, **values)}</li>" for s in copy["steps"]) + "</ol>"
    body = f"""{page_intro(ctx, 'download', crumbs)}
<div class="wrap cols">
  {section('price', copy['price_title'], price_table(ctx))}
  {section('steps', copy['steps_title'], steps)}
</div>
<div class="wrap">
  {section('safety', copy['safety_title'], paras(copy['safety']), 'callout')}
  {section('requirements', copy['req_title'], req_table(ctx))}
  {section('platforms', copy['platforms_title'], platforms(ctx))}
  {section('regional', copy['regional_title'], bullets(copy['regional']))}
</div>
{promo(ctx)}
<div class="wrap narrow">{section('faq', copy['faq_title'], faq(ctx, copy['faq'], values))}</div>
{sources(ctx, ['steam-store', 'steam-news'])}"""
    return body, [json_ld(faq_ld(copy["faq"], values))]
