"""Sunum (sunum/sunum.pdf): 10 slayt, her başlık bir bulgu cümlesi. Sayılar results/ klasöründen okunur."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
o = json.loads((ROOT / "results" / "ozet.json").read_text(encoding="utf-8"))
top = pd.read_csv(ROOT / "results" / "topluluklar.csv", index_col=0)


def n(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, d=1):
    return "%" + n(x * 100, d)


def img(name, h="100%"):
    b = base64.b64encode((ROOT / "figures" / name).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b}" style="max-height:{h};max-width:100%">'


t, ol, kp, pn, dg, tp, nk, nm, kr = (o[k] for k in
    ["temel", "olculer", "kuvvet_yasasi", "pozitif_negatif", "denge", "topluluk", "negatif_kumelenme", "null_model", "kirilganlik"])
tip, bek = dg["tipler"], dg["beklenen_tip"]
hub = kr["en_merkezi_silinince"]
kopan = kr["once"]["ana_bilesen"] - hub["ana_bilesen"] - 1


def ucgen(a, b, c, etiket, dengeli):
    # a, b, c: kenar işaretleri (üst-sol, üst-sağ, alt)
    col = lambda s: "#7cb8ff" if s == "+" else "#f0b45e"
    dash = lambda s: "" if s == "+" else 'stroke-dasharray="7 5"'
    return f"""<figure class="tri"><svg viewBox="0 0 160 140" width="150">
      <line x1="80" y1="18" x2="22" y2="118" stroke="{col(a)}" stroke-width="5" {dash(a)}/>
      <line x1="80" y1="18" x2="138" y2="118" stroke="{col(b)}" stroke-width="5" {dash(b)}/>
      <line x1="22" y1="118" x2="138" y2="118" stroke="{col(c)}" stroke-width="5" {dash(c)}/>
      <text x="40" y="66" fill="{col(a)}" font-size="22" font-weight="700">{a}</text>
      <text x="112" y="66" fill="{col(b)}" font-size="22" font-weight="700">{b}</text>
      <text x="74" y="138" fill="{col(c)}" font-size="22" font-weight="700">{c}</text>
      <circle cx="80" cy="18" r="10" fill="#ededee"/><circle cx="22" cy="118" r="10" fill="#ededee"/><circle cx="138" cy="118" r="10" fill="#ededee"/>
    </svg><figcaption><b class="{'ok' if dengeli else 'no'}">{'Dengeli' if dengeli else 'Dengesiz'}</b><br>{etiket}</figcaption></figure>"""


slides = []
S = lambda title, body, cls="": slides.append(f'<section class="slide {cls}"><h1>{title}</h1><div class="body">{body}</div></section>')

# 1 — Soru
slides.append(f"""<section class="slide kapak"><p class="ust">Sosyal Ağ Analizi · Arda Alaçamlı</p>
<h1>Bitcoin OTC'de güvensizlik rastgele dağılmıyor: ağ dengeli, ama üç küme kuralı bozuyor</h1>
<div class="soru"><p>Araştırma sorusu</p><ol><li>Güvensizlik (negatif) kenarları belirli kümelerde toplanıyor mu?</li><li>Ağ yapısal olarak "dengeli" mi?</li></ol></div>
<p class="alt">Veri: Stanford SNAP soc-sign-bitcoin-otc · 2010–2016</p></section>""")

# 2 — Veri ve ağ
S(f"{n(t['dugum'])} kullanıcı, {n(t['kenar_yonlu'])} puan: her 10 puandan 1'i güvensizlik", f"""
<div class="iki"><div><ul>
<li><b>Düğüm:</b> Platformdaki bir kullanıcı (anonim kimlik, ör. K28a80ce)</li>
<li><b>Kenar:</b> A → B = "A, B ile işlem yaptı ve ona puan verdi"</li>
<li><b>Yön korunur:</b> Puan tek taraflı bir yargıdır; çiftlerin {pct(t['karsilikli_oran'],0)}'i karşılıklı puanlaşmış</li>
<li><b>İşaret:</b> −10…−1 güvensizlik, +1…+10 güven</li>
<li><b>Örnekleme yok:</b> Ağın tamamı analiz edildi</li>
<li><b>Tekrarlanabilir:</b> İndir → anonimleştir → kenar listesi + GraphML (script), analiz SEED = 42</li></ul></div>
<div class="kutular"><div class="kutu"><b>{n(t['dugum'])}</b><span>kullanıcı</span></div><div class="kutu"><b>{n(t['kenar_yonlu'])}</b><span>yönlü puan</span></div>
<div class="kutu turuncu"><b>{pct(t['negatif_kenar_orani'],0)}</b><span>negatif puan</span></div><div class="kutu"><b>{n(ol['yogunluk']*1000,1)}‰</b><span>yoğunluk</span></div></div></div>""")

# 3 — Temel yapı + kırılganlık
S(f"Pazar tek parça, ama tek bir tüccara bağımlı: o hesap çıkarsa {n(kopan)} kişi kopuyor", f"""
<div class="iki"><div><table>
<tr><td>En büyük bileşen</td><td>{n(ol['en_buyuk_zayif_bilesen'])} / {n(t['dugum'])}</td></tr>
<tr><td>Ortalama en kısa yol · çap</td><td>{n(ol['ort_en_kisa_yol'],2)} · {ol['cap']}</td></tr>
<tr><td>Ortalama kümelenme</td><td>{n(ol['ort_kumelenme'],3)}</td></tr>
<tr><td>Derece benzeşimi</td><td>{n(ol['derece_benzesimi'],2)}</td></tr>
<tr><td>Derece dağılımı</td><td>ağır kuyruklu (α = {n(kp['alpha'],2)}); log-normal daha iyi uyuyor</td></tr></table>
<p class="not">Negatif benzeşim: Büyük tüccarlar küçük, yeni kullanıcılarla işlem yapıyor (göbek-jant yapısı).</p></div>
<div class="vurgu"><p class="buyuk">K28a80ce</p><p>Betweenness'ı en yüksek hesap (PageRank'te de 1.)</p>
<p>Çıkarılırsa ana bileşen <b>{n(kr['once']['ana_bilesen'])} → {n(hub['ana_bilesen'])}</b>, bileşen sayısı <b>{kr['once']['bilesen_sayisi']} → {hub['bilesen_sayisi']}</b>.</p>
<p>{n(kopan)} kullanıcının pazarla tek bağlantısı bu hesap: platform onlar hakkında başka kimsenin görüşünü bilmiyor.</p></div></div>""")

# 4 — Topluluklar + null model
S(f"Topluluklar rastlantı değil: modülerlik {n(nm['modularite']['gozlenen'],2)}, aynı dereceli rastgele ağlarda {n(nm['modularite']['null_ort'],2)}", f"""
<div class="tek">{img('null_model.png','330px')}</div>
<div class="uc"><p><b>Louvain</b> Q = {n(tp['louvain_modularite_ort'],3)} · <b>Leiden</b> Q = {n(tp['leiden_modularite_ort'],3)}</p>
<p><b>Kararlılık (10 tohum):</b> NMI {n(tp['louvain_nmi_ort'],2)} / {n(tp['leiden_nmi_ort'],2)}. Büyük gruplar sabit, sınırdaki kullanıcılar yer değiştiriyor.</p>
<p><b>100 rastgele ağ:</b> Kümelenme z = {n(nm['kumelenme']['z'],0)}, modülerlik z = {n(nm['modularite']['z'],0)}. Null model olmasaydı 0,49'un yüksek olduğunu söyleyemezdik.</p></div>""")

