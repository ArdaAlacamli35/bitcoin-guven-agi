"""Etkileşimli ağ verisi (web/ag.json) ve A3 statik poster (poster/poster_A3.pdf) üretir.

Filtre kararı: 5.881 düğümün tamamı ekranda okunmaz bir yumağa dönüşür. Bu yüzden
- derecesi en az 20 olan düğümler (ağın omurgası) ve
- negatif kenar yoğunluğu yüksek (z > 2) topluluklardaki, derecesi en az 8 olan düğümler
gösterilir. İkinci kural, araştırma sorusunun odağı olan güvensizlik kümelerinin
filtrede kaybolmaması içindir. Bu bir yanlılıktır ve raporda belirtilir.

Önce analiz.ipynb çalıştırılmalıdır (results/ klasörünü üretir).
"""
from __future__ import annotations

import json
from pathlib import Path

import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
mer = pd.read_csv(ROOT / "results" / "dugum_olculeri.csv", index_col=0)
top = pd.read_csv(ROOT / "results" / "topluluklar.csv", index_col=0)
ken = pd.read_csv(ROOT / "data" / "processed" / "kenarlar.csv")

catisma = set(top.index[(top["neg_z"] > 2) & (top["ic_kenar"] >= 30)])
secili = mer.index[(mer["derece"] >= 20) | (mer["topluluk"].isin(catisma) & (mer["derece"] >= 8))]
secili = set(secili)
e = ken[ken["kaynak"].isin(secili) & ken["hedef"].isin(secili)].copy()

# Yönsüz çizim için çiftleri birleştir: işaret = puan toplamının işareti
e["a"] = np.where(e["kaynak"] < e["hedef"], e["kaynak"], e["hedef"])
e["b"] = np.where(e["kaynak"] < e["hedef"], e["hedef"], e["kaynak"])
pairs = e.groupby(["a", "b"])["puan"].agg(["sum", "count"]).reset_index()
pairs = pairs[pairs["sum"] != 0]

nodes = sorted(set(pairs["a"]) | set(pairs["b"]))
idx = {v: i for i, v in enumerate(nodes)}
g = ig.Graph(n=len(nodes), edges=[(idx[a], idx[b]) for a, b in zip(pairs["a"], pairs["b"])])
# Yerleşim: yalnızca pozitif kenarlar çeker (güven = yakınlık), negatifler yerleşimi etkilemez.
w = [1.0 if s > 0 else 0.05 for s in pairs["sum"]]
np.random.seed(SEED)
import random
random.seed(SEED)
lay = g.layout_fruchterman_reingold(weights=w, niter=1500, seed=None)
xy = np.array(lay.coords)
xy = (xy - xy.mean(0)) / xy.std(0)

# Renkler: büyük topluluklar için ayırt edilebilir palet; çatışma kümeleri sıcak tonlarda.
PALET = ["#4e79a7", "#59a14f", "#76b7b2", "#9c755f", "#b07aa1", "#edc948", "#86bcb6", "#d37295", "#e15759", "#f28e2b", "#a0cbe8", "#8cd17d"]
renk = {}
soguk = iter([c for c in PALET if c not in ("#e15759", "#f28e2b", "#d37295")])
sicak = iter(["#e15759", "#f28e2b", "#d37295", "#ff9da7"])
for c in top.index:
    renk[c] = next(sicak) if c in catisma else next(soguk, "#8a8f98")
DIGER = "#5c6068"

def ad(c):
    return f"T{c} · {top.loc[c, 'ad']}" if c in top.index else "Diğer küçük topluluklar"

out_nodes = []
for v in nodes:
    r = mer.loc[v]
    c = int(r["topluluk"])
    out_nodes.append({
        "id": v, "x": round(float(xy[idx[v], 0]), 4), "y": round(float(xy[idx[v], 1]), 4),
        "c": c if c in top.index else -1,
        "d": int(r["derece"]), "gp": int(r["gelen_pozitif"]), "gn": int(r["gelen_negatif"]),
        "pr": round(float(r["pagerank"]) * 1000, 4), "prp": round(float(r["pr_pozitif"]) * 1000, 4),
        "prn": round(float(r["pr_negatif"]) * 1000, 4), "bt": round(float(r["betweenness"]), 6),
    })
