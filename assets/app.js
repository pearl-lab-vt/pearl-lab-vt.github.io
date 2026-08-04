/* PEARL Lab — all client-side rendering.
   Data lives in /data/*.json. Nothing here needs a build step. */

const DATA = {};

async function load(name) {
  if (DATA[name]) return DATA[name];
  const res = await fetch(`${window.PEARL_BASE || ''}data/${name}.json`, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`Could not load data/${name}.json (${res.status})`);
  DATA[name] = await res.json();
  return DATA[name];
}

const el = (sel) => document.querySelector(sel);

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function fmtDate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-US',
    { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
}

function initials(name) {
  return name.split(/\s+/).filter(w => /^[A-Za-z]/.test(w)).slice(0, 2)
    .map(w => w[0].toUpperCase()).join('');
}

function published(items) {
  return items.filter(i => !i.draft).sort((a, b) => b.date.localeCompare(a.date));
}

/* ---------- shared chrome ---------- */

async function renderChrome(current) {
  const site = await load('site');
  const base = window.PEARL_BASE || '';
  const pages = [
    ['index.html', 'Home'],
    ['research.html', 'Research'],
    ['people.html', 'People'],
    ['publications.html', 'Publications'],
    ['news.html', 'News'],
  ];

  // The logo is inlined (not an <img>) so it inherits the page's colour
  // variables and recolours itself in dark mode. Swap assets/logo.svg to
  // change it — nothing else needs editing.
  let logo = window.__PEARL_LOGO__ || '';
  if (!logo) {
    try {
      const r = await fetch(`${base}assets/logo.svg`, { cache: 'no-cache' });
      if (r.ok) logo = await r.text();
    } catch (_) { /* logo is decorative; the wordmark stands on its own */ }
  }

  // Institutional band. The Virginia Tech logo is a licensed trademark: download
  // the official file from brand.vt.edu (VT login) and save it at the path in
  // site.institution_logo. Until then this shows the university name in type,
  // which is always permissible.
  const band = el('#institution');
  if (band) {
    band.innerHTML = `<div class="wrap">
      <a class="inst" href="${esc(site.institution_url || 'https://www.vt.edu')}">
        ${site.institution_logo ? `<img src="${base}${esc(site.institution_logo)}"
             alt="${esc(site.institution)}"
             onerror="this.closest('.inst').classList.add('nologo');this.remove();">` : ''}
        <span class="inst-name">${esc(site.institution)}</span>
      </a>
      <span class="inst-depts">${site.departments.map(d =>
        `<a href="${esc(d.url)}">${esc(d.name)}</a>`).join(' &middot; ')}</span>
    </div>`;
  }

  const header = el('#site-header');
  if (header) {
    header.innerHTML = `<div class="wrap">
      <a class="brand" href="${base}index.html">
        ${logo ? `<span class="logo" aria-hidden="true">${logo}</span>` : ''}
        <span class="mark">${esc(site.name)}</span>
        <span class="sub">${esc(site.tagline)}</span>
      </a>
      <nav class="site" aria-label="Main">
        ${pages.map(([href, label]) =>
          `<a href="${base}${href}"${href === current ? ' aria-current="page"' : ''}>${label}</a>`).join('')}
      </nav>
    </div>`;
  }

  const footer = el('#site-footer');
  if (footer) {
    const l = site.links;
    footer.innerHTML = `<div class="wrap cols">
      <div>
        <strong>${esc(site.name)}</strong> — ${esc(site.tagline)}<br>
        ${site.departments.map(d => `<a href="${esc(d.url)}">${esc(d.name)}</a>`).join(' &middot; ')}<br>
        ${esc(site.institution)}, ${esc(site.location)}
      </div>
      <div class="links">
        <a href="mailto:${esc(l.email)}">Email</a>
        ${l.linkedin ? `<a href="${esc(l.linkedin)}">LinkedIn</a>` : ''}
        ${l.github ? `<a href="${esc(l.github)}">GitHub</a>` : ''}
        ${l.scholar ? `<a href="${esc(l.scholar)}">Scholar</a>` : ''}
        ${l.orcid ? `<a href="${esc(l.orcid)}">ORCID</a>` : ''}
        <a href="${base}feed.xml">RSS</a>
      </div>
    </div>`;
  }
}

/* ---------- home ---------- */

/* ---------- sponsors ---------- */

