#!/usr/bin/env python3
"""build_legal.py — turn src/legal/*.html into self-contained pages under legal/.

Inlines legal.css (no extra request) and highlights any [[PLATZHALTER]] still in
the text, so a missing Impressum detail is impossible to overlook. Exits 1 while
placeholders remain unless --allow-placeholders is passed (deploy.sh does that
until Stefani's details are in — see scripts/pull-from-design.md).

    python3 scripts/build_legal.py [--allow-placeholders]
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
css = (root / "src/legal/legal.css").read_text(encoding="utf-8")
style_block = f"<style>\n{css}\n</style>"

missing = set()
for name in ("Impressum.html", "Datenschutz.html"):
    html = (root / "src/legal" / name).read_text(encoding="utf-8")
    html, n = re.subn(r'<link[^>]*href="legal\.css"[^>]*>', lambda m: style_block, html)
    if n != 1:
        print(f"  ! {name}: expected exactly one legal.css <link>, found {n}")
    found = re.findall(r"\[\[([A-Z_]+)\]\]", html)
    missing.update(found)
    html = re.sub(r"\[\[([A-Z_]+)\]\]", r'<span class="todo">[\1]</span>', html)
    out = root / "legal" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"✓ legal/{name}" + (f"  ⚠ placeholders: {', '.join(sorted(set(found)))}" if found else ""))

if missing and "--allow-placeholders" not in sys.argv:
    raise SystemExit("✗ legal pages still contain placeholders: " + ", ".join(sorted(missing)))
