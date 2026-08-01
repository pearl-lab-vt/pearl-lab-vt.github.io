# PEARL Lab website

The site for **PEARL** — Performance Engineering for Accelerators, Runtimes and Learning — at Virginia Tech.
Live at <https://pearl-lab-vt.github.io>.

Everything you will ever edit is a **JSON file in `data/`**. The HTML pages read
those files in the browser, so adding a person or a paper means editing one file
and committing it. There is no Jekyll, no theme, no Gemfile, no `npm install`.

---

## 1. One-time setup

### Create the GitHub organization and repository

1. Go to <https://github.com/organizations/plan> and create a **free** organization
   named `pearl-lab-vt`. (If that name is taken, pick another and update `url` in
   `data/site.json` plus `og:url` in the five `*.html` files.)
2. In that org, create a public repository named exactly **`pearl-lab-vt.github.io`**.
3. Push this folder to it:

   ```bash
   cd ~/Library/CloudStorage/OneDrive-VirginiaTech/Web/pearl-lab-vt.github.io
   git init -b main
   git add .
   git commit -m "Initial PEARL Lab site"
   git remote add origin git@github.com:pearl-lab-vt/pearl-lab-vt.github.io.git
   git push -u origin main
   ```

4. In the repo, go to **Settings → Pages → Build and deployment** and set
   **Source = GitHub Actions**. (Not "Deploy from a branch" — the workflow in
   `.github/workflows/deploy.yml` handles deployment.)
5. Push once more, or run the workflow manually from the **Actions** tab. The site
   goes live in about a minute.

### Add your students as maintainers

**Settings → Collaborators and teams**. Give students *Write* access so they can
add their own papers and news. Everything they need to touch is JSON — no
web-development knowledge required.

### Optional: a custom domain

If you ever want `pearl.cs.vt.edu`, add a file named `CNAME` containing just that
hostname, ask VT IT to point a CNAME record at `pearl-lab-vt.github.io`, then set the
domain under **Settings → Pages**. Update `url` in `data/site.json` to match.

---

## 2. Everyday editing

| To change… | Edit |
|---|---|
| Lab name, tagline, blurb, social links | `data/site.json` |
| Research thrusts shown on the home and research pages | `data/research.json` |
| Members and alumni | `data/people.json` |
| Publications | `data/publications.json` |
| **News** (this is the one that feeds LinkedIn) | `data/news.json` |
| Sponsor logos shown on the home and research pages | `data/sponsors.json` |

You can edit any of these directly on github.com — click the file, click the
pencil, commit. The site rebuilds itself.

### Publishing from your machine

```bash
python3 scripts/publish.py           # check, review, commit, push
python3 scripts/publish.py --check   # check and preview only, touch nothing
```

The script validates every data file and rebuilds the feed before it touches
git, so malformed JSON stops the run rather than reaching the site. It then
lists what changed and — importantly — **which items are about to be posted to
LinkedIn**, with the exact text, before asking whether to push. Answer `n` and
nothing happens.

`--check` is the safe way to look at your edits: it validates, rebuilds
`preview.html`, and stops.

See `LINKEDIN.md` for the LinkedIn side.

### Adding a news item

Add an object at the **top** of `items` in `data/news.json`:

```json
{
  "slug": "ics27-paper",
  "date": "2026-09-14",
  "category": "papers",
  "title": "Something good happened",
  "summary": "Two or three sentences. This exact text becomes the LinkedIn post, so write it as if it were the post.",
  "links": [{ "label": "Paper", "url": "https://example.org/paper" }]
}
```

| Field | Required | Notes |
|---|---|---|
| `slug` | yes | lowercase, hyphens only. Becomes the URL `/news/<slug>/`. Never change it after publishing — the RSS feed uses it as the item's identity. |
| `date` | yes | `YYYY-MM-DD` |
| `title` | yes | |
| `summary` | yes | **This is what gets posted to LinkedIn.** Write it as a finished post, not a stub. |
| `category` | no | `papers`, `awards`, `grants`, `people`, `service` — creates the filter buttons |
| `body` | no | Longer HTML shown on the site only |
| `links` | no | `[{ "label": …, "url": … }]` |
| `image` | no | Path like `assets/news/thing.png`. Becomes the LinkedIn preview image. |
| `draft` | no | `true` hides it from the site **and** the feed |