/* This is an acknowledgement of support first and a logo strip second.
   A named sponsor with the award it funded is the thing NSF and DOE actually
   require, and it needs no permission from anybody. A logo, where we have the
   official file and the right to display it, sits above that name.

   Logos are shown unmodified, at full colour, on a white plate: brand policies
   almost universally forbid recolouring or filtering, and every one of these
   marks is drawn for a light background. If a file is missing, the <img>
   removes itself and the entry stands on the name and the award — which is
   why the section reads as deliberate rather than broken while we wait for
   permissions. */
function renderSponsors(sponsors) {
  const base = window.PEARL_BASE || '';
  const items = (sponsors.items || []).filter(s => !s.hidden);
  if (!items.length) return '';

  return `<div class="wrap">
    <h2 class="sponsor-head">${esc(sponsors.heading)}</h2>
    <ul class="sponsor-row">
      ${items.map(s => `<li class="sponsor${s.file ? '' : ' nologo'}">
        <a class="sponsor-link" href="${esc(s.url)}">
          ${s.file ? `<img src="${base}${esc(s.file)}" alt="${esc(s.name)}" loading="lazy"
             onerror="this.closest('.sponsor').classList.add('nologo');this.remove();">` : ''}
          <span class="sponsor-name">${esc(s.name)}</span>
        </a>
      </li>`).join('')}
    </ul>
    ${sponsors.note ? `<p class="sponsor-note">${esc(sponsors.note)}</p>` : ''}
  </div>`;
}

/* ---------- home ---------- */

async function renderHome() {
  const [site, research, news, sponsors] = await Promise.all(
    [load('site'), load('research'), load('news'), load('sponsors')]);
  const base = window.PEARL_BASE || '';

  el('#hero').innerHTML = `<div class="wrap">
    <div class="eyebrow">${esc(site.institution)}</div>
    <h1>${esc(research.headline)}</h1>
    <p class="lede">${esc(research.intro)}</p>
    ${site.acronym ? `<div class="acronym">${Object.entries(site.acronym)
        .map(([k, v]) => `<div><b>${esc(k)}</b>${esc(v)}</div>`).join('')}</div>` : ''}
    <p class="meta">Directed by <a href="${esc(site.director.url)}">${esc(site.director.name)}</a>,
      ${esc(site.director.title)} &middot;
      ${site.departments.map(d => `<a href="${esc(d.url)}">${esc(d.name)}</a>`).join(', ')}</p>
  </div>`;

  const sponsorBand = el('#sponsors');
  if (sponsorBand) sponsorBand.innerHTML = renderSponsors(sponsors);

  el('#thrusts').innerHTML = `<div class="wrap">
    <div class="section-head">
      <h2>Research</h2>
      <a href="${base}research.html">Research program &rarr;</a>
    </div>
    <div class="grid three">
      ${research.thrusts.map(t => `<div class="card">
        <h3><a href="${base}research.html#${esc(t.id)}">${esc(t.title)}</a></h3>
        ${t.stake ? `<p class="stake">${esc(t.stake)}</p>` : ''}
        <p>${esc(t.blurb)}</p>
      </div>`).join('')}
    </div>
    ${research.closing ? `<p class="closing">${esc(research.closing)}</p>` : ''}
  </div>`;

  const recent = published(news.items).slice(0, 5);
  el('#latest').innerHTML = `<div class="wrap">
    <div class="section-head">
      <h2>Recent news</h2>
      <a href="${base}news.html">All news &rarr;</a>
    </div>
    ${recent.length ? `<ul class="news-list">${recent.map(newsRow).join('')}</ul>`
      : `<p class="callout">No published news items yet. Add one to <code>data/news.json</code>.</p>`}
  </div>`;
}

/* ---------- news ---------- */

function newsRow(item) {
  const base = window.PEARL_BASE || '';
  const links = (item.links || []).map(l =>
    `<a href="${esc(l.url)}">${esc(l.label)}</a>`).join('');
  return `<li id="${esc(item.slug)}">
    <div class="news-date">${fmtDate(item.date)}</div>
    <div class="news-body">
      <h3><a href="${base}news/${esc(item.slug)}/">${esc(item.title)}</a>${
        item.category ? `<span class="tag">${esc(item.category)}</span>` : ''}</h3>
      <p>${esc(item.summary)}</p>
      ${item.body ? `<div class="extra">${item.body}</div>` : ''}
      ${links ? `<div class="linkrow">${links}</div>` : ''}
    </div>
  </li>`;
}

