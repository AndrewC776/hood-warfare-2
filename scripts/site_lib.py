"""Shared helpers for the static site build: config, i18n, formatting, URLs."""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
I18N = ROOT / "i18n"
OUT = ROOT / os.environ.get("SITE_OUT", "_site")
ORIGIN = os.environ.get("SITE_ORIGIN", "https://andrewc776.github.io").rstrip("/")
BASE = os.environ.get("SITE_BASE", "/hood-warfare-2").rstrip("/")
REPO_URL = "https://github.com/AndrewC776/hood-warfare-2"
PROMO_URL = "https://wasmarcade.net/"

LANG_ORDER = ["en", "zh", "zh-tw", "ja", "ko", "es", "pt-br", "ru", "de", "fr"]
PAGES = [
    ("home", ""),
    ("download", "download/"),
    ("weapons", "weapons/"),
    ("maps", "maps/"),
    ("modes", "modes/"),
    ("guide", "guide/"),
    ("news", "news/"),
    ("charts", "steam-charts/"),
]
PAGE_SLUG = dict(PAGES)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def deep_merge(base, override):
    """Return base with override applied; lists only replace when lengths match."""
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            merged[key] = deep_merge(base[key], value) if key in base else value
        return merged
    if isinstance(base, list):
        return override if isinstance(override, list) and len(override) == len(base) else base
    if isinstance(override, str) and not override.strip():
        return base
    return override


def load_langs() -> dict:
    english = load_json(I18N / "en.json")
    langs = {}
    for code in LANG_ORDER:
        raw = english if code == "en" else load_json(I18N / f"{code}.json")
        if raw is None:
            continue
        merged = deep_merge(english, raw)
        merged["meta"] = {**english["meta"], **raw.get("meta", {})}
        merged["gloss"] = raw.get("gloss", {})
        langs[code] = merged
    return langs


def fill(text: str, **values) -> str:
    """Replace {key} placeholders without touching other braces."""
    for key, value in values.items():
        text = text.replace("{" + key + "}", str(value))
    return text


def page_url(lang: dict, page: str, absolute: bool = False) -> str:
    prefix = f"/{lang['meta']['path']}" if lang["meta"]["path"] else ""
    path = f"{BASE}{prefix}/{PAGE_SLUG[page]}"
    return f"{ORIGIN}{path}" if absolute else path


def fmt_int(n, lang: dict) -> str:
    if n is None:
        return "-"
    return f"{int(n):,}".replace(",", lang["meta"]["thousands_sep"])


def fmt_pct(n, lang: dict) -> str:
    return fill(lang["meta"]["percent_format"], n=n)


def parse_time(iso: str) -> datetime:
    value = datetime.fromisoformat(iso)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def fmt_date(iso: str, lang: dict) -> str:
    when = parse_time(iso) if "T" in iso else datetime.fromisoformat(iso)
    meta = lang["meta"]
    return fill(meta["date_format"], y=when.year, mon=meta["months"][when.month - 1], d=when.day)


def fmt_time_utc(iso: str, lang: dict) -> str:
    when = parse_time(iso).astimezone(timezone.utc)
    return f"{fmt_date(iso, lang)} {when:%H:%M}"


def star_path(cx: float, cy: float, outer: float, inner_ratio: float = 0.42) -> str:
    """Six-pointed star like the ones on the Chicago flag."""
    import math

    points = []
    for i in range(12):
        radius = outer if i % 2 == 0 else outer * inner_ratio
        angle = math.radians(-90 + i * 30)
        points.append(f"{cx + radius * math.cos(angle):.2f},{cy + radius * math.sin(angle):.2f}")
    return "M" + " L".join(points) + " Z"


def star_svg(size: int = 24, cls: str = "star") -> str:
    return (
        f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true">'
        f'<path d="{star_path(12, 12, 11.5)}"/></svg>'
    )


def badge(conf: str, lang: dict) -> str:
    return f'<span class="badge b-{esc(conf)}">{esc(lang["site"]["badges"][conf])}</span>'


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def json_ld(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{payload}</script>'
