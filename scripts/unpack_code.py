#!/usr/bin/env python3
"""unpack_code.py — decode an ss_code.json bundle (source HTML + support.js)
pulled from the Claude Design "Stefani Sofija" project into the repo.

Same "build from live source" path as the other WHYKINGS sites: the page is
hosted as its Claude Design source (client-rendered) plus its dependencies.
The single top-level *.dc.html entry is written as index.html.

    python3 scripts/unpack_code.py [path/to/ss_code.json]
    (defaults to the newest ~/Downloads/ss_code*.json)
"""
import base64
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# Chrome saves repeat downloads as "ss_code (1).json", … → take the NEWEST.
if len(sys.argv) > 1:
    src = Path(sys.argv[1])
else:
    matches = sorted(Path.home().glob("Downloads/ss_code*.json"), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise SystemExit("No ss_code*.json found in ~/Downloads")
    src = matches[-1]
print(f"reading {src.name}")

data = json.loads(src.read_text(encoding="utf-8"))
files = data.get("files", data)  # {"files": {path: base64}} (current) or flat

# Do NOT hardcode the entry name — Claude Design files get renamed.
entries = [p for p in files if p.lower().endswith(".dc.html") and "/" not in p]
if len(entries) != 1:
    raise SystemExit(f"Expected exactly one top-level .dc.html in the bundle, got: {entries}")
RENAME = {entries[0]: "index.html"}
print(f"entry: {entries[0]} -> index.html")

count = 0
for rel, b64 in files.items():
    if isinstance(b64, dict):
        b64 = b64["content"]
    dest = (root / RENAME.get(rel, rel)).resolve()
    if root not in dest.parents:
        print(f"  ! skipped (outside repo): {rel}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(b64))
    count += 1
print(f"✓ wrote {count} code files (source -> index.html)")
