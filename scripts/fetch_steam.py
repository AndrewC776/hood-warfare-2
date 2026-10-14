"""Refresh live Steam data for the site.

Writes data/steam.json (latest snapshot) and appends to data/history.json.
Every request is independent: if one endpoint fails, the previous value for
that field is kept so a flaky Steam API never breaks the build.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
APP_ID = json.loads((DATA / "game.json").read_text())["app_id"]
PRICE_REGIONS = ["us", "gb", "cn", "tw", "hk", "jp", "kr", "es", "mx", "br", "ru", "de", "fr"]
HISTORY_CAP = 4000
UA = "hw2-guide-bot/1.0 (+https://github.com/AndrewC776/hood-warfare-2)"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_json(url: str, retries: int = 2) -> dict | None:
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - log and keep previous data
            print(f"warn: {url} attempt {attempt + 1}: {exc}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return None


def load(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def fetch_players() -> dict | None:
    data = get_json(
        f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={APP_ID}"
    )
    resp = (data or {}).get("response", {})
    if resp.get("result") != 1:
        return None
    return {"count": int(resp["player_count"]), "at": now_iso()}


def fetch_reviews() -> dict | None:
    data = get_json(
        f"https://store.steampowered.com/appreviews/{APP_ID}"
        "?json=1&language=all&purchase_type=all&num_per_page=0"
    )
    summary = (data or {}).get("query_summary")
    if not summary or not summary.get("total_reviews"):
        return None
    return {
        "total": summary["total_reviews"],
        "positive": summary["total_positive"],
        "negative": summary["total_negative"],
        "score": summary.get("review_score"),
        "desc": summary.get("review_score_desc"),
        "at": now_iso(),
    }


def fetch_details() -> dict | None:
    data = get_json(f"https://store.steampowered.com/api/appdetails?appids={APP_ID}&l=english")
    entry = (data or {}).get(str(APP_ID), {})
    if not entry.get("success"):
        return None
    d = entry["data"]
    movie = next(iter(d.get("movies") or []), None)
    return {
        "header": d.get("header_image"),
        "screenshots": [
            {"thumb": s.get("path_thumbnail"), "full": s.get("path_full")}
            for s in d.get("screenshots", [])
        ],
        "trailer": None
        if not movie
        else {
            "name": movie.get("name"),
            "poster": movie.get("thumbnail"),
            "hls": movie.get("hls_h264"),
        },
        "release": (d.get("release_date") or {}).get("date"),
    }


def fetch_prices() -> dict:
    prices = {}
    for cc in PRICE_REGIONS:
        data = get_json(
            f"https://store.steampowered.com/api/appdetails?appids={APP_ID}&cc={cc}&filters=price_overview"
        )
        entry = (data or {}).get(str(APP_ID), {})
        overview = entry.get("data", {}).get("price_overview") if isinstance(entry.get("data"), dict) else None
        if entry.get("success") and overview:
            prices[cc] = {
                "currency": overview["currency"],
                "initial": overview["initial_formatted"] or overview["final_formatted"],
                "final": overview["final_formatted"],
                "discount": overview["discount_percent"],
            }
        time.sleep(0.4)
    return prices


BB_TAG = re.compile(r"\[/?[a-z0-9*]+(=[^\]]*)?\]", re.I)


def bbcode_lines(text: str) -> list[str]:
    text = re.sub(r"\[/p\]|\[br\]|\n", "\n", text, flags=re.I)
    text = BB_TAG.sub("", text)
    lines = [ln.strip().lstrip("•").strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]


def fetch_news() -> list | None:
    data = get_json(
        "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
        f"?appid={APP_ID}&count=30&feeds=steam_community_announcements"
    )
    items = (data or {}).get("appnews", {}).get("newsitems")
    if items is None:
        return None
    return [
        {
            "gid": str(n["gid"]),
            "title": n["title"].strip(),
            "date": datetime.fromtimestamp(n["date"], timezone.utc).replace(microsecond=0).isoformat(),
            "url": f"https://store.steampowered.com/news/app/{APP_ID}/view/{n['gid']}",
            "lines": bbcode_lines(n.get("contents", "")),
        }
        for n in items
    ]


def safe(fetcher):
    """Run one fetcher; a malformed response must not abort the whole refresh."""
    try:
        return fetcher()
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        print(f"warn: {fetcher.__name__} failed: {exc!r}", file=sys.stderr)
        return None


def main() -> int:
    previous = load(DATA / "steam.json", {})
    players = safe(fetch_players)
    snapshot = {
        "fetched_at": now_iso(),
        "players": players or previous.get("players"),
        "reviews": safe(fetch_reviews) or previous.get("reviews"),
        "details": safe(fetch_details) or previous.get("details"),
        "prices": {**previous.get("prices", {}), **(safe(fetch_prices) or {})},
        "news": safe(fetch_news) or previous.get("news", []),
    }
    (DATA / "steam.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=1) + "\n")

    history = load(DATA / "history.json", [])
    if players and (not history or history[-1][0] != players["at"]):
        history = [*history, [players["at"], players["count"]]][-HISTORY_CAP:]
        (DATA / "history.json").write_text(json.dumps(history, separators=(",", ":")) + "\n")

    ok = {k: bool(snapshot[k]) for k in ("players", "reviews", "details", "prices", "news")}
    print(f"steam snapshot {snapshot['fetched_at']} {ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
