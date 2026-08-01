#!/usr/bin/env python3
"""
Generate feed.xml and one permalink page per news item from data/news.json.

Run it locally with:   python3 scripts/build.py
GitHub Actions runs it on every push to main (see .github/workflows/deploy.yml).

Nothing else on the site needs a build step — the HTML pages read the JSON
directly in the browser. This script exists so that (a) LinkedIn / RSS readers
have a real URL and a real preview card per item, and (b) the feed is valid XML.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name: str) -> dict:
    """Read a data file, and explain clearly if the JSON is malformed."""
    path = DATA / f"{name}.json"
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        lines = text.splitlines()
        print(f"\n  data/{name}.json is not valid JSON.", file=sys.stderr)
        print(f"  {e.msg}, at line {e.lineno}, column {e.colno}\n", file=sys.stderr)
        for n in range(max(1, e.lineno - 2), min(len(lines), e.lineno + 2) + 1):
            mark = ">>" if n == e.lineno else "  "
            print(f"  {mark} {n:4} | {lines[n - 1][:100]}", file=sys.stderr)
        hints = {
            "Extra data": "Something sits outside the outermost { }. A new news item "
                          "belongs INSIDE the \"items\": [ ... ] array, not at the top "
                          "of the file.",
            "Expecting ',' delimiter": "A comma is missing between two entries.",
            "Expecting value": "A trailing comma before ] or }, or an empty slot.",
            "Expecting property name": "A trailing comma after the last entry in a block.",
        }
        for key, hint in hints.items():
            if e.msg.startswith(key):
                print(f"\n  Likely cause: {hint}", file=sys.stderr)
                break
        print(f"\n  Nothing was changed. Fix data/{name}.json and run this again.",
              file=sys.stderr)
        raise SystemExit(1)


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def rfc822(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc, hour=12)
    return format_datetime(dt)


def pretty(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")


def published(items: list[dict]) -> list[dict]:
    out = [i for i in items if not i.get("draft")]
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def validate(items: list[dict]) -> list[str]:
    errors, seen = [], set()
    for i, item in enumerate(items):
        where = f"item {i} ({item.get('slug', 'no-slug')})"
        for field in ("slug", "date", "title", "summary"):
            if not item.get(field):
                errors.append(f"{where}: missing required field '{field}'")
        slug = item.get("slug", "")
        if slug and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            errors.append(f"{where}: slug must be lowercase letters, digits and hyphens")
        if slug in seen:
            errors.append(f"{where}: duplicate slug '{slug}'")
        seen.add(slug)
        if item.get("date"):
            try:
                datetime.strptime(item["date"], "%Y-%m-%d")
            except ValueError:
                errors.append(f"{where}: date must be YYYY-MM-DD, got {item['date']!r}")
    return errors


ARTICLE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_esc} · PEARL Lab</title>
<meta name="description" content="{summary_esc}">
<link rel="canonical" href="{url}">
<link rel="icon" href="../../assets/logo.svg" type="image/svg+xml">
<link rel="alternate icon" href="../../assets/favicon.png">
<link rel="stylesheet" href="../../assets/style.css">
<link rel="alternate" type="application/rss+xml" title="PEARL Lab news" href="../../feed.xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="PEARL Lab — Virginia Tech">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{summary_esc}">
<meta property="og:url" content="{url}">
<meta property="article:published_time" content="{date}">
{og_image}<meta name="twitter:card" content="summary{large}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site" id="site-header"></header>
<main id="main">
  <article class="wrap article">
    <div class="kicker">{pretty_date}{cat}</div>
    <h1>{title_esc}</h1>
    {image_tag}
    <p style="font-size:1.1rem">{summary_esc}</p>
    {body}
    {links}
    <p style="margin-top:36px"><a href="../../news.html">&larr; All news</a></p>
  </article>
</main>
<footer class="site" id="site-footer"></footer>
<script>window.PEARL_BASE = "../../";</script>
<script src="../../assets/app.js"></script>
<script>bootChrome("news.html");</script>
</body>
</html>
"""


