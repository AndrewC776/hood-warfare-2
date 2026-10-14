"""Check that every i18n/<lang>.json matches the structure of i18n/en.json.

Reports missing/extra keys, list-length mismatches, and strings whose
{placeholders} or HTML tags differ from English. Exit code 1 on any problem.
Usage: python3 scripts/check_i18n.py [lang ...]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

I18N = Path(__file__).resolve().parent.parent / "i18n"
FREE_FORM = {"gloss", "meta"}
PLACEHOLDER = re.compile(r"\{[a-z_]+\}")
TAG = re.compile(r"</?([a-z]+)[^>]*>")


def walk(ref, other, path, problems):
    if path and path[0] in FREE_FORM:
        return
    if isinstance(ref, dict):
        if not isinstance(other, dict):
            problems.append(f"{'.'.join(path)}: expected object")
            return
        for key in ref:
            if key not in other:
                problems.append(f"{'.'.join(path + [key])}: missing")
            else:
                walk(ref[key], other[key], path + [key], problems)
        for key in other:
            if key not in ref and not (path == [] and key in FREE_FORM):
                problems.append(f"{'.'.join(path + [key])}: extra key")
    elif isinstance(ref, list):
        if not isinstance(other, list) or len(other) != len(ref):
            problems.append(f"{'.'.join(path)}: list length differs")
            return
        for i, (a, b) in enumerate(zip(ref, other)):
            walk(a, b, path + [str(i)], problems)
    elif isinstance(ref, str):
        if not isinstance(other, str) or not other.strip():
            problems.append(f"{'.'.join(path)}: empty or not a string")
            return
        if sorted(PLACEHOLDER.findall(ref)) != sorted(PLACEHOLDER.findall(other)):
            problems.append(f"{'.'.join(path)}: placeholders differ")
        if sorted(TAG.findall(ref)) != sorted(TAG.findall(other)):
            problems.append(f"{'.'.join(path)}: HTML tags differ")


def main(langs):
    ref = json.loads((I18N / "en.json").read_text())
    files = [I18N / f"{l}.json" for l in langs] or sorted(p for p in I18N.glob("*.json") if p.stem not in ("en", "promo"))
    failed = False
    for f in files:
        problems = []
        data = json.loads(f.read_text())
        for key in ("lang", "html_lang", "hreflang", "name", "og_locale", "path", "price_cc", "date_format", "months", "thousands_sep", "percent_format"):
            if key not in data.get("meta", {}):
                problems.append(f"meta.{key}: missing")
        walk(ref, data, [], problems)
        status = "ok" if not problems else f"{len(problems)} problem(s)"
        print(f"{f.name}: {status}")
        for p in problems:
            print("  -", p)
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
