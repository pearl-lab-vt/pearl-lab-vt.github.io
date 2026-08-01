#!/usr/bin/env python3
"""
Publish the site.

    python3 scripts/publish.py            # check, show what changed, commit, push
    python3 scripts/publish.py --check    # check and report only, touch nothing
    python3 scripts/publish.py -m "..."   # supply the commit message
    python3 scripts/publish.py --yes      # skip the confirmation prompt

What it does, in order:

  1. Validates every file in data/ and rebuilds feed.xml, sitemap.xml and the
     news permalink pages. A malformed file stops the run before git is touched.
  2. Works out which news items are NEW since the last commit, and which of
     those will reach LinkedIn — so you see the posts before you cause them.
  3. Shows you the changed files, asks once, then commits and pushes.

GitHub Actions takes it from there and deploys in about a minute.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BOLD, DIM, GREEN, YELLOW, RED, OFF = (
    "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[31m", "\033[0m"
)


def say(msg: str = "") -> None:
    print(msg, flush=True)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, **kw)


def git(*args: str) -> subprocess.CompletedProcess:
    return run(["git", *args])


def have_git_repo() -> bool:
    return (ROOT / ".git").is_dir()


def news_at_head() -> dict | None:
    """data/news.json as of the last commit, or None on the very first publish."""
    r = git("show", "HEAD:data/news.json")
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def published(items: list[dict]) -> list[dict]:
    return [i for i in items if not i.get("draft")]


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--check", "-n", action="store_true",
                    help="validate and report only; do not commit or push")
    ap.add_argument("-m", "--message", help="commit message")
    ap.add_argument("--yes", "-y", action="store_true", help="do not ask before pushing")
    args = ap.parse_args()

    # ---- 1. build -------------------------------------------------------
    say(f"{BOLD}1. Checking your data and rebuilding{OFF}")
    r = run([sys.executable, "scripts/build.py"])
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        say()
        say(f"{RED}Stopped. Fix the problem above and run this again.{OFF}")
        say(f"{DIM}Nothing was committed or pushed, and the live site is untouched.{OFF}")
        return 1
    run([sys.executable, "scripts/preview.py"])
    say(f"   {GREEN}data is valid{OFF}, preview.html rebuilt")
    say()

    # ---- 2. what is new, and what will reach LinkedIn --------------------
    news = json.loads((ROOT / "data" / "news.json").read_text(encoding="utf-8"))
    since = news.get("feed_since")
    now = published(news["items"])

    first_publish = False
    if have_git_repo():
        old = news_at_head()
        if old is None:
            first_publish = True
            new_items = []
        else:
            known = {i["slug"] for i in old.get("items", [])}
            new_items = [i for i in now if i["slug"] not in known]
    else:
        first_publish = True
        new_items = []

    say(f"{BOLD}2. What this publish changes{OFF}")
    if first_publish:
        say(f"   {DIM}First publish — every one of the {len(now)} news items is new.{OFF}")
    elif new_items:
        say(f"   {len(new_items)} new news item(s):")
        for i in new_items:
            say(f"     · {i['date']}  {i['title']}")
    else:
        say(f"   {DIM}No new news items.{OFF}")

    will_post = [i for i in new_items if not since or i["date"] >= since]
    held = [i for i in new_items if since and i["date"] < since]
    say()
    if will_post:
        say(f"   {YELLOW}{BOLD}These will be posted to LinkedIn{OFF} "
            f"{DIM}(via the RSS feed, once Buffer picks them up):{OFF}")
        for i in will_post:
            say(f"     · {i['title']}")
            body = i["summary"]
            say(f"       {DIM}{body[:110]}{'…' if len(body) > 110 else ''}{OFF}")
            say(f"       {DIM}{len(body)} characters{OFF}")
    else:
        say(f"   {DIM}Nothing new will reach LinkedIn from this publish.{OFF}")
    if held:
        say(f"   {DIM}{len(held)} item(s) stay off the feed "
            f"(dated before feed_since = {since}).{OFF}")
    say()

    # ---- 3. commit and push ---------------------------------------------
    if not have_git_repo():
        say(f"{BOLD}3. Not a git repository yet{OFF}")
        say("   Run these once, then use this script from now on:")
        say()
        say("     git init -b main")
        say("     git add .")
        say('     git commit -m "Initial PEARL Lab site"')
        say("     git remote add origin git@github.com:pearl-lab-vt/pearl-lab-vt.github.io.git")
        say("     git push -u origin main")
        return 0

    changed = git("status", "--porcelain").stdout.strip()
    if not changed:
        say(f"{BOLD}3. Nothing to publish{OFF} — no files have changed.")
        return 0

    say(f"{BOLD}3. Files changed{OFF}")
    for line in changed.splitlines():
        say(f"   {line}")
    say()

    if args.check:
        say(f"{DIM}--check: stopping here. Nothing committed, nothing pushed.{OFF}")
        say(f"{DIM}Open preview.html to see the result.{OFF}")
        return 0

    msg = args.message
    if not msg:
        if will_post:
            msg = f"Add: {will_post[0]['title']}" if len(will_post) == 1 \
                  else f"Add {len(will_post)} news items"
        elif new_items:
            msg = f"Add {len(new_items)} news item(s)"
        else:
            msg = f"Site update {date.today().isoformat()}"

    if not args.yes:
        say(f'Commit message: {BOLD}{msg}{OFF}')
        try:
            reply = input("Publish? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            say()
            reply = ""
        if reply not in ("y", "yes"):
            say(f"{DIM}Cancelled. Nothing was pushed.{OFF}")
            return 0

    for step, cmd in (("staging", ["add", "-A"]),
                      ("committing", ["commit", "-m", msg])):
        r = git(*cmd)
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            say(f"{RED}Failed while {step}.{OFF}")
            return 1

    say(f"{DIM}pushing…{OFF}")
    r = git("push")
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        say()
        say(f"{RED}Push failed.{OFF} The commit is saved locally; nothing is lost.")
        say(f"{DIM}If this is the first push, run: git push -u origin main{OFF}")
        return 1

    site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
    org_repo = site["url"].replace("https://", "").rstrip("/")
    org = org_repo.split(".")[0]
    say()
    say(f"{GREEN}{BOLD}Published.{OFF}")
    say(f"   Build:  https://github.com/{org}/{org_repo}/actions")
    say(f"   Live:   {site['url']}  {DIM}(about a minute){OFF}")
    if will_post:
        say(f"   LinkedIn: {len(will_post)} item(s) will appear in your Buffer queue "
            f"{DIM}within the hour{OFF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
