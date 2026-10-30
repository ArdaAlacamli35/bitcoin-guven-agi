"""Sade sunum (sunum/sunum.pdf): 10 slayt, her slaytta tek fikir, büyük yazı, terim yerine günlük dil.
Ayrıntılı sürüm: 05_sunum.py (sunum/sunum_ayrintili.pdf). Sayılar results/ klasöründen okunur."""
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
S = lambda title, body, nedemek="": slides.append(
    f'<section class="slide"><h1>{title}</h1><div class="body">{body}</div>'
    + (f'<p class="nedemek"><b>Ne demek?</b> {nedemek}</p>' if nedemek else '') + '</section>')
K = lambda sayi, yazi, renk="": f'<div class="kutu {renk}"><b>{sayi}</b><span>{yazi}</span></div>'
c7, c8, c9 = top.loc[7], top.loc[8], top.loc[9]

# 1
slides.append(f"""<section class="slide kapak"><p class="ust">Sosyal Ağ Analizi · Arda Alaçamlı</p>
<h1>Bitcoin pazarında güvensizlik rastgele dağılmıyor: ağ dengeli, ama üç grup kuralı bozuyor</h1>
<div class="soru"><p>İki sorum var</p><ol><li>"Güvenmiyorum" puanları belli gruplarda mı toplanıyor?</li><li>Ağ "dostumun dostu dostumdur" kuralına uyuyor mu?</li></ol></div>
<p class="alt">Veri: Stanford SNAP · Bitcoin OTC alım-satım platformu · 2010–2016</p></section>""")

# 2
S(f"{n(t['dugum'])} kullanıcı, {n(t['kenar_yonlu'])} puan: her 10 puandan 1'i \"güvenmiyorum\"",
  f"""<div class="kutular uclu">{K(n(t['dugum']),'kullanıcı')}{K(n(t['kenar_yonlu']),'puan (işlemden sonra verilen)')}{K(pct(t['negatif_kenar_orani'],0),'güvensizlik puanı (−1 … −10)','turuncu')}</div>
<p class="orta">İnsanlar bitcoin alıp sattıktan sonra karşı tarafa <span class="ok">+1 … +10 (güveniyorum)</span> ya da <span class="no">−1 … −10 (güvenmiyorum)</span> puan vermiş.</p>""",
  "Her kullanıcı ağda bir nokta, her puan bir ok. Ağın tamamını kullandım, örnekleme yapmadım.")

# 3
S(f"Pazar tek bir hesaba bağımlı: o hesap silinince {n(kopan)} kişi yalnız kalıyor",
  f"""<div class="kutular">{K('K28a80ce','en çok "köprü" olan hesap')}{K(n(kopan),'bu hesap silinince pazardan kopan kişi','turuncu')}</div>
<p class="orta">Herkes herkese ortalama <b>{n(ol['ort_en_kisa_yol'],1)} adımda</b> ulaşıyor. Büyük tüccarlar, çok sayıda yeni ve küçük kullanıcıyla işlem yapıyor.</p>""",
  "Betweenness: başkaları arasındaki en kısa yolların ne kadarının bu kişiden geçtiği. Köprü yıkılınca o kişiler pazardan kopuyor.")

# 4
S("Gruplar tesadüf değil: gerçek ağ, 100 rastgele ağın hepsinden daha gruplu",
  f"""<div class="kutular">{K(n(nm['modularite']['gozlenen'],2),'gerçek ağın gruplaşma puanı')}{K(n(nm['modularite']['null_ort'],2),'100 rastgele ağın ortalaması','gri')}</div>
<p class="orta">Grupları Louvain ve Leiden algoritmalarıyla buldum. 10 kez çalıştırdım: büyük gruplar her seferinde aynı çıktı.</p>""",
  "Modülerlik, grupların içinin dışına göre ne kadar sıkı bağlı olduğunu ölçer. Karşılaştırma yapmasaydım 0,49'un yüksek mi düşük mü olduğunu bilemezdim.")

# 5
S("Yöntem: bir üçgende eksi sayısı 0 ya da 2 ise üçgen dengelidir",
  f"""<div class="ucgenler">{ucgen('+','+','+','Dostumun dostu dostumdur',True)}{ucgen('+','−','−','Düşmanımın düşmanı dostumdur',True)}{ucgen('+','+','−','İki dostum birbirine düşman',False)}{ucgen('−','−','−','Herkes herkese düşman',False)}</div>""",
  "Ağdaki tüm üçgenleri saydım. Sonra artı/eksileri 1000 kez rastgele karıştırıp \"tesadüf olsaydı ne çıkardı?\" diye karşılaştırdım.")

