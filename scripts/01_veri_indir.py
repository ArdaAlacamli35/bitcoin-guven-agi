"""Ham veriyi SNAP'ten indirir ve bütünlüğünü doğrular.

Kaynak: Stanford Network Analysis Project (SNAP), soc-sign-bitcoin-otc
https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html
Biçim: SOURCE,TARGET,RATING,TIME  (RATING: -10..+10, TIME: Unix saniye)

Çalıştırma:  python scripts/01_veri_indir.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz"
ROOT = Path(__file__).resolve().parents[1]
OUT_GZ = ROOT / "data" / "raw" / "soc-sign-bitcoinotc.csv.gz"
OUT_META = ROOT / "data" / "raw" / "indirme_bilgisi.json"


def main() -> int:
    OUT_GZ.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "bitcoin-guven-agi ders projesi"})
    with urllib.request.urlopen(req, timeout=60) as r:
        blob = r.read()
    OUT_GZ.write_bytes(blob)

    rows = gzip.decompress(blob).decode("utf-8").strip().splitlines()
    bad = [i for i, line in enumerate(rows) if len(line.split(",")) != 4]
    if bad:
        print(f"Hatalı satır: {len(bad)}", file=sys.stderr)
        return 1

    meta = {
        "kaynak": URL,
        "indirme_zamani_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "satir_sayisi": len(rows),
    }
    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
