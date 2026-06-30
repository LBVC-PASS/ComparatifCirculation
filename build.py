#!/usr/bin/env python3
"""Synchronise les blocs JSON embarqués dans index.html avec les fichiers source.

L'application charge en priorité taxonomie.json et articles.json via fetch().
Quand la page est ouverte en local (file://), fetch() échoue : elle se rabat
alors sur des copies embarquées dans index.html. Ce script régénère ces copies
pour qu'elles ne se désynchronisent jamais à la main.

Usage : python3 build.py   (aucune dépendance, bibliothèque standard uniquement)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"

# (id du <script>, fichier source)
BLOCKS = [
    ("emb-tax", "taxonomie.json"),
    ("emb-art", "articles.json"),
]


def main() -> int:
    html = HTML.read_text(encoding="utf-8")
    for block_id, fname in BLOCKS:
        data = json.loads((ROOT / fname).read_text(encoding="utf-8"))
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        pattern = re.compile(
            r'(<script id="' + re.escape(block_id) + r'"[^>]*>)(.*?)(</script>)',
            re.DOTALL,
        )
        if not pattern.search(html):
            print(f"!! bloc #{block_id} introuvable dans index.html", file=sys.stderr)
            return 1
        html = pattern.sub(lambda m: m.group(1) + payload + m.group(3), html, count=1)
        print(f"ok  #{block_id} <- {fname}")
    HTML.write_text(html, encoding="utf-8")
    print("index.html mis à jour.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