# 6
S(f"Ağ dengeli: üçgenlerin {pct(dg['guclu_denge_orani'],0)}'si kurala uyuyor, tesadüf olsaydı {pct(dg['null_guclu_ort'],0)} olurdu",
  f"""<div class="kutular">{K(pct(dg['guclu_denge_orani'],0),'gerçek ağda dengeli üçgen')}{K(pct(dg['null_guclu_ort'],0),'puanlar rastgele dağıtılsaydı','gri')}</div>
<p class="orta">1000 rastgele karıştırmanın hiçbiri {pct(dg['guclu_denge_orani'],0)}'ye yaklaşmadı. En belirgin örüntü: <b>aynı kişiye eksi verenler birbirine artı veriyor</b> (beklenenin {n(tip['+--']/bek['+--'],0)} katı).</p>""",
  "\"Düşmanımın düşmanı dostumdur\" bu pazarda gerçekten işliyor.")

# 7
S("Güvensizlik genelde gruplar arasında, ama üç grupta içeriye yerleşmiş",
  f"""<div class="kutular uclu">{K('T7','birkaç hesap çok sayıda kişiye eksi vermiş (2012)','turuncu')}{K('T8',f"3 hesap {int(c8.neg_alan)} kişiye eksi vermiş (2013)",'turuncu')}{K('T9',f"iç puanların {pct(c9.ic_neg_oran,0)}'si eksi, neredeyse hepsi −10",'turuncu')}</div>
<p class="orta">Diğer 8 grupta eksi puanlar az ve çoğu grupların <b>arasında</b>. <span class="no">Canlı gösterim: etkileşimli ağda T9.</span></p>""",
  "İki farklı durum var: T7–T8'de birkaç kişi toplu eksi veriyor, T9'da herkes birbirine en sert puanı veriyor.")

# 8
S("Çok güvenilen biri az güvenilmeyen biri demek değil: iki puan ayrı şeyler",
  f"""<div class="kutular">{K(f"{pn['ilk20_kesisim']} / 20","\"en güvenilen 20\" ve \"en güvenilmeyen 20\" listesinde ortak kişi")}{K(pct(pn['negatif_kenarlarin_yuzde_kaci_ilk_yuzde5'],0),"eksi puanların, kullanıcıların sadece %5'ine gidiyor",'turuncu')}</div>""",
  "Artıları ve eksileri tek bir \"net puan\"da toplamak bilgi kaybettirir. Bir itibar sistemi ikisini ayrı göstermeli.")

# 9
S("Cevap: ağ dengeli, güvensizlik gruplar arasında, ama üç grup ayrı incelenmeli",
  f"""<div class="iki2"><div class="vurgu turuncu"><p class="buyuk">Soru 1: Toplanıyor mu?</p><p><b>Genelde hayır.</b> Eksi puanlar grupların arasında. İstisna: T7, T8, T9.</p></div>
<div class="vurgu"><p class="buyuk">Soru 2: Dengeli mi?</p><p><b>Evet.</b> Üçgenlerin {pct(dg['guclu_denge_orani'],0)}'si dengeli, tesadüf olsaydı {pct(dg['null_guclu_ort'],0)}.</p></div></div>""")

# 10
S("Sınırlar: bu ağ kimin dolandırıcı olduğunu söylemez", """<ul class="sinir">
<li><b>Kim haklı bilinmez:</b> Veri sadece kimin kime puan verdiğini gösteriyor.</li>
<li><b>Veri eski:</b> 2010–2016; bugünkü kripto pazarını temsil etmez.</li>
<li><b>Grup bulma eksileri görmüyor:</b> Eksileri hesaba katan bir yöntem T9'u bölebilirdi.</li>
<li><b>Haritada 786 kişi var:</b> Okunabilsin diye. Hesapların hepsi 5.881 kişilik tam ağda yapıldı.</li></ul>
<p class="alt">Kod, rapor ve etkileşimli ağ: github.com/ArdaAlacamli35/bitcoin-guven-agi</p>""")

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

.slide h1 { font-size: 38px !important; margin-bottom: 40px !important; }
.body { font-size: 26px !important; }
.kutular.uclu { grid-template-columns: repeat(3, 1fr); }
.kutular { gap: 24px; }
.kutu { padding: 30px; }
.kutu b { font-size: 58px; } .kutu span { font-size: 22px; display: block; margin-top: 6px; }
.kutu.gri b { color: #a3a6ad; }
.orta { text-align: center; margin-top: 36px; }
.nedemek { position: absolute; left: 60px; right: 60px; bottom: 40px; margin: 0; font-size: 22px; color: #c9cbd0; border-top: 1px solid #2b2d31; padding-top: 16px; }
.nedemek b { color: #f0b45e; }
.iki2 { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.sinir li { font-size: 26px !important; margin-bottom: 18px; }
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