If the JSON is malformed, the GitHub Action fails with a clear message and the
live site is left untouched — a bad commit can't take the site down.

### Preview locally

Two ways:

```bash
python3 scripts/preview.py     # writes preview.html — just double-click it
```

or serve the real thing, which also exercises the feed and the news permalinks:

```bash
python3 scripts/build.py
python3 -m http.server 8000    # then open http://localhost:8000
```

Do not double-click `index.html` itself. Browsers block `fetch()` on `file://`
URLs, so the page would come up empty. That is what `preview.html` is for.

---

## 3. Feeding LinkedIn

Every published news item becomes:

- a page at `https://pearl-lab-vt.github.io/news/<slug>/` with Open Graph tags, so
  LinkedIn renders a proper preview card, and
- an entry in `https://pearl-lab-vt.github.io/feed.xml`.

Connect the feed to the LinkedIn company page **once**, and from then on writing a
news item is the only thing you do.

Setup and the day-to-day routine are written up in **`LINKEDIN.md`**. Short
version: sign up at Buffer, connect the PEARL LinkedIn **Page**, point it at
`https://pearl-lab-vt.github.io/feed.xml`, and set new items to queue for your
approval.

### Alternatives

- **Zapier** — "New item in RSS feed" → "Create Share Update in LinkedIn Pages".
  Free tier covers a lab's posting volume comfortably.
- **IFTTT** — "RSS Feed → LinkedIn". Simplest, least control over formatting.
- **Manual** — the site *is* the source of truth; open `/news/<slug>/`, paste the
  URL into LinkedIn, and LinkedIn pulls the title, summary and image itself.

### The backlog guard

`data/news.json` has a `feed_since` field:

```json
"feed_since": "2026-08-01"
```

Only items dated on or after that date go into `feed.xml`. This exists because
RSS-to-LinkedIn tools post *everything* they find the first time they read a feed
— without this, connecting Buffer would dump a decade of archived news onto the
company page at once. Historical items still appear on the website; they are just
not in the feed.

Leave it alone once the site is live.

---

## 3a. Sponsor logos

`data/sponsors.json` drives the band under the hero. Each entry points at a file
in `assets/sponsors/`. **If the file is not there, the entry renders as the
sponsor's name in type** — so the page is always correct, and dropping in an
official logo upgrades it in place.

`assets/sponsors/README.md` lists the official download source for each mark and
summarises what each owner's brand policy permits. Read it before adding files.
Do not take logos from aggregator sites; do not redraw or recolour them.

Set `"hidden": true` on an entry to keep it on file without displaying it.

---

## 4. How it fits together

```
index.html  research.html  people.html      static shells; app.js fills them in
publications.html  news.html                from data/*.json at page load

data/*.json                                 the only files you edit
assets/sponsors/                            official sponsor logo files
assets/style.css                            all styling; colors live in :root
assets/app.js                               all rendering

scripts/publish.py                          the command you actually run
scripts/build.py                            writes feed.xml, sitemap.xml,
                                            robots.txt and news/<slug>/index.html
scripts/preview.py                          writes the offline preview.html
.github/workflows/deploy.yml                runs build.py, deploys to Pages
```

`feed.xml`, `sitemap.xml`, `robots.txt` and `news/` are generated and are listed in
`.gitignore` — GitHub Actions rebuilds them on every push, so the repository only
ever contains files a human wrote.

To restyle, edit the custom properties at the top of `assets/style.css`. The site
already follows the reader's light/dark preference.

---

## 5. Credits

Content carried over from the original PEARL site and from
<https://dsniko.github.io>.
