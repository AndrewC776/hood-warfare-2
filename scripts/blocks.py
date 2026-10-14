"""Reusable HTML blocks shared by several pages."""

from __future__ import annotations

from site_lib import badge, esc, fill, fmt_date, page_url


def section(sid: str, title: str, body: str, cls: str = "") -> str:
    return (
        f'<section class="sec {cls}" id="{sid}" aria-labelledby="{sid}-h">'
        f'<h2 id="{sid}-h">{esc(title)}</h2>{body}</section>'
    )


def paras(items: list[str]) -> str:
    return "".join(f"<p>{text}</p>" for text in items)


def bullets(items: list[str], cls: str = "ticks") -> str:
    return f'<ul class="{cls}">' + "".join(f"<li>{text}</li>" for text in items) + "</ul>"


def page_intro(ctx: dict, page: str, crumbs: str, extra: str = "") -> str:
    copy = ctx["lang"]["pages"][page]
    return (
        f'<div class="intro wrap">{crumbs}<h1>{esc(copy["h1"])}</h1>'
        f'<p class="lede">{copy["lede"]}</p>{extra}</div>'
    )


def gloss(ctx: dict, group: str, item_id: str) -> str:
    text = ctx["lang"].get("gloss", {}).get(group, {}).get(item_id)
    return f'<span class="gloss">{esc(text)}</span>' if text else ""


def legend(ctx: dict) -> str:
    return f'<p class="legend">{ctx["lang"]["site"]["badge_legend"]}</p>'


def sources(ctx: dict, ids: list[str]) -> str:
    lang = ctx["lang"]
    by_id = {s["id"]: s for s in ctx["game"]["sources"]}
    items = "".join(
        f'<li><a href="{esc(by_id[i]["url"])}" rel="noopener">{esc(lang["sources"].get(i, by_id[i]["publisher"]))}</a>'
        f' <span class="muted">{esc(fmt_date(by_id[i]["date"], lang))}</span></li>'
        for i in ids
        if i in by_id
    )
    return (
        f'<aside class="sources wrap" aria-labelledby="src-h"><h2 id="src-h">{esc(lang["site"]["sources"])}</h2>'
        f"<ul>{items}</ul></aside>"
    )


def faq(ctx: dict, items: list[dict], values: dict) -> str:
    return '<div class="faq">' + "".join(
        f'<details><summary>{esc(item["q"])}</summary><div class="faq-a"><p>{fill(item["a"], **values)}</p></div></details>'
        for item in items
    ) + "</div>"


def faq_ld(items: list[dict], values: dict) -> dict:
    import re

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", fill(item["a"], **values))},
            }
            for item in items
        ],
    }


def local_prices(ctx: dict) -> list[tuple[str, dict]]:
    prices = ctx["steam"].get("prices", {})
    wanted = [cc for cc in ctx["lang"]["meta"]["price_cc"] if cc in prices]
    if "us" not in wanted and "us" in prices:
        wanted.append("us")
    return [(cc, prices[cc]) for cc in wanted]


def regular_price(ctx: dict) -> str:
    found = local_prices(ctx)
    return found[0][1]["initial"] if found else "$5.99"


def common_values(ctx: dict) -> dict:
    lang = ctx["lang"]
    return {
        "download": page_url(lang, "download"),
        "charts": page_url(lang, "charts"),
        "steam": ctx["game"]["steam_url"],
        "version": ctx["game"]["facts"]["latest_version"],
        "today": fmt_date(ctx["today_iso"], lang),
        "price": esc(regular_price(ctx)),
    }


def conf_cell(ctx: dict, conf: str) -> str:
    return f"<td>{badge(conf, ctx['lang'])}</td>"


def buy_button(ctx: dict, cls: str = "btn btn-buy") -> str:
    return (
        f'<a class="{cls}" href="{esc(ctx["game"]["steam_url"])}" rel="noopener">'
        f'{esc(ctx["lang"]["site"]["buy"])}</a>'
    )
