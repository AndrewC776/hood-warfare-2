"""Weapons, maps, modes and beginner guide pages."""

from __future__ import annotations

from blocks import bullets, exception_badge, gloss, legend, page_intro, paras, section, sources, status_line
from site_lib import badge, esc, fill, page_url


def unlock_label(ctx: dict, level) -> str:
    site = ctx["lang"]["site"]
    if level is None:
        return esc(site["unknown"])
    return esc(site["start"]) if level == 0 else esc(fill(site["level"], n=level))


def primary_table(ctx: dict) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["weapons"]
    rows = "".join(
        f'<tr><th scope="row">{esc(w["name"])}{exception_badge(ctx, w["conf"], "community")}</th>'
        f'<td>{esc(lang["classes"][w["class"]])}</td>'
        f'<td class="num">{unlock_label(ctx, w["unlock"])}</td><td>{lang["weapons"][w["id"]]}</td></tr>'
        for w in ctx["game"]["weapons"]["primary"]
    )
    head = "".join(f'<th scope="col">{esc(copy[k])}</th>' for k in ("th_weapon", "th_class", "th_unlock", "th_notes"))
    return (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
        f'{status_line(ctx, "community")}<p class="muted small">{esc(copy["unlock_note"])}</p>'
    )


def other_table(ctx: dict) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["weapons"]
    rows = "".join(
        f'<tr><th scope="row">{esc(w["name"])}{exception_badge(ctx, w["conf"], "community")}</th>'
        f'<td>{esc(lang["slots"][w["slot"]])}</td>'
        f'<td class="num">{unlock_label(ctx, w["unlock"])}</td><td>{lang["weapons"][w["id"]]}</td></tr>'
        for w in ctx["game"]["weapons"]["other"]
    )
    head = "".join(f'<th scope="col">{esc(copy[k])}</th>' for k in ("th_weapon", "th_slot", "th_unlock", "th_notes"))
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def passives_list(ctx: dict) -> str:
    lang = ctx["lang"]
    items = "".join(
        f'<div><dt>{esc(p["name"])}{exception_badge(ctx, p["conf"], "community")}</dt><dd>{esc(lang["passives"][p["id"]])}</dd></div>'
        for p in ctx["game"]["passives"]
    )
    return f'<dl class="defs">{items}</dl>'


def streak_table(ctx: dict) -> str:
    lang = ctx["lang"]
    copy = lang["pages"]["weapons"]
    rows = "".join(
        f'<tr><th scope="row">{esc(k["name"])}{gloss(ctx, "killstreaks", k["id"])}</th><td class="num">{k["kills"]}</td>'
        f'<td>{esc(lang["killstreaks"][k["id"]]["effect"])}</td><td>{esc(lang["killstreaks"][k["id"]]["counter"])}</td></tr>'
        for k in ctx["game"]["killstreaks"]
    )
    head = "".join(f'<th scope="col">{esc(copy[k])}</th>' for k in ("th_weapon", "th_kills", "th_effect"))
    head += f'<th scope="col">{esc(copy["streak_counter"])}</th>'
    return (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
        f'{status_line(ctx, "community")}'
    )


def loadouts(ctx: dict) -> str:
    copy = ctx["lang"]["pages"]["weapons"]
    items = "".join(
        f'<div class="loadout"><h3>{esc(l["name"])}</h3><p class="kit">{esc(l["kit"])}</p><p>{esc(l["why"])}</p></div>'
        for l in copy["loadouts"]
    )
    return f'<p class="muted small">{esc(copy["loadouts_note"])}</p><div class="loadouts">{items}</div>'