async function renderNews() {
  const news = await load('news');
  const items = published(news.items);
  const cats = [...new Set(items.map(i => i.category).filter(Boolean))].sort();

  el('#news').innerHTML = `<div class="wrap">
    <div class="eyebrow">Updates</div>
    <h1>News</h1>
    <p class="lede" style="max-width:60ch">Publications, awards, funding and group news. Items are
      also distributed via our <a href="${window.PEARL_BASE || ''}feed.xml">RSS feed</a> and on
      <a href="${esc((DATA.site && DATA.site.links.linkedin) || '#')}">LinkedIn</a>.</p>
    <div class="filters" id="news-filters">
      <button aria-pressed="true" data-cat="">All</button>
      ${cats.map(c => `<button aria-pressed="false" data-cat="${esc(c)}">${esc(c)}</button>`).join('')}
    </div>
    <ul class="news-list" id="news-items">${items.map(newsRow).join('')}</ul>
  </div>`;

  el('#news-filters').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const cat = btn.dataset.cat;
    [...el('#news-filters').children].forEach(b =>
      b.setAttribute('aria-pressed', String(b === btn)));
    el('#news-items').innerHTML =
      items.filter(i => !cat || i.category === cat).map(newsRow).join('');
  });

  if (location.hash) {
    const t = document.getElementById(location.hash.slice(1));
    if (t) t.scrollIntoView();
  }
}

/* ---------- research ---------- */

async function renderResearch() {
  const [research, pubs, sponsors] = await Promise.all(
    [load('research'), load('publications'), load('sponsors')]);
  const band = el('#sponsors');
  if (band) band.innerHTML = renderSponsors(sponsors);

  el('#research').innerHTML = `<div class="wrap">
    <div class="eyebrow">Research</div>
    <h1>Research program</h1>
    <p class="lede" style="max-width:66ch">${esc(research.intro)}</p>
    ${research.thrusts.map(t => {
      const related = pubs.items.filter(p => p.topic === t.id).slice(0, 4);
      return `<section id="${esc(t.id)}" style="border:0;padding:44px 0 0">
        <h2>${esc(t.title)}</h2>
        ${t.stake ? `<p class="stake big">${esc(t.stake)}</p>` : ''}
        <p style="max-width:66ch">${esc(t.blurb)}</p>
        <div class="grid two">
          <div class="card">
            <h3>Current work</h3>
            <ul>${(t.highlights || []).map(h => `<li>${esc(h)}</li>`).join('')}</ul>
          </div>
          ${related.length ? `<div class="card">
            <h3>Selected papers</h3>
            <ul>${related.map(p => `<li>${esc(p.title)} <em>(${esc(p.venue)}, ${p.year})</em></li>`).join('')}</ul>
          </div>` : ''}
        </div>
      </section>`;
    }).join('')}
    ${research.closing ? `<p class="closing" style="margin-top:48px">${esc(research.closing)}</p>` : ''}
  </div>`;
}

/* ---------- people ---------- */

function personCard(p) {
  const nameHtml = p.url ? `<a href="${esc(p.url)}">${esc(p.name)}</a>` : esc(p.name);
  return `<div class="person">
    <div class="avatar" aria-hidden="true">${esc(initials(p.name))}</div>
    <div>
      <div class="name">${nameHtml}</div>
      <div class="role">${esc(p.role)}${p.expected ? ` &middot; expected ${esc(p.expected)}` : ''}</div>
      ${p.affiliation ? `<div class="role">${esc(p.affiliation)}</div>` : ''}
      ${p.topic ? `<div class="topic">${esc(p.topic)}</div>` : ''}
      ${p.note ? `<div class="note">${esc(p.note)}</div>` : ''}
    </div>
  </div>`;
}

