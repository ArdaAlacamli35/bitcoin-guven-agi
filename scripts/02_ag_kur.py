"""Ham kenar listesinden yönlü, işaretli ve ağırlıklı ağı kurar.

Kararlar (raporda gerekçeleriyle):
- Düğüm: Bitcoin OTC platformundaki bir kullanıcı. SNAP kimlikleri zaten anonimdir; yine de
  yayımlanan dosyalarda kimlikler tuzlu SHA-256 ile yeniden adlandırılır (ör. K3f9a1c).
- Kenar: A -> B, "A, B'ye bir güven puanı verdi". Yön korunur (puan tek taraflıdır).
- Ağırlık: puan (-10..+10). İşaret: puan > 0 ise +1 (güven), < 0 ise -1 (güvensizlik).
- Aynı yönde tekrar eden puan yoktur (doğrulanır); varsa en son puan alınırdı.

Çıktılar: data/processed/kenarlar.csv, data/processed/ag.graphml
Çalıştırma: python scripts/02_ag_kur.py   (ANON_TUZ ortam değişkeni ile tuz verilebilir)
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "data" / "processed"
TUZ = os.environ.get("ANON_TUZ", "bva-sosyal-ag-2026")


def anon(uid: int) -> str:
    return "K" + hashlib.sha256(f"{TUZ}:{uid}".encode()).hexdigest()[:7]


def main() -> None:
    df = pd.read_csv(RAW, header=None, names=["kaynak", "hedef", "puan", "zaman"])
    assert df["puan"].between(-10, 10).all() and (df["puan"] != 0).all()
    assert not df.duplicated(["kaynak", "hedef"]).any(), "Aynı yönde tekrar eden puan var"
    assert (df["kaynak"] != df["hedef"]).all(), "Kendine puan var"

    ids = pd.unique(df[["kaynak", "hedef"]].values.ravel())
    mapping = {int(u): anon(int(u)) for u in ids}
    assert len(set(mapping.values())) == len(mapping), "Hash çakışması"

    df["kaynak"] = df["kaynak"].map(mapping)
    df["hedef"] = df["hedef"].map(mapping)
    df["isaret"] = (df["puan"] > 0).astype(int) * 2 - 1
    df["tarih"] = pd.to_datetime(df["zaman"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    df = df.sort_values("zaman").drop(columns="zaman")

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "kenarlar.csv", index=False)

    G = nx.DiGraph()
    for r in df.itertuples(index=False):
        G.add_edge(r.kaynak, r.hedef, puan=int(r.puan), isaret=int(r.isaret), tarih=r.tarih)
    nx.write_graphml(G, OUT / "ag.graphml")
    print(f"{G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar yazıldı.")


if __name__ == "__main__":
    main()
