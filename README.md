# stefanisofija.com

Portfolio site for **Stefani Sofija — Hochzeitsfotografie**, hosted on GitHub
Pages (`theWHYKINGS/stefanisofijaphotography`, target domain `www.stefanisofija.com`).

Like the other WHYKINGS sites, it's built from a **Claude Design** project and
hosted as the live source (client-rendered `index.html` + `support.js`).

```bash
python3 scripts/unpack_code.py      # newest ~/Downloads/ss_code*.json -> index.html
scripts/deploy.sh "what changed"    # post-process + commit + push + Pages build
```

Full protocol and open go-live items: [`scripts/pull-from-design.md`](scripts/pull-from-design.md).
