#!/usr/bin/env python3
"""inject_head.py — add the bits the Claude Design source doesn't carry.

index.html is regenerated from Claude Design on every pull, so anything added
by hand is wiped. This re-applies it idempotently:

  * <html lang="de">
  * <title> + meta description + canonical + og tags + favicon
  * <script src="enhance.js"> (contact form delivery + mobile layout)
  * Impressum / Datenschutz links in the footer (the design has none)

    python3 scripts/inject_head.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
idx = root / "index.html"
html = idx.read_text(encoding="utf-8")

TITLE = "Stefani Sofija — Hochzeitsfotografie"
DESC = ("Hochzeitsfotografie von Stefani Sofija: ehrlich, ruhig und nah an euch. "
        "Reduzierte, zeitlose Bilder von den echten Momenten eures Tages.")
URL = "https://www.stefanisofijaphotography.com/"

HEAD = f"""<title>{TITLE}</title>
<meta name="description" content="{DESC}" />
<link rel="canonical" href="{URL}" />
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{TITLE}" />
<meta property="og:description" content="{DESC}" />
<meta property="og:url" content="{URL}" />
<meta property="og:image" content="{URL}assets/photos/first-look.jpg" />
<meta property="og:locale" content="de_DE" />
<meta name="twitter:card" content="summary_large_image" />
<script src="enhance.js" defer></script>
"""

changed = []

if not re.search(r"<html[^>]*\blang=", html):
    html = re.sub(r"<html\b", '<html lang="de"', html, count=1)
    changed.append('lang="de"')

BEGIN, END = "<!-- injected-head:begin -->", "<!-- injected-head:end -->"
block = f"{BEGIN}\n{HEAD}{END}\n"
if BEGIN in html:
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", lambda m: block, html, flags=re.S)
else:
    i = html.find("<head>")
    if i == -1:
        raise SystemExit("ERROR: no <head> found in index.html")
    html = html[: i + len("<head>")] + "\n" + block + html[i + len("<head>"):]
    changed.append("head block")

# Footer: append the legal links right after the design's footer tagline.
LEGAL = ('<span class="ss-legal" style="font-size:10.5px; letter-spacing:0.14em; color:#aaa; '
         'text-transform:uppercase; display:flex; gap:18px;">'
         '<a href="legal/Impressum.html">Impressum</a><a href="legal/Datenschutz.html">Datenschutz</a></span>')
if 'class="ss-legal"' not in html:
    new, n = re.subn(r"(Hochzeitsfotografie</span>)(\s*</footer>)", lambda m: m.group(1) + "\n    " + LEGAL + m.group(2), html, count=1)
    if n:
        html = new
        changed.append("footer legal links")
    else:
        print("  ! footer tagline not found — legal links NOT injected (footer changed in the design?)")

idx.write_text(html, encoding="utf-8")
print("✓ inject_head: " + (", ".join(changed) if changed else "already up to date"))