# 5 — Yöntem açıklaması
S("Yapısal denge: bir üçgendeki negatif kenar sayısı çiftse üçgen dengelidir", f"""
<div class="ucgenler">{ucgen('+','+','+','Dostumun dostu dostumdur',True)}{ucgen('+','−','−','Düşmanımın düşmanı dostumdur',True)}{ucgen('+','+','−','İki dostum birbirine düşman',False)}{ucgen('−','−','−','Herkes herkese düşman (zayıf dengede kabul)',False)}</div>
<p class="not orta">Test: Üçgenler sabit kalır, işaretler kenarlar arasında <b>1000 kez rastgele karıştırılır</b>. Gözlenen dengeli oran bu dağılımla karşılaştırılır.</p>""")

# 6 — Denge sonucu
S(f"Ağ dengeli: dengesiz üçgenler rastlantıdan {n(bek['++-']/tip['++-'],1)} kat az (z = {n(dg['z_guclu_denge'],0)})", f"""
<div class="tek">{img('yapisal_denge.png','330px')}</div>
<div class="uc"><p><b>{n(dg['ucgen'])}</b> üçgenin <b>{pct(dg['guclu_denge_orani'])}</b>'i dengeli; rastgele işaretlerle <b>{pct(dg['null_guclu_ort'])}</b>.</p>
<p><b>+−−</b> {n(tip['+--'])} gözlendi, {n(bek['+--'])} beklenirdi: Aynı kişiyi işaretleyenler birbirine güveniyor.</p>
<p><b>−−−</b> {n(tip['---']/bek['---'],1)} kat fazla: Birbirine düşman ikiden çok grup var (zayıf denge).</p></div>""")

