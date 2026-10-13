# Pulling the latest from Claude Design (Stefani Sofija)

Claude does this through the authenticated browser session (Claude-in-Chrome),
because the Claude Design API needs the claude.ai login. You just say
**"deploy stefanisofija"**.

## Project

- **Project ID:** `8f5c0dc9-f88a-4a48-aaf9-c76a8bda0bc7`
- **Entry file:** the single top-level `*.dc.html` (as of 2026-10-13:
  `Stefani Sofija.dc.html`) → published as `index.html`. Detected dynamically.
- **Deps:** just `support.js`. `uploads/` only holds two reference screenshots
  of the old site — not used by the page.
- **API base:** `https://claude.ai/design/anthropic.omelette.api.v1alpha.OmeletteService/`
- **Bundle prefix:** `ss_` (`wk_` main site, `ak_` Academy, `cm_` CMON, `sm_` Spielmäuse)

## Pull (in an open claude.ai tab)

```js
const PID = '8f5c0dc9-f88a-4a48-aaf9-c76a8bda0bc7';
const BASE = 'https://claude.ai/design/anthropic.omelette.api.v1alpha.OmeletteService/';
const call = async (m, b) => (await fetch(BASE + m, { method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Connect-Protocol-Version': '1' },
  credentials: 'include', body: JSON.stringify({ projectId: PID, ...b }) })).json();

const list = await call('ListFiles', {});
const entry = list.entries.filter(e => e.type === 'file' && e.path.endsWith('.dc.html'));
// exactly one expected — otherwise stop and ask which is canonical
const files = {};
for (const p of [entry[0].path, 'support.js'])   // + any new *.js the source references
  files[p] = (await call('GetFile', { path: p })).content;
const a = document.createElement('a');
a.href = URL.createObjectURL(new Blob([JSON.stringify({ files })], { type: 'application/json' }));
a.download = 'ss_code.json'; a.click();
```

(The tool output filter blocks file contents returned inline — always go via
the download.)

## Then, locally

```bash
python3 scripts/unpack_code.py          # newest ~/Downloads/ss_code*.json -> index.html + support.js
scripts/deploy.sh "what changed"        # localize + legal + head → commit → push → Pages build
```

## Post-processing (deploy.sh, all idempotent)

- `localize_assets.py` — removes the (unused) Google Fonts link, rewrites the
  photos from `onecdn.io` (old onepage.io CDN — will disappear) to
  `assets/photos/*.jpg`, and unpkg React/Babel → `vendor/`. **Zero third-party
  requests** remain. A **new photo** in the design shows up as
  "unknown onecdn image": download it to `assets/photos/<name>.jpg` (resize to
  ≤2048px, e.g. `sips -Z 2048`) and add its id to `PHOTOS`. If Stefani uploads
  photos directly into the Design project instead, pull them from `uploads/`.
- `build_legal.py` — `src/legal/*.html` → `legal/` (CSS inlined). Highlights
  `[[PLATZHALTER]]` in yellow; fails without `--allow-placeholders`.
- `inject_head.py` — `lang="de"`, title/meta/OG/favicon, `<script src="enhance.js">`,
  Impressum/Datenschutz links in the footer.

`enhance.js` (repo-owned, survives pulls): sends the contact form via
Web3Forms (capture-phase click on "Abschicken", validates Vorname + E-Mail,
then lets React show the design's "Danke" state) and adds the mobile layout
(the design is desktop-only). Config at the top: `CONTACT_EMAIL`, `WEB3FORMS_KEY`.

## Status (2026-10-13)

- Impressum/Datenschutz filled: Ossiacher Str. 16, 80687 München,
  stefanisofijaphotography@gmail.com, Kleinunternehmerin § 19 UStG, no phone
  (the contact form serves as the second fast contact channel).
- Domain = **www.stefanisofijaphotography.com** (NOT stefanisofija.com), DNS at
  all-inkl (ns5/ns6.kasserver.com): `www` CNAME → `theWHYKINGS.github.io.`,
  apex A → 185.199.108.153 / .109 / .110 / .111. `CNAME` file in repo.
- Web3Forms key set 2026-10-13 (created with stefanisofijaphotography@gmail.com).
- HTTPS: if "Enforce HTTPS" is greyed out after a DNS change, GitHub still has
  the old IP cached (all-inkl TTL = 2 h). Wait, then remove + re-add the custom
  domain in Settings → Pages to retrigger the Let's Encrypt certificate.