def render_weapons(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    copy = ctx["lang"]["pages"]["weapons"]
    chips = "".join(f"<li>{esc(a)}</li>" for a in ctx["game"]["attachments_seen"])
    body = f"""{page_intro(ctx, 'weapons', crumbs, legend(ctx))}
<div class="wrap">
  {section('primary', copy['primary_title'], primary_table(ctx))}
  {section('other', copy['other_title'], other_table(ctx))}
  {section('streaks', copy['streaks_title'], streak_table(ctx))}
  {section('loadouts', copy['loadouts_title'], loadouts(ctx))}
  <div class="cols">
    {section('attachments', copy['attach_title'], paras(copy['attach']) + f'<ul class="chips">{chips}</ul>')}
    {section('passives', copy['passives_title'], passives_list(ctx))}
  </div>
  {section('skins', copy['skins_title'], paras(copy['skins']))}
</div>
{sources(ctx, ['steam-store', 'hw2org', 'tpose', 'gamerblurb', 'dexerto'])}"""
    return body, []


def render_maps(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    lang = ctx["lang"]
    copy = lang["pages"]["maps"]
    blocks = "".join(
        f"""<article class="map" id="{m['id']}" aria-labelledby="{m['id']}-h">
  <h2 id="{m['id']}-h">{esc(m['name'])}{gloss(ctx, 'maps', m['id'])}</h2>
  <p class="map-meta"><span class="tag">{esc(lang['ranges'][m['range']])}</span>{exception_badge(ctx, m['conf'], 'official')}</p>
  <p>{esc(lang['maps'][m['id']]['desc'])}</p>
  <dl class="defs compact"><div><dt>{esc(copy['best_for'])}</dt><dd>{esc(lang['maps'][m['id']]['best'])}</dd></div>
  <div><dt>{esc(copy['tips'])}</dt><dd>{esc(lang['maps'][m['id']]['tips'])}</dd></div></dl>
</article>"""
        for m in ctx["game"]["maps"]
    )
    body = f"""{page_intro(ctx, 'maps', crumbs, legend(ctx) + status_line(ctx, 'official'))}
<div class="wrap">
  <div class="maps">{blocks}</div>
  <div class="cols">
    {section('spawns', copy['spawn_title'], paras(copy['spawn']))}
    {section('routes', copy['routes_title'], f"<p>{esc(copy['routes'])}</p>")}
  </div>
  <p class="note">{esc(copy['unconfirmed'])} {badge('unverified', lang)}</p>
</div>
{sources(ctx, ['steam-store', 'steam-news', 'insider-gaming', 'tpose', 'gamerblurb'])}"""
    return body, []


def render_modes(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    lang = ctx["lang"]
    copy = lang["pages"]["modes"]
    modes = ctx["game"]["modes"]
    rows = "".join(
        f'<tr><th scope="row"><a href="#{m["id"]}">{esc(m["name"])}</a>{gloss(ctx, "modes", m["id"])}</th>'
        f'<td>{esc(m["cod"])}</td><td>{esc(copy["respawn"] if m["respawn"] else copy["one_life"])}</td></tr>'
        for m in modes
    )
    table = (
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">{esc(copy["th_mode"])}</th>'
        f'<th scope="col">{esc(copy["th_cod"])}</th><th scope="col">{esc(copy["th_lives"])}</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
    )
    blocks = "".join(
        f"""<article class="mode" id="{m['id']}" aria-labelledby="{m['id']}-h">
  <h2 id="{m['id']}-h">{esc(m['name'])}{gloss(ctx, 'modes', m['id'])}</h2>
  <dl class="defs compact"><div><dt>{esc(copy['rules'])}</dt><dd>{esc(lang['modes'][m['id']]['rules'])}{exception_badge(ctx, m['conf'], 'official')}</dd></div>
  <div><dt>{esc(copy['tips'])}</dt><dd>{esc(lang['modes'][m['id']]['tips'])}</dd></div></dl>
</article>"""
        for m in modes
    )
    body = f"""{page_intro(ctx, 'modes', crumbs, status_line(ctx, 'official'))}
<div class="wrap">
  {section('overview', copy['table_title'], table)}
  <div class="modes">{blocks}</div>
  {section('private', copy['private_title'], paras(copy['private']))}
</div>
{sources(ctx, ['steam-store', 'steam-news', 'dexerto', 'gamerblurb'])}"""
    return body, []


def render_guide(ctx: dict, crumbs: str) -> tuple[str, list[str]]:
    lang = ctx["lang"]
    copy = lang["pages"]["guide"]
    first = '<ol class="steps">' + "".join(
        f'<li><strong>{esc(s["step"])}</strong><span>{esc(s["why"])}</span></li>' for s in copy["first_hour"]
    ) + "</ol>"
    prog = '<dl class="defs">' + "".join(
        f'<div><dt>{esc(p["k"])}</dt><dd>{esc(p["v"])}</dd></div>' for p in copy["progression"]
    ) + "</dl>"
    fixes = '<dl class="defs">' + "".join(
        f'<div><dt>{esc(p["k"])}</dt><dd>{esc(p["v"])}</dd></div>' for p in copy["fixes"]
    ) + "</dl>"
    links = (
        f'<p class="see-also"><a href="{esc(page_url(lang, "weapons"))}">{esc(lang["site"]["nav"]["weapons"])}</a>'
        f'<a href="{esc(page_url(lang, "maps"))}">{esc(lang["site"]["nav"]["maps"])}</a>'
        f'<a href="{esc(page_url(lang, "modes"))}">{esc(lang["site"]["nav"]["modes"])}</a></p>'
    )
    body = f"""{page_intro(ctx, 'guide', crumbs)}
<div class="wrap">
  <div class="cols">
    {section('first-hour', copy['first_hour_title'], first)}
    {section('progression', copy['progression_title'], prog)}
  </div>
  <div class="cols">
    {section('controls', copy['controls_title'], bullets(copy['controls']))}
    {section('tips', copy['tips_title'], bullets(copy['tips']))}
  </div>
  {section('fixes', copy['fixes_title'], fixes)}
  {links}
</div>
{sources(ctx, ['steam-store', 'steam-news', 'gamerblurb', 'tpose'])}"""
    return body, []