# 7 — Negatif kümeler
c7, c8, c9 = top.loc[7], top.loc[8], top.loc[9]
S("Güvensizlik grupların arasında durur, ama T7–T9'da grubun içine yerleşmiş", f"""
<div class="iki"><div>{img('topluluk_negatif.png','360px')}</div><div>
<p>Negatif kenarların <b>{pct(nk['neg_kenarlarin_toplulukar_arasi_payi'],0)}</b>'i topluluklar arasında (pozitiflerde {pct(nk['poz_kenarlarin_toplulukar_arasi_payi'],0)}). İç negatif oranı rastgeleden düşük (z = {n(nk['z_ic_neg'],1)}).</p>
<p class="kume"><b>T7 · T8: Toplu işaretleme.</b> İç negatiflerin {pct(c7.ilk3_veren_payi,0)} / {pct(c8.ilk3_veren_payi,0)}'ini sadece 3 hesap vermiş. T8'de bu 3 hesap {int(c8.neg_alan)} farklı kişiyi işaretlemiş.</p>
<p class="kume"><b>T9: Karşılıklı −10 çatışması.</b> İç kenarların {pct(c9.ic_neg_oran,0)}'ü negatif, bunların {pct(c9.eksi10_payi,0)}'u en sert puan (−10). {int(c9.neg_veren)} kişi → {int(c9.neg_alan)} kişi, 2013.</p>
<p class="not">Canlı gösterim: Etkileşimli ağda T9'u filtrele → en çok güvensizlik toplayan hesabı aç.</p></div></div>""")

# 8 — Pozitif/negatif merkeziyet
S(f"İtibar ve güvensizlik ayrı şeyler: pozitif ve negatif PageRank neredeyse ilişkisiz (ρ = {n(pn['spearman_pr_pos_neg_aktif'],2)})", f"""
<div class="kutular genis"><div class="kutu"><b>ρ = {n(pn['spearman_pr_pos_neg_aktif'],2)}</b><span>en az 5 puan almış {n(pn['aktif_dugum'])} kullanıcıda pozitif ve negatif PageRank korelasyonu</span></div>
<div class="kutu"><b>{pn['ilk20_kesisim']} / 20</b><span>"en güvenilen 20" ile "en güvenilmeyen 20" listelerinin ortak kullanıcı sayısı</span></div>
<div class="kutu turuncu"><b>{pct(pn['negatif_kenarlarin_yuzde_kaci_ilk_yuzde5'],0)}</b><span>negatif puanların, kullanıcıların sadece %5'ine gidiyor</span></div></div>
<p class="not orta">Çıkarım: Tek bir "net puan" (pozitif − negatif) bu iki bilgiyi birbirine karıştırır. Bir itibar sistemi ikisini ayrı göstermeli.</p>""")

# 9 — Cevap
S("Cevap: Ağ dengeli, güvensizlik sınırlarda, ama üç küme ayrı ayrı incelenmeli", f"""
<div class="iki"><div class="vurgu"><p class="buyuk">Soru 2: Dengeli mi?</p><p><b>Evet.</b> Dengeli üçgen oranı {pct(dg['guclu_denge_orani'])}, rastgele {pct(dg['null_guclu_ort'])}; z = {n(dg['z_guclu_denge'],0)}. "Düşmanımın düşmanı dostumdur" rastlantıdan {n(tip['+--']/bek['+--'],1)} kat sık.</p></div>
<div class="vurgu turuncu"><p class="buyuk">Soru 1: Kümeleniyor mu?</p><p><b>Genelde hayır:</b> Güvensizlik toplulukların arasında. <b>Üç istisna:</b> T7–T8'de birkaç hesap çok kişiyi toplu işaretliyor, T9'da karşılıklı −10 çatışması var. İki farklı mekanizma, tek bir "negatif oran" ile ayırt edilemez.</p></div></div>""")

