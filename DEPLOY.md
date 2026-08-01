# PEARL site — deploy checklist

Org name is **pearl-lab-vt**. Every file in the project already points at
`https://pearl-lab-vt.github.io`, so nothing needs editing first.

---

## 1. Create the organization  (browser)

Open <https://github.com/account/organizations/new?plan=free>

- Organization name: `pearl-lab-vt`
- Contact email: `dsn@vt.edu`
- Owned by: **My personal account**

Click **Next**, then skip inviting members and skip the survey.

## 2. Create the repository  (browser)

Open <https://github.com/organizations/pearl-lab-vt/repositories/new>

- Repository name: `pearl-lab-vt.github.io`  ← exactly this, including `.github.io`
- Visibility: **Public**
- Leave every checkbox unticked — no README, no .gitignore, no license

Click **Create repository**.

## 3. Push the files  (Terminal)

Open Terminal (⌘-Space, type `Terminal`) and paste this whole block:

```bash
cd ~/Library/CloudStorage/OneDrive-VirginiaTech/Web/pearl-lab-vt.github.io
git init -b main
git add .
git commit -m "Initial PEARL Lab site"
git remote add origin git@github.com:pearl-lab-vt/pearl-lab-vt.github.io.git
git push -u origin main
```

Success looks like a final line containing `main -> main`.

Your existing GitHub SSH key is already trusted (you push `dsniko.github.io`
the same way), so there should be no password prompt.

## 4. Turn on Pages  (browser)

Open <https://github.com/pearl-lab-vt/pearl-lab-vt.github.io/settings/pages>

Under **Build and deployment → Source**, choose **GitHub Actions**.

Not "Deploy from a branch" — that setting skips the build step, and the RSS
feed and the news permalink pages would never be generated.

## 5. Watch it deploy

Open the **Actions** tab. A run called "Build and deploy" starts on its own.
Green check, about one minute.

Then visit **https://pearl-lab-vt.github.io**

A 404 for the first two or three minutes is normal.

---

## Afterwards

**Add students:** Settings → Collaborators and teams → Add people → role **Write**.

**Connect LinkedIn:** sign up at buffer.com, add the PEARL company page as a
channel, then add the feed `https://pearl-lab-vt.github.io/feed.xml` and set new
items to queue for your approval.

The feed is empty on day one by design (`feed_since` is 2026-08-01), so the 24
historical items will not flood the company page. Your next news entry is the
first thing that posts.

---

## The editing loop, from then on

1. Edit a file in `data/` — on github.com with the pencil icon, or locally.
2. If local: `git add . && git commit -m "add X" && git push`
3. Wait about a minute.

Malformed JSON fails the Action with a specific error and leaves the live site
on its last good build. A bad commit cannot take the site down.

## Still open

- News dates are the month from your CV with a plausible day. Adjust any that matter.
- Your CV lists Emadeldin Abdrabou under ECE; your mentees page says CS. The site
  omits the department rather than pick one.
- CV entry [53] names the SCALE-R sponsor as plain "Sony"; the site calls it a
  Sony Faculty Innovation Award, following what you told me.
- `pearl-lab-web/_to_delete/` holds one orphaned page. Delete that folder.
