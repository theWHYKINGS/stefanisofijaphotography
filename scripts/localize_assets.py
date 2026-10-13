#!/usr/bin/env python3
"""localize_assets.py — point the pulled source at locally hosted assets.

The Claude Design source pulls from three third parties, each of which would
send the visitor's IP elsewhere (GDPR) or break later:

  * index.html : Google Fonts <link> (Inter)  -> removed. The design sets
                 'Helvetica Neue', Helvetica, Arial everywhere, so Inter is
                 never actually used; dropping it changes nothing visually.
  * index.html : photos hotlinked from onecdn.io (the CDN of Stefani's old
                 onepage.io site — gone once that account ends)
                 -> assets/photos/*.jpg (committed)
  * support.js : React / ReactDOM / Babel from unpkg.com -> vendor/*.js
                 (byte-identical copies; React's SRI hashes still match)

Idempotent — deploy.sh runs it after every pull.

NEW PHOTO in the design? Its onecdn URL shows up as "unknown onecdn image"
below: download it into assets/photos/<name>.jpg and add it to PHOTOS.
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent

UNPKG = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js": "vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js": "vendor/react-dom.production.min.js",
    "https://unpkg.com/@babel/standalone@7.26.4/babel.min.js": "vendor/babel.min.js",
}

PHOTOS = {
    "8c41d0ba-4632-49e2-88dc-24502a210f77": "first-look",
    "98f2c170-86c4-43a1-9044-abee539aeb8c": "zeremonie",
    "56430bc1-0d04-4d8f-9c94-f147073a6952": "portrait",
    "d5e2c810-20fa-49ec-a5b6-ffbe17ce7ab3": "schwarz-weiss",
    "33acf690-dc24-4c66-a7df-16b852fb79c3": "paar",
    "0714e5d7-19ab-4a1d-964e-00f631d0e094": "feier",
    "5208f1d2-728a-4806-8f14-ed007ced8168": "goldene-stunde",
    "034f2b76-3201-4cae-80e5-2d20d0347675": "momente",
    "d1cfe4fc-b2c4-4e23-bd16-7df2e0c72f0e": "liebe",
}

changed = []
problems = []

# --- index.html: fonts + photos ---
idx = root / "index.html"
html = before = idx.read_text(encoding="utf-8")
html = re.sub(r'\s*<link[^>]*href="https://fonts\.g(?:oogleapis|static)\.com[^"]*"[^>]*>', "", html)
if html != before:
    changed.append("Google Fonts removed")


def photo(m):
    name = PHOTOS.get(m.group(1))
    if not name:
        problems.append(f"unknown onecdn image: {m.group(0)}")
        return m.group(0)
    if not (root / f"assets/photos/{name}.jpg").exists():
        problems.append(f"missing file assets/photos/{name}.jpg")
    return f"assets/photos/{name}.jpg"


n_before = html
html = re.sub(r"https://onecdn\.io/media/([0-9a-f-]{36})/full", photo, html)
if html != n_before:
    changed.append("photos → assets/photos/")
idx.write_text(html, encoding="utf-8")

for host in ("fonts.googleapis", "fonts.gstatic", "onecdn.io", "unpkg.com"):
    if host in html:
        problems.append(f"index.html still references {host}")

# --- support.js: React/ReactDOM/Babel ---
support = root / "support.js"
s = before = support.read_text(encoding="utf-8")
for url, rel in UNPKG.items():
    s = s.replace(url, rel)
if s != before:
    support.write_text(s, encoding="utf-8")
    changed.append("support.js → vendor/")
for u in re.findall(r"https://unpkg\.com/[^\"'\s)]+", s):
    problems.append(f"support.js still points at an unknown CDN file: {u} (version bump? re-vendor it)")

print("✓ localize_assets: " + (", ".join(changed) if changed else "already local"))
for p in problems:
    print("  ! " + p)
raise SystemExit(1 if problems else 0)
