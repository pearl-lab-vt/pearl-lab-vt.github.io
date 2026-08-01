# Getting lab news onto LinkedIn

The site is the source of truth. You write a news item once, in
`data/news.json`, and it reaches three places: the website, the RSS feed, and
the LinkedIn company page. You never write the same thing twice.

This document is the one-time setup, then the routine.

---

## How it works

```
data/news.json  →  publish  →  feed.xml  →  Buffer  →  LinkedIn company page
```

Every published news item becomes a page at
`https://pearl-lab-vt.github.io/news/<slug>/` carrying Open Graph tags, so
LinkedIn renders a proper preview card with the title, the summary and the
image if there is one. Buffer watches `feed.xml` and drops each new entry into a
queue for you to approve.

**The `summary` field is the LinkedIn post.** Write it as a finished post, not
as a stub you intend to expand later. Two or three sentences, opening with the
problem rather than the venue, is the shape that works. Look at any existing
entry in `data/news.json` for the pattern.

---

## One-time setup, about ten minutes

Do this only after the site is live at <https://pearl-lab-vt.github.io> and you
can open `https://pearl-lab-vt.github.io/feed.xml` in a browser and see XML.

**1.** Sign up at <https://buffer.com>. The free tier covers a lab's volume.

**2.** Connect a channel. Choose **LinkedIn Page**, not LinkedIn Profile, and
pick the PEARL company page. You need admin rights on the page, which you have.

**3.** Find the RSS feature. In Buffer it lives under **Create → Feeds** (older
accounts may show it as "Content Inbox"). Add:

```
https://pearl-lab-vt.github.io/feed.xml
```

**4.** Buffer's Feeds do **not** post by themselves. New items appear in a
reading view and you click **Create Post** on the ones you want, which opens a
composer already carrying the title, the summary and the link. One click per
item; the writing is already done.

**5.** Confirm it loads and shows your recent news items.

---

## What goes in the feed

`feed.xml` carries the most recent `feed_max_items` published news items,
20 by default. That is what feed readers expect, and it matters more than it
sounds: **an empty feed is rejected outright by most readers, Buffer included,
with a generic "couldn't load feed" error.** If Buffer ever refuses your feed,
open `https://pearl-lab-vt.github.io/feed.xml` and count the `<item>` elements
before suspecting anything else.

`data/news.json` also has a `feed_since` field, normally **blank**. Setting it
to a date keeps everything older out of the feed. You only want that if you
move to a tool that posts *automatically* — an auto-poster reading a full feed
for the first time will push the whole archive to the company page at once.
With Buffer's click-to-post model there is nothing to guard against, so leave
it empty.

`scripts/build.py` warns on stderr if a build produces a feed with no items.

---

## The routine, once set up

1. Add an entry at the top of `items` in `data/news.json`.
2. `python3 scripts/publish.py`

The publish script tells you, before it pushes anything, exactly which items
will reach LinkedIn and shows you the text that will be posted:

```
   These will be posted to LinkedIn (via the RSS feed, once Buffer picks them up):
     · FACT: agentic kernel synthesis, grounded in CUTLASS
       Ask a language model for a fast CUDA kernel and it will hand back…
       412 characters
```

If that text is not what you want on the company page, answer `n` at the
prompt, fix the `summary`, and run it again.

3. Buffer picks the item up within the hour and puts it in your queue.
4. Approve it in Buffer. It posts.

---

## If something does not appear

**Check the feed first.** Open `https://pearl-lab-vt.github.io/feed.xml` and
look for the item. If it is missing there, the problem is on your side, and it
is nearly always one of three things: the item is marked `"draft": true`, its
date is before `feed_since`, or the deploy has not finished. Check the Actions
tab on GitHub for a green check.

**If the item is in the feed but not in Buffer**, Buffer polls on its own
schedule and can take up to an hour on the free tier. There is usually a manual
refresh in the feed settings.

**If a post looks wrong on LinkedIn**, LinkedIn caches preview cards
aggressively. Their Post Inspector at
<https://www.linkedin.com/post-inspector/> forces a re-fetch of a URL.

---

## Changing your mind about a post

Never edit the `slug` of an item that has already been published. The feed uses
it as the item's permanent identity, and changing it makes Buffer treat the item
as brand new and post it a second time.

Editing the `title` or `summary` of an already-posted item is safe: the website
updates, and the feed entry changes, but Buffer will not repost it.

To remove an item entirely, delete it from `data/news.json` and publish. The
page and the feed entry disappear. Anything already posted to LinkedIn stays
there and has to be removed on LinkedIn.

---

## Alternatives, if Buffer stops suiting you

- **Zapier** — "New item in RSS feed" → "Create Share Update in LinkedIn
  Pages". More configurable, and it appears in the Claude connector registry if
  you later want posts triggered from a conversation.
- **IFTTT** — simplest of the three, least control over formatting.
- **By hand** — open `https://pearl-lab-vt.github.io/news/<slug>/`, paste the
  URL into LinkedIn, and let LinkedIn pull the title, summary and image from the
  Open Graph tags. No third-party account at all.

Nothing about the site depends on which one you pick. The feed is a plain RSS
2.0 document and any tool that reads RSS can consume it.