# 10 — Sınırlar
S("Sınırlar: Bu ağ kimin dolandırıcı olduğunu söylemez", """
<ul class="sinir">
<li><b>Nedensellik yok:</b> T7–T9'daki kullanıcıların dolandırıcı olduğu ya da işaretleyenlerin haklı olduğu bu veriden çıkarılamaz.</li>
<li><b>Eski veri:</b> 2010–2016, tek anlık görüntü; bugünkü kripto pazarını temsil etmez.</li>
<li><b>Yön kaybı:</b> Denge analizi yönsüz ağda yapıldı; 58 çelişkili çift çıkarıldı.</li>
<li><b>Topluluk tespiti işareti görmüyor:</b> İşaretli modülerlik T9'u bölebilirdi.</li>
<li><b>Kararlılık orta:</b> NMI ≈ 0,7; küçük topluluk sınırları kesin değil.</li>
<li><b>Görselleştirme filtresi:</b> 786 düğüm gösteriliyor (çatışma kümeleri bilinçli olarak dahil edildi). Hesapların hepsi tam ağda yapıldı.</li></ul>
<p class="alt">Kod, defter, rapor ve etkileşimli ağ: github.com/ArdaAlacamli35/bitcoin-guven-agi</p>""")

css = """
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "DejaVu Sans", sans-serif; }
.slide { width: 1280px; height: 720px; padding: 46px 60px; background: #121315; color: #ededee; page-break-after: always; position: relative; overflow: hidden; }
.slide h1 { font-size: 33px; line-height: 1.2; margin: 0 0 26px; letter-spacing: -0.5px; }
.kapak h1 { font-size: 48px; margin-top: 70px; max-width: 1050px; }
.ust { color: #f0b45e; font-weight: 700; margin: 0; font-size: 18px; }
.soru { margin-top: 40px; border-left: 5px solid #f0b45e; padding-left: 20px; font-size: 24px; }
.soru p { color: #a3a6ad; margin: 0 0 6px; font-size: 18px; } .soru ol { margin: 0; padding-left: 26px; }
.alt { position: absolute; bottom: 30px; left: 60px; color: #8a8f98; font-size: 16px; }
.body { font-size: 21px; line-height: 1.45; }
.iki { display: grid; grid-template-columns: 1.15fr 1fr; gap: 40px; align-items: start; }
ul { margin: 0; padding-left: 24px; } li { margin-bottom: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 20px; } td { border-bottom: 1px solid #2b2d31; padding: 9px 4px; } td:last-child { text-align: right; font-weight: 700; }
.not { color: #a3a6ad; font-size: 18px; margin-top: 14px; } .orta { text-align: center; margin-top: 26px; }
.vurgu { background: #1b1c1f; border: 1px solid #2b2d31; border-left: 5px solid #7cb8ff; border-radius: 8px; padding: 20px 24px; }
.vurgu.turuncu { border-left-color: #f0b45e; }
.vurgu p { margin: 0 0 12px; } .buyuk { font-size: 30px; font-weight: 800; font-family: "DejaVu Sans Mono", monospace; }
.kutular { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; } .kutular.genis { grid-template-columns: repeat(3, 1fr); margin-top: 20px; }
.kutu { background: #1b1c1f; border: 1px solid #2b2d31; border-radius: 8px; padding: 22px; }
.kutu b { display: block; font-size: 40px; color: #7cb8ff; } .kutu.turuncu b { color: #f0b45e; } .kutu span { color: #a3a6ad; font-size: 18px; }
.tek { text-align: center; } .uc { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; font-size: 18px; margin-top: 14px; } .uc p { margin: 0; }
.ucgenler { display: flex; justify-content: space-around; margin-top: 10px; }
.tri { margin: 0; text-align: center; width: 240px; } .tri figcaption { font-size: 18px; color: #ededee; margin-top: 8px; }
.ok { color: #7cb8ff; } .no { color: #f0b45e; }
.kume { background: #1b1c1f; border-left: 4px solid #f0b45e; padding: 10px 14px; font-size: 18px; margin: 10px 0; }
.sinir li { font-size: 21px; }
img { border-radius: 6px; background: white; }
"""
html = f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Sunum</title><style>{css}</style></head><body>{"".join(slides)}</body></html>'
out = ROOT / "sunum"
out.mkdir(exist_ok=True)
(out / "sunum.html").write_text(html, encoding="utf-8")
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(**({"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}))
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto((out / "sunum.html").as_uri())
    pg.pdf(path=str(out / "sunum.pdf"), width="1280px", height="720px", print_background=True)
    b.close()
print(f"sunum/sunum.pdf yazıldı ({len(slides)} slayt)")
