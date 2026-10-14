"""News/patch notes page and Steam player-count page."""

from __future__ import annotations

from datetime import timedelta

from blocks import page_intro, paras, section, source_rel, sources, top_peak
from news_util import news_entries
from site_lib import esc, fill, fmt_date, fmt_int, fmt_pct, fmt_time_utc, parse_time

CHART_W, CHART_H, PAD_L, PAD_B, PAD_T = 720, 260, 56, 28, 12
# Below this share of the reported peak, the page stops claiming the game is "not dead".
DEAD_THRESHOLD = 0.10


def render_news(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    lang = ctx["lang"]
    copy = lang["pages"]["news"]
    items = ""
    for n in news_entries(ctx):
        note = "" if n["translated"] else f'<p class="muted small">{esc(copy["untranslated"])}</p>'
        points = "".join(f"<li>{esc(p)}</li>" for p in n["points"])
        items += f"""<li class="post" id="n{esc(n['gid'])}">
  <time datetime="{esc(n['date'])}">{esc(fmt_date(n['date'], lang))}</time>
  <div><h3>{esc(n['title'])}</h3>{note}<ul class="ticks">{points}</ul>
  <p><a href="{esc(n['url'])}" rel="noopener">{esc(copy['read_original'])}</a></p></div>
</li>"""
    press = "".join(
        f'<li><a href="{esc(p["url"])}" rel="noopener">{esc(p["publisher"])}: {esc(p["title"])}</a> '
        f'<span class="muted">{esc(fmt_date(p["date"], lang))}</span><p>{esc(lang["press"][p["id"]])}</p></li>'
        for p in ctx["game"]["press"]
    )
    body = f"""{page_intro(ctx, 'news', crumbs)}
<div class="wrap">
  {section('official', copy['official_title'], f'<ol class="timeline">{items}</ol>')}
  <div class="cols">
    {section('viral', copy['viral_title'], paras(copy['viral']))}
    {section('press', copy['press_title'], f'<ul class="press">{press}</ul>')}
  </div>
  {section('roadmap', copy['roadmap_title'], f"<p>{esc(copy['roadmap'])}</p>")}
</div>
{sources(ctx, ['steam-news', 'dexerto', 'insider-gaming'])}"""
    return body, []


def history_points(ctx: dict) -> list[tuple]:
    return [(parse_time(t), int(c)) for t, c in ctx["history"]]


def peak_since(points: list[tuple], hours: int):
    if not points:
        return None
    cutoff = points[-1][0] - timedelta(hours=hours)
    window = [p for p in points if p[0] >= cutoff]
    return max(window, key=lambda p: p[1]) if window else None


def chart_svg(ctx: dict, points: list[tuple]) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["charts"]
    if len(points) < 2:
        return f'<p class="chart-empty">{esc(copy["chart_empty"])}</p>'
    t0, t1 = points[0][0].timestamp(), points[-1][0].timestamp()
    top = max(c for _, c in points) * 1.1 or 1
    plot_w, plot_h = CHART_W - PAD_L - 8, CHART_H - PAD_B - PAD_T

    def xy(t, c):
        x = PAD_L + (t.timestamp() - t0) / max(t1 - t0, 1) * plot_w
        y = PAD_T + plot_h - c / top * plot_h
        return f"{x:.1f},{y:.1f}"

    line = " ".join(xy(t, c) for t, c in points)
    area = f"{PAD_L},{PAD_T + plot_h} {line} {PAD_L + plot_w},{PAD_T + plot_h}"
    grid = ""
    for frac in (0, 0.5, 1):
        value = int(top / 1.1 * frac)
        y = PAD_T + plot_h - value / top * plot_h
        grid += (
            f'<line x1="{PAD_L}" x2="{PAD_L + plot_w}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
            f'<text x="{PAD_L - 8}" y="{y + 4:.1f}" class="axis" text-anchor="end">{fmt_int(value, lang)}</text>'
        )
    first, last = points[0][0].isoformat(), points[-1][0].isoformat()
    labels = (
        f'<text x="{PAD_L}" y="{CHART_H - 6}" class="axis">{esc(fmt_date(first, lang))}</text>'
        f'<text x="{PAD_L + plot_w}" y="{CHART_H - 6}" class="axis" text-anchor="end">{esc(fmt_date(last, lang))}</text>'
    )
    return (
        f'<figure class="chart"><svg viewBox="0 0 {CHART_W} {CHART_H}" role="img" aria-label="{esc(copy["chart_aria"])}">'
        f'{grid}<polygon points="{area}" class="area"/><polyline points="{line}" class="line"/>{labels}</svg></figure>'
    )


def daily_peaks(points: list[tuple]) -> list[tuple]:
    best: dict = {}
    for t, c in points:
        day = t.date().isoformat()
        best[day] = max(best.get(day, 0), c)
    return sorted(best.items(), reverse=True)[:14]


def stat(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<span class="stat-sub">{sub}</span>' if sub else ""
    return f'<div class="stat"><span class="stat-label">{esc(label)}</span><span class="stat-value">{value}</span>{sub_html}</div>'


def render_charts(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    lang, steam, game = ctx["lang"], ctx["steam"], ctx["game"]
    copy = lang["pages"]["charts"]
    points = history_points(ctx)
    players = steam.get("players")
    tiles = ""
    if players:
        when = f'<time datetime="{esc(players["at"])}">{esc(fill(copy["at"], time=fmt_time_utc(players["at"], lang)))}</time>'
        tiles += stat(copy["current"], f'<span class="dot" aria-hidden="true"></span>{fmt_int(players["count"], lang)}', when)
    span_hours = (points[-1][0] - points[0][0]).total_seconds() / 3600 if len(points) >= 2 else 0
    # Only show a tracked peak once the history actually covers that window.
    windows = ((copy["peak_24h"], 24, 24), (copy["peak_7d"], 24 * 7, 24 * 7), (copy["peak_tracked"], 24 * 3650, 24))
    for label, hours, needed in windows:
        peak = peak_since(points, hours) if span_hours >= needed else None
        if peak:
            tiles += stat(label, fmt_int(peak[1], lang), esc(fmt_time_utc(peak[0].isoformat(), lang)) + " UTC")
    top_reported = top_peak(ctx)
    if top_reported:
        tiles += stat(
            copy["reported_title"],
            fmt_int(top_reported["value"], lang),
            esc(f'{fmt_date(top_reported["date"], lang)}, {lang["sources"][top_reported["source"]]}'),
        )
    reviews = steam.get("reviews")
    if reviews and reviews.get("total"):
        pct = fmt_pct(round(100 * reviews["positive"] / reviews["total"]), lang)
        tiles += stat(copy["reviews"], esc(pct), esc(fill(copy["reviews_value"], pct=pct, total=fmt_int(reviews["total"], lang))))
    by_source = {s["id"]: s for s in game["sources"]}
    reported = "".join(
        f'<tr><td>{esc(fmt_date(r["date"], lang))}</td><td class="num">{fmt_int(r["value"], lang)}</td>'
        f'<td><a href="{esc(by_source[r["source"]]["url"])}" rel="{source_rel(by_source[r["source"]])}">{esc(lang["sources"][r["source"]])}</a>'
        f' <span class="muted">({esc(copy["reported_note"][r["note"]])})</span></td></tr>'
        for r in sorted(game["reported_peaks"], key=lambda r: r["value"], reverse=True)
    )
    reported_tbl = (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">{esc(copy["th_date"])}</th>'
        f'<th scope="col">{esc(copy["th_players"])}</th><th scope="col">{esc(copy["th_source"])}</th></tr></thead>'
        f"<tbody>{reported}</tbody></table></div>"
    )
    daily = "".join(
        f'<tr><td>{esc(fmt_date(day, lang))}</td><td class="num">{fmt_int(c, lang)}</td></tr>' for day, c in daily_peaks(points)
    )
    daily_tbl = (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">{esc(copy["th_date"])}</th>'
        f'<th scope="col">{esc(copy["th_players"])}</th></tr></thead><tbody>{daily}</tbody></table></div>'
    )
    more = (
        f'<p>{esc(copy["more_links"])} <a href="{esc(game["steamdb_url"])}" rel="noopener">{esc(copy["link_steamdb_hw2"])}</a>, '
        f'<a href="{esc(game["steamdb_hw1_url"])}" rel="noopener">{esc(copy["link_steamdb_hw1"])}</a>, '
        f'<a href="{esc(game["steamcharts_hw1_url"])}" rel="noopener">{esc(copy["link_steamcharts_hw1"])}</a></p>'
    )
    answers = qa_sections(ctx, players, reviews, top_reported)
    body = f"""{page_intro(ctx, 'charts', crumbs)}
<div class="wrap">
  <div class="stats">{tiles}</div>
  {answers}
  {section('chart', copy['chart_title'], chart_svg(ctx, points))}
  <div class="cols">
    {section('reported', copy['reported_title'], reported_tbl)}
    {section('daily', copy['daily_title'], daily_tbl)}
  </div>
  {section('method', copy['method_title'], paras(copy['method']) + more)}
</div>
{sources(ctx, ['steam-store', 'itad', 'steam-hw1', 'insider-gaming', 'hw2org-steamdb'])}"""
    return body, []


def qa_sections(ctx: dict, players, reviews, peak) -> str:
    """Direct answers for "how many people play" / "is it dead" / first-game confusion."""
    lang, steam, game = ctx["lang"], ctx["steam"], ctx["game"]
    copy = lang["pages"]["charts"]
    out = ""
    if players and peak:
        values = {
            "count": fmt_int(players["count"], lang),
            "time": fmt_time_utc(players["at"], lang),
            "peak": fmt_int(peak["value"], lang),
        }
        out += section("now", copy["answer_title"], f"<p>{esc(fill(copy['answer'], **values))}</p>")
        ratio = players["count"] / peak["value"]
        if reviews and reviews.get("total") and ratio >= DEAD_THRESHOLD:
            share = fmt_pct(round(100 * ratio), lang)
            positive = fmt_pct(round(100 * reviews["positive"] / reviews["total"]), lang)
            dead = fill(copy["dead"], count=values["count"], pct=share, reviews=positive)
            out += section("dead", copy["dead_title"], f"<p>{esc(dead)}</p>")
    hw1 = game["predecessor"]
    vs = f"<p>{esc(fill(copy['vs'], hw1_peak=fmt_int(hw1['reported_peak'], lang)))}</p>"
    hw1_now = steam.get("players_hw1")
    fresh = hw1_now and players and abs((parse_time(hw1_now["at"]) - parse_time(players["at"])).total_seconds()) < 6 * 3600
    if fresh:
        vs += f"<p>{esc(fill(copy['vs_now'], count=fmt_int(hw1_now['count'], lang)))}</p>"
    return out + section("vs-hw1", copy["vs_title"], vs)