out_edges = [[idx[a], idx[b], 1 if s > 0 else -1] for a, b, s in zip(pairs["a"], pairs["b"], pairs["sum"])]
communities = [{"id": int(c), "ad": ad(c), "renk": renk[c], "uye": int(top.loc[c, "uye"]),
                "ic_neg": round(float(top.loc[c, "ic_neg_oran"]), 4), "neg_z": round(float(top.loc[c, "neg_z"]), 2),
                "catisma": bool(c in catisma)} for c in top.index]
communities.append({"id": -1, "ad": "Diğer küçük topluluklar", "renk": DIGER, "uye": None, "ic_neg": None, "neg_z": None, "catisma": False})

web = ROOT / "web"
web.mkdir(exist_ok=True)
(web / "ag.json").write_text(json.dumps({
    "meta": {"toplam_dugum": int(len(mer)), "gosterilen_dugum": len(nodes), "gosterilen_kenar": len(out_edges),
             "filtre": "derece ≥ 20, ya da çatışma kümesinde derece ≥ 8"},
    "communities": communities, "nodes": out_nodes, "edges": out_edges,
}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"web/ag.json: {len(nodes)} düğüm, {len(out_edges)} kenar")

# ---------------- A3 poster ----------------
ozet = json.loads((ROOT / "results" / "ozet.json").read_text(encoding="utf-8"))
A3 = (16.54, 11.69)  # yatay, inç
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig = plt.figure(figsize=A3, facecolor="#121315")
ax = fig.add_axes([0.02, 0.04, 0.66, 0.84], facecolor="#121315")
ax.set_axis_off()

pos_e = [(idx[a], idx[b]) for a, b, s in zip(pairs["a"], pairs["b"], pairs["sum"]) if s > 0]
neg_e = [(idx[a], idx[b]) for a, b, s in zip(pairs["a"], pairs["b"], pairs["sum"]) if s < 0]
from matplotlib.collections import LineCollection
ax.add_collection(LineCollection([[xy[a], xy[b]] for a, b in pos_e], colors="#7f8ea3", linewidths=0.25, alpha=0.18, zorder=1))
ax.add_collection(LineCollection([[xy[a], xy[b]] for a, b in neg_e], colors="#ff7a1a", linewidths=0.6, alpha=0.65, zorder=2))
col = [renk.get(n["c"], DIGER) for n in out_nodes]
size = [6 + 2.2 * np.sqrt(n["d"]) ** 1.25 for n in out_nodes]
ax.scatter(xy[:, 0], xy[:, 1], s=size, c=col, edgecolors="#121315", linewidths=0.4, zorder=3)
ax.autoscale()

# Etiketler: her topluluğun merkezine kısa ad, en yüksek PageRank'li 6 düğüme anonim kimlik
for c in top.index:
    pts = np.array([xy[idx[n["id"]]] for n in out_nodes if n["c"] == c])
    if len(pts) < 8:
        continue
    cx, cy = np.median(pts, axis=0)
    ax.text(cx, cy, f"T{c}", color="white", fontsize=15, fontweight="bold", ha="center", va="center", zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", fc=renk[c], ec="none", alpha=0.9))
for n in sorted(out_nodes, key=lambda n: -n["pr"])[:6]:
    x, y = xy[idx[n["id"]]]
    ax.annotate(n["id"], (x, y), xytext=(8, 8), textcoords="offset points", color="#ededee", fontsize=9, zorder=6,
                arrowprops=dict(arrowstyle="-", color="#ededee", lw=0.6))

fig.text(0.02, 0.95, "Bitcoin OTC güven ağı dengeli: dengesiz üçgenler rastlantıya göre 2,7 kat az, güvensizlik üç kümede toplanıyor",
         color="#ededee", fontsize=16.5, fontweight="bold")
fig.text(0.02, 0.915, f"SNAP soc-sign-bitcoin-otc · {ozet['temel']['dugum']:,} kullanıcı, {ozet['temel']['kenar_yonlu']:,} puan (2010–2016) · "
         f"Gösterilen: {len(nodes)} düğüm (derece ≥ 20; çatışma kümelerinde ≥ 8) · Konum: pozitif kenarlarla Fruchterman–Reingold".replace(",", "."),
         color="#a3a6ad", fontsize=10.5)

# Sağ panel: lejant ve bulgular
lx = 0.70
fig.text(lx, 0.86, "Topluluklar (Leiden, renk)", color="#ededee", fontsize=13, fontweight="bold")
y = 0.83
for c in top.index:
    fig.patches.append(plt.Circle((lx + 0.007, y + 0.005), 0.0055, color=renk[c], transform=fig.transFigure, figure=fig))
    t = f"T{c}  {top.loc[c, 'ad']} · {int(top.loc[c, 'uye'])} üye · iç neg. %{top.loc[c, 'ic_neg_oran']*100:.0f}"
    fig.text(lx + 0.018, y, t, color="#ededee" if c in catisma else "#c8cad0", fontsize=8.6,
             fontweight="bold" if c in catisma else "normal")
    y -= 0.026
y -= 0.01
fig.legend(handles=[Line2D([0], [0], color="#7f8ea3", lw=2, label="Güven (pozitif puan)"),
                    Line2D([0], [0], color="#ff7a1a", lw=2, label="Güvensizlik (negatif puan)"),
                    Line2D([0], [0], marker="o", color="none", markerfacecolor="#a3a6ad", markersize=9, label="Düğüm boyutu = derece")],
           loc="upper left", bbox_to_anchor=(lx - 0.004, y), frameon=False, labelcolor="#ededee", fontsize=10)
y -= 0.11
d = ozet["denge"]; nk = ozet["negatif_kumelenme"]; nm = ozet["null_model"]
bul = [
    ("Yapısal denge", f"Üçgenlerin %{d['guclu_denge_orani']*100:.1f}'i dengeli; işaretler rastgele dağıtılsa %{d['null_guclu_ort']*100:.1f} olurdu (z = {d['z_guclu_denge']:.0f})."),
    ("'Düşmanımın düşmanı dostumdur'", f"+−− üçgen: {d['tipler']['+--']:,} gözlendi, rastlantıda {d['beklenen_tip']['+--']:,.0f} beklenirdi.".replace(",", ".")),
    ("Güvensizlik nerede?", f"Negatif puanların %{nk['neg_kenarlarin_toplulukar_arasi_payi']*100:.0f}'i topluluklar ARASINDA (pozitiflerde %{nk['poz_kenarlarin_toplulukar_arasi_payi']*100:.0f})."),
    ("Ama üç istisna var", "T7–T9'da iç negatif oranı %32–67; ağ geneli %10. T8'de negatiflerin %95'ini yalnızca 3 hesap vermiş."),
    ("Rastlantı değil", f"Modülerlik z = {nm['modularite']['z']:.0f}, kümelenme z = {nm['kumelenme']['z']:.0f} (100 derece korumalı rastgele ağ)."),
]
fig.text(lx, y, "Bulgular", color="#ededee", fontsize=13, fontweight="bold")
y -= 0.03
import textwrap
for b, t in bul:
    fig.text(lx, y, b, color="#f0b45e", fontsize=10.5, fontweight="bold"); y -= 0.022
    for line in textwrap.wrap(t, 62):
        fig.text(lx, y, line, color="#ededee", fontsize=9.8); y -= 0.02
    y -= 0.008
fig.text(lx, 0.035, "Arda Alaçamlı · Sosyal Ağ Analizi · MCBÜ Büyük Veri Analistliği · 2026\nKimlikler tuzlu SHA-256 ile anonimleştirilmiştir. Ağ verisi nedensellik göstermez.",
         color="#8a8f98", fontsize=8.5)
(ROOT / "poster").mkdir(exist_ok=True)
fig.savefig(ROOT / "poster" / "poster_A3.pdf", facecolor=fig.get_facecolor())
fig.savefig(ROOT / "poster" / "poster_A3_onizleme.png", dpi=80, facecolor=fig.get_facecolor())
print("poster/poster_A3.pdf yazıldı")
