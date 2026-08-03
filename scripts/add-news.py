#!/usr/bin/env python3
"""
Add a news item to data/news.json without hand-editing JSON.

    python3 scripts/add-news.py item.json

`item.json` holds ONE news item — just the object, e.g.

    {
      "slug": "icecs26-riscv-transformers",
      "date": "2026-11-08",
      "category": "papers",
      "title": "...",
      "summary": "...",
      "links": [{ "label": "ICECS 2026", "url": "https://www.icecs2026.gr" }]
    }

The script validates it, refuses duplicate slugs, inserts it in the right place
inside `items`, and rewrites the file with the surrounding structure intact.
It exists because pasting an object into the wrong part of a JSON file is the
easiest mistake to make and the most annoying one to read as an error.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWS = ROOT / "data" / "news.json"

REQUIRED = ("slug", "date", "title", "summary")


def die(msg: str) -> None:
    print(f"\n  {msg}\n", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2:
        die("Usage: python3 scripts/add-news.py item.json")

    src = Path(sys.argv[1])
    if not src.exists():
        die(f"No such file: {src}")

    try:
        item = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{src} is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}")

    if isinstance(item, list):
        die(f"{src} holds a list. It should hold a single item object: {{ ... }}")
    if not isinstance(item, dict):
        die(f"{src} should hold a single item object: {{ ... }}")

    missing = [f for f in REQUIRED if not item.get(f)]
    if missing:
        die(f"The item is missing: {', '.join(missing)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", item["slug"]):
        die(f"slug {item['slug']!r} must be lowercase letters, digits and hyphens")
    try:
        datetime.strptime(item["date"], "%Y-%m-%d")
    except ValueError:
        die(f"date {item['date']!r} must be YYYY-MM-DD")

    news = json.loads(NEWS.read_text(encoding="utf-8"))
    if any(i["slug"] == item["slug"] for i in news["items"]):
        die(f"data/news.json already has an item with slug {item['slug']!r}. "
            f"Never reuse a slug — feed readers treat it as the item's identity.")

    backup = NEWS.with_suffix(".json.bak")
    shutil.copy2(NEWS, backup)

    news["items"].insert(0, item)
    news["items"].sort(key=lambda i: i["date"], reverse=True)
    NEWS.write_text(json.dumps(news, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    json.loads(NEWS.read_text(encoding="utf-8"))  # prove it still parses

    pos = next(n for n, i in enumerate(news["items"]) if i["slug"] == item["slug"])
    print(f"\n  Added '{item['title']}'")
    print(f"  {item['date']} · position {pos + 1} of {len(news['items'])}")
    print(f"  Previous file saved as {backup.name}\n")
    print(f"  This text will be the LinkedIn post ({len(item['summary'])} characters):\n")
    for line in (item["summary"][i:i + 76] for i in range(0, len(item["summary"]), 76)):
        print(f"    {line}")
    print("\n  Next:  python3 scripts/publish.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
