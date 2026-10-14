"""Merge live Steam announcements with the translated summaries in i18n."""

from __future__ import annotations

MAX_ORIGINAL_LINES = 4


def news_entries(ctx: dict) -> list[dict]:
    translated = ctx["lang"].get("news", {})
    entries = []
    for item in ctx["steam"].get("news", []):
        summary = translated.get(item["gid"])
        entries.append(
            {
                "gid": item["gid"],
                "date": item["date"],
                "url": item["url"],
                "title": summary["title"] if summary else item["title"],
                "points": summary["points"] if summary else item["lines"][:MAX_ORIGINAL_LINES],
                "translated": bool(summary),
            }
        )
    return entries
