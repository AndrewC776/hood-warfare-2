# Hood Warfare 2 Guide

Unofficial multilingual guide to Hood Warfare 2 (Trapstar Games, Steam, 2026): price and download, weapons, killstreaks, maps, modes, beginner tips, patch notes and live Steam player count.

Live site: https://andrewc776.github.io/hood-warfare-2/

Languages: English, 简体中文, 繁體中文, 日本語, 한국어, Español, Português (Brasil), Русский, Deutsch, Français.

## How it works

- `data/game.json` holds game facts, each tagged `official`, `community` or `unverified`, with sources.
- `i18n/<lang>.json` holds all page copy; `i18n/en.json` is the reference. `i18n/promo.json` holds the partner promo.
- `scripts/fetch_steam.py` pulls price (13 regions), reviews, player count, screenshots and patch notes from the Steam Web API into `data/steam.json` and appends `data/history.json`.
- `scripts/build.py` renders static HTML for every language into `_site/` (no dependencies, Python 3.12).
- `.github/workflows/site.yml` refreshes Steam data every 3 hours, commits it, rebuilds and deploys to GitHub Pages.

## Local

```bash
python3 scripts/fetch_steam.py
python3 scripts/check_i18n.py
python3 scripts/build.py
```

Not affiliated with Trapstar Games or Valve.