def build_articles(site: dict, items: list[dict]) -> int:
    outdir = ROOT / "news"
    # Clear stale article directories so deleted news items disappear.
    # Some synced folders (OneDrive, Dropbox) disallow deletes; the pages are
    # regenerated either way, so a failure here is a warning, not an error.
    if outdir.exists():
        for child in sorted(outdir.iterdir()):
            if child.is_dir():
                try:
                    for f in child.iterdir():
                        f.unlink()
                    child.rmdir()
                except OSError as e:
                    print(f"    note: could not remove {child.name}/ ({e.strerror})",
                          file=sys.stderr)
    outdir.mkdir(exist_ok=True)

    for item in items:
        url = f"{site['url'].rstrip('/')}/news/{item['slug']}/"
        img = item.get("image")
        img_url = f"{site['url'].rstrip('/')}/{img.lstrip('/')}" if img else ""
        links = item.get("links") or []
        page = ARTICLE.format(
            title_esc=html.escape(item["title"], quote=True),
            summary_esc=html.escape(item["summary"], quote=True),
            url=url,
            date=item["date"],
            pretty_date=pretty(item["date"]),
            cat=f' · {html.escape(item["category"])}' if item.get("category") else "",
            body=item.get("body", ""),
            image_tag=f'<img src="../../{html.escape(img)}" alt="">' if img else "",
            og_image=f'<meta property="og:image" content="{html.escape(img_url, quote=True)}">\n' if img else "",
            large="_large_image" if img else "",
            links=(
                '<div class="linkrow">'
                + "".join(
                    f'<a href="{html.escape(l["url"], quote=True)}">{html.escape(l["label"])}</a>'
                    for l in links
                )
                + "</div>"
            )
            if links
            else "",
        )
        d = outdir / item["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
    return len(items)


def build_feed(site: dict, news: dict, items: list[dict]) -> int:
    # A feed carries the most recent N items — that is what readers expect, and
    # an EMPTY feed is rejected outright by most of them (Buffer included).
    # feed_since is an optional floor: leave it blank for normal behaviour, and
    # set it to today's date only if you switch to a tool that AUTO-posts, so
    # the backlog cannot be dumped onto social media in one burst.
    since = news.get("feed_since") or None
    limit = int(news.get("feed_max_items") or 20)
    feed_items = [i for i in items if not since or i["date"] >= since][:limit]
    base = site["url"].rstrip("/")

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/">',
        "<channel>",
        f"<title>{html.escape(site['name'])} — {html.escape(site['tagline'])}</title>",
        f"<link>{base}/</link>",
        f"<description>{html.escape(site['description'])}</description>",
        "<language>en-us</language>",
        f"<lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>",
        f'<atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml" />',
    ]
    for item in feed_items:
        url = f"{base}/news/{item['slug']}/"
        desc = item["summary"]
        if item.get("body"):
            desc += " " + strip_tags(item["body"])
        parts += [
            "<item>",
            f"<title>{html.escape(item['title'])}</title>",
            f"<link>{url}</link>",
            f"<guid isPermaLink=\"true\">{url}</guid>",
            f"<pubDate>{rfc822(item['date'])}</pubDate>",
            f"<description>{html.escape(desc)}</description>",
        ]
        if item.get("category"):
            parts.append(f"<category>{html.escape(item['category'])}</category>")
        parts.append("</item>")
    parts += ["</channel>", "</rss>", ""]

    (ROOT / "feed.xml").write_text("\n".join(parts), encoding="utf-8")
    return len(feed_items)


def build_sitemap(site: dict, items: list[dict]) -> None:
    base = site["url"].rstrip("/")
    urls = [f"{base}/{p}" for p in
            ("", "research.html", "people.html", "publications.html", "news.html")]
    urls += [f"{base}/news/{i['slug']}/" for i in items]
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")


def main() -> int:
    site = load("site")
    news = load("news")

    # Fail loudly on malformed data instead of shipping a broken feed.
    errors = validate(news["items"])
    for name in ("people", "publications", "research", "sponsors"):
        load(name)  # raises on invalid JSON
    if errors:
        print("data/news.json has problems:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    items = published(news["items"])
    n_articles = build_articles(site, items)
    n_feed = build_feed(site, news, items)
    build_sitemap(site, items)

    drafts = sum(1 for i in news["items"] if i.get("draft"))
    print(f"OK  {n_articles} news pages, {n_feed} feed entries, {drafts} drafts skipped")
    if news.get("feed_since"):
        print(f"    feed_since={news['feed_since']} (older items are on the site but not in the feed)")
    if n_feed == 0:
        print("    WARNING: the feed has no items. Most readers reject an empty "
              "feed — clear feed_since in data/news.json.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
