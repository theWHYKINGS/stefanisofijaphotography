#!/usr/bin/env bash
#
# deploy.sh — post-process the freshly pulled design and publish it to
# GitHub Pages (github.com/theWHYKINGS/stefanisofijaphotography →
# https://www.stefanisofijaphotography.com).
#
# Usage:
#   scripts/deploy.sh                 # timestamped commit message
#   scripts/deploy.sh "Neue Fotos"    # custom message
#
# The *pull* half (Claude Design → ~/Downloads/ss_code.json → unpack_code.py)
# is done by Claude via the browser — see scripts/pull-from-design.md.

set -euo pipefail

cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"   # local gh install
REPO="theWHYKINGS/stefanisofijaphotography"

MSG="${1:-Update site — $(date '+%Y-%m-%d %H:%M')}"

# --- post-process the fresh source (all idempotent) ---
echo "Pointing fonts, photos + React/Babel at local copies…"
python3 scripts/localize_assets.py
echo "Building legal pages…"
python3 scripts/build_legal.py
echo "Injecting title / meta / enhance.js / footer legal links…"
python3 scripts/inject_head.py

if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing changed — working tree is clean. Nothing to deploy."
  exit 0
fi

git add -A
git status --short
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

echo "Pushing to GitHub…"
git push -q origin main

# Pages doesn't reliably queue a build on push for these repos — ask for one.
gh api -X POST "repos/$REPO/pages/builds" --jq '.status' || \
  echo "  ! could not request a build — check https://github.com/$REPO/settings/pages"

echo
echo "✅ Pushed. GitHub Pages will rebuild in ~1 minute."
echo "   Live:  https://www.stefanisofijaphotography.com"
