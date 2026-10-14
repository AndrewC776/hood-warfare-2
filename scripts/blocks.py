"""Reusable HTML blocks shared by several pages."""

from __future__ import annotations

from site_lib import badge, esc, fill, fmt_date, fmt_int, page_url


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
    lede = fill(copy["lede"], **common_values(ctx))
    return (
        f'<div class="intro wrap">{crumbs}<h1>{esc(copy["h1"])}</h1>'
        f'<p class="lede">{lede}</p>{extra}</div>'
    )


def gloss(ctx: dict, group: str, item_id: str) -> str:
    text = ctx["lang"].get("gloss", {}).get(group, {}).get(item_id)
    return f'<span class="gloss">{esc(text)}</span>' if text else ""


def legend(ctx: dict) -> str:
    return f'<p class="legend">{ctx["lang"]["site"]["badge_legend"]}</p>'


def status_line(ctx: dict, default: str) -> str:
    """One line stating the default confidence, so rows only badge the exceptions."""
    text = fill(ctx["lang"]["site"]["status_default"], badge=badge(default, ctx["lang"]))
    return f'<p class="legend">{text}</p>'


def exception_badge(ctx: dict, conf: str, default: str) -> str:
    return f" {badge(conf, ctx['lang'])}" if conf != default else ""


def source_rel(source: dict) -> str:
    return "nofollow noopener" if source.get("nofollow") else "noopener"


def sources(ctx: dict, ids: list[str]) -> str:
    lang = ctx["lang"]
    by_id = {s["id"]: s for s in ctx["game"]["sources"]}
    listed = [by_id[i] for i in ids if i in by_id]
    items = "".join(
        f'<li><a href="{esc(s["url"])}" rel="{source_rel(s)}">{esc(lang["sources"].get(s["id"], s["publisher"]))}</a></li>'
        for s in listed
    )
    checked = max((s["date"] for s in listed), default=ctx["today_iso"])
    heading = fill(lang["site"]["sources_checked"], date=fmt_date(checked, lang))
    return (
        f'<aside class="sources wrap" aria-labelledby="src-h"><h2 id="src-h">{esc(heading)}</h2>'
        f"<ul>{items}</ul></aside>"
    )


def answerable(items: list[dict], values: dict) -> list[dict]:
    """Drop FAQ items whose answer needs a value we don't have (e.g. no reported peak)."""
    return [i for i in items if not ("{peak}" in i["a"] and values.get("peak") in (None, "-"))]


def faq(ctx: dict, items: list[dict], values: dict) -> str:
    items = answerable(items, values)
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
            for item in answerable(items, values)
        ],
    }


def local_prices(ctx: dict) -> list[tuple[str, dict]]:
    prices = ctx["steam"].get("prices", {})
    wanted = [cc for cc in ctx["lang"]["meta"]["price_cc"] if cc in prices]
    if "us" not in wanted and "us" in prices:
        wanted.append("us")
    return [(cc, prices[cc]) for cc in wanted]


def price_full(ctx: dict) -> str:
    """Regular price plus the current discount, e.g. "$5.99 ($5.39 with the current 10% discount)"."""
    found = local_prices(ctx)
    if not found:
        return "$5.99"
    price = found[0][1]
    if not price.get("discount"):
        return price["initial"]
    return fill(ctx["lang"]["site"]["price_with_discount"], regular=price["initial"], final=price["final"], n=price["discount"])


def top_peak(ctx: dict) -> dict | None:
    return max(ctx["game"]["reported_peaks"], key=lambda r: r["value"], default=None)


def common_values(ctx: dict) -> dict:
    lang = ctx["lang"]
    return {
        "download": page_url(lang, "download"),
        "charts": page_url(lang, "charts"),
        "steam": ctx["game"]["steam_url"],
        "version": ctx["game"]["facts"]["latest_version"],
        "today": fmt_date(ctx["today_iso"], lang),
        "price": esc(price_full(ctx)),
        "peak": fmt_int((top_peak(ctx) or {}).get("value"), lang),
        "hw1_url": ctx["game"]["predecessor"]["store_url"],
    }


def buy_button(ctx: dict, cls: str = "btn btn-buy") -> str:
    return (
        f'<a class="{cls}" href="{esc(ctx["game"]["steam_url"])}" rel="noopener">'
        f'{esc(ctx["lang"]["site"]["buy"])}</a>'
    )