async function renderPeople() {
  const people = await load('people');

  const alumni = [...people.alumni].sort((a, b) =>
    (b.year || 0) - (a.year || 0) || a.name.localeCompare(b.name));

  el('#people').innerHTML = `<div class="wrap">
    <div class="eyebrow">People</div>
    <h1>Members</h1>
    ${people.groups.map(g => `<section style="border:0;padding:34px 0 0">
      <h2>${esc(g.title)}</h2>
      ${g.note ? `<p style="color:var(--muted);font-size:.95rem">${esc(g.note)}</p>` : ''}
      <div class="people">${g.members.map(personCard).join('')}</div>
    </section>`).join('')}

    <section style="border:0;padding:44px 0 0">
      <h2>Alumni</h2>
      <ul class="alumni-list">
        ${alumni.map(a => `<li>
          ${a.url ? `<a href="${esc(a.url)}">${esc(a.name)}</a>` : esc(a.name)},
          ${esc(a.degree)} <span class="yr">${esc(a.year)}</span>
          ${a.thesis ? `<span class="th">${esc(a.thesis)}</span>` : ''}
          ${a.topic ? `<span class="th">${esc(a.topic)}</span>` : ''}
          ${a.next ? `<span class="th">Now: ${esc(a.next)}</span>` : ''}
        </li>`).join('')}
      </ul>
      ${people.alumni_note ? `<p style="margin-top:20px;font-size:.92rem;color:var(--muted)">${people.alumni_note}</p>` : ''}
    </section>

    <section style="border:0;padding:44px 0 0">
      <div class="callout">
        <p><strong>Prospective students.</strong> Doctoral students are admitted through the
        Virginia Tech <a href="https://website.cs.vt.edu/academic/graduate.html">Computer Science</a>
        and <a href="https://ece.vt.edu/grad.html">Electrical and Computer Engineering</a> graduate
        programs. Undergraduate researchers are supervised throughout the academic year.
        Enquiries, accompanied by a curriculum vitae and a brief statement of research interests,
        may be addressed to <a href="mailto:dsn@vt.edu">dsn@vt.edu</a>.</p>
      </div>
    </section>
  </div>`;
}

/* ---------- publications ---------- */

async function renderPublications() {
  const [pubs, research] = await Promise.all([load('publications'), load('research')]);
  const topics = Object.fromEntries(research.thrusts.map(t => [t.id, t.title]));
  const all = [...pubs.items].sort((a, b) => b.year - a.year || a.title.localeCompare(b.title));

  function list(items) {
    let out = '', year = null;
    for (const p of items) {
      if (p.year !== year) { year = p.year; out += `<h2 class="pub-year">${year}</h2>`; }
      out += `<div class="pub">
        <div class="t">${p.url ? `<a href="${esc(p.url)}">${esc(p.title)}</a>` : esc(p.title)}</div>
        <div class="a">${esc(p.authors)}</div>
        <div class="v">${esc(p.venue)}${p.topic && topics[p.topic] ? ` &middot; ${esc(topics[p.topic])}` : ''}</div>
      </div>`;
    }
    return out;
  }

  el('#publications').innerHTML = `<div class="wrap">
    <div class="eyebrow">Publications</div>
    <h1>Selected publications</h1>
    <div class="filters" id="pub-filters">
      <button aria-pressed="true" data-topic="">All</button>
      ${research.thrusts.map(t => `<button aria-pressed="false" data-topic="${esc(t.id)}">${esc(t.title)}</button>`).join('')}
    </div>
    <div id="pub-items">${list(all)}</div>
    ${pubs.note ? `<p style="margin-top:28px;font-size:.92rem;color:var(--muted)">${pubs.note}</p>` : ''}
  </div>`;

  el('#pub-filters').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const topic = btn.dataset.topic;
    [...el('#pub-filters').children].forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    el('#pub-items').innerHTML = list(all.filter(p => !topic || p.topic === topic));
  });
}

/* ---------- boot ---------- */

/* News permalink pages under /news/<slug>/ are pre-rendered by scripts/build.py.
   They only need the shared header and footer, not a page renderer. */
async function bootChrome(current) {
  try {
    await renderChrome(current);
  } catch (err) {
    console.error(err);
  }
}

async function boot(page) {
  try {
    await renderChrome(page);
    if (page === 'index.html') await renderHome();
    else if (page === 'news.html') await renderNews();
    else if (page === 'research.html') await renderResearch();
    else if (page === 'people.html') await renderPeople();
    else if (page === 'publications.html') await renderPublications();
  } catch (err) {
    console.error(err);
    const main = el('main');
    if (main) {
      main.innerHTML = `<div class="wrap" style="padding:60px 0">
        <h1>Something went wrong loading this page</h1>
        <p class="callout">${esc(err.message)}<br><br>
        If you are previewing locally, serve the folder over HTTP
        (<code>python3 -m http.server</code>) rather than opening the file directly.
        Browsers block <code>fetch()</code> on <code>file://</code> URLs.</p>
      </div>`;
    }
  }
}
