"""Raporu (rapor/rapor.pdf) analiz sonuçlarından üretir. Tüm sayılar results/ klasöründen okunur.

Çalıştırma: python scripts/04_rapor.py   (önce analiz.ipynb ve 03_gorsellestirme.py)
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
o = json.loads((ROOT / "results" / "ozet.json").read_text(encoding="utf-8"))
mer = pd.read_csv(ROOT / "results" / "dugum_olculeri.csv", index_col=0)
top = pd.read_csv(ROOT / "results" / "topluluklar.csv", index_col=0)


def n(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, d=1):
    return "%" + n(x * 100, d)


def img(name, w="100%"):
    b = base64.b64encode((ROOT / "figures" / name).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b}" style="width:{w}">'


t, ol, kp, pn, dg, tp, nk, nm, kr = (o[k] for k in
    ["temel", "olculer", "kuvvet_yasasi", "pozitif_negatif", "denge", "topluluk", "negatif_kumelenme", "null_model", "kirilganlik"])
sp = pd.DataFrame(o["merkeziyet_spearman"])
ort_derece = 2 * t["kenar_yonsuz"] / t["dugum"]
ilk = mer.sort_values("pagerank", ascending=False).head(10)
hub = kr["en_merkezi_silinince"]
kopan = kr["once"]["ana_bilesen"] - hub["ana_bilesen"] - 1
negtop = mer.sort_values("pr_negatif", ascending=False).head(5)
cat = top[(top["neg_z"] > 2) & (top["ic_kenar"] >= 30)]

rows_top = "".join(
    f"<tr><td class=m>{i}</td><td>{int(r.derece)}</td><td>{int(r.gelen_pozitif)}</td><td>{int(r.gelen_negatif)}</td>"
    f"<td>{n(r.pagerank*1000,2)}</td><td>{n(r.betweenness,3)}</td><td>T{int(r.topluluk)}</td></tr>" for i, r in ilk.iterrows())
rows_neg = "".join(
    f"<tr><td class=m>{i}</td><td>{int(r.gelen_pozitif)}</td><td>{int(r.gelen_negatif)}</td><td>{pct(r.neg_pay_gelen)}</td><td>T{int(r.topluluk)}</td></tr>"
    for i, r in negtop.iterrows())
rows_comm = "".join(
    f"<tr{' class=hl' if c in cat.index else ''}><td>T{c}</td><td>{r.ad}</td><td>{int(r.uye)}</td><td>{int(r.ic_kenar)}</td>"
    f"<td>{pct(r.ic_neg_oran)}</td><td>{n(r.neg_z,1)}</td><td>{pct(r.ilk3_veren_payi,0)}</td><td>{pct(r.eksi10_payi,0)}</td><td>{int(r.medyan_yil)}</td></tr>"
    for c, r in top.iterrows())
olc = ["derece", "betweenness", "closeness", "pagerank", "eigenvector"]
rows_sp = "".join("<tr><th>" + a + "</th>" + "".join(f"<td>{n(sp.loc[a, b], 2)}</td>" for b in olc) + "</tr>" for a in olc)
tip = dg["tipler"]; bek = dg["beklenen_tip"]; zt = dg["z_tip"]
rows_tip = "".join(
    f"<tr><td class=m>{k}</td><td>{d}</td><td>{n(tip[k])}</td><td>{n(bek[k])}</td><td>{n(tip[k]/bek[k],2)}×</td><td>{n(zt[k],1)}</td></tr>"
    for k, d in [("+++", "Dengeli: dostumun dostu dostumdur"), ("+--", "Dengeli: düşmanımın düşmanı dostumdur"),
                 ("++-", "Dengesiz"), ("---", "Güçlü dengeye göre dengesiz, zayıf dengeye göre dengeli")])

html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Bitcoin OTC Güven Ağı — Rapor</title>
<style>
@page {{ size: A4; }}
body {{ font-family: "DejaVu Serif", Georgia, serif; font-size: 10.3pt; line-height: 1.45; color: #111; }}
h1 {{ font-family: "DejaVu Sans", sans-serif; font-size: 19pt; margin: 0 0 4pt; line-height: 1.2; }}
h2 {{ font-family: "DejaVu Sans", sans-serif; font-size: 13pt; margin: 16pt 0 5pt; border-bottom: 1px solid #ccc; padding-bottom: 2pt; }}
h3 {{ font-family: "DejaVu Sans", sans-serif; font-size: 11pt; margin: 11pt 0 4pt; }}
p {{ margin: 0 0 6pt; text-align: justify; }}
.alt {{ color: #555; font-family: "DejaVu Sans", sans-serif; font-size: 9.5pt; }}
.ozet {{ background: #f3f1ec; border-left: 4px solid #d9822b; padding: 8pt 10pt; margin: 10pt 0; }}
table {{ border-collapse: collapse; width: 100%; font-family: "DejaVu Sans", sans-serif; font-size: 8.3pt; margin: 6pt 0 8pt; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 3pt 4pt; text-align: right; }}
th:first-child, td:first-child, td.l {{ text-align: left; }}
td:nth-child(2) {{ text-align: left; }}
thead th {{ background: #eee; }}
tr.hl td {{ background: #fdebd9; font-weight: bold; }}
.m {{ font-family: "DejaVu Sans Mono", monospace; }}
figure {{ margin: 8pt 0; page-break-inside: avoid; }} figcaption {{ font-size: 8.5pt; color: #444; font-family: "DejaVu Sans", sans-serif; }}
.kirmizi {{ page-break-before: always; }}
ul {{ margin: 0 0 6pt 16pt; padding: 0; }} li {{ margin-bottom: 3pt; }}
.kaynak li {{ font-size: 9pt; }}
</style></head><body>

<h1>Kripto Takas Platformunda Güven Ağı: Güvensizlik Kümeleniyor mu, Ağ Dengeli mi?</h1>
<p class="alt">Arda Alaçamlı · 2516016006 · Sosyal Ağ Analizi dönem ödevi · Manisa Celal Bayar Üniversitesi, Büyük Veri Analistliği · Öğr. Gör. Osman Can Çetlenbik · Ekim 2026</p>

<div class="ozet"><b>Özet.</b> Bitcoin OTC platformunda {n(t['dugum'])} kullanıcının birbirine verdiği {n(t['kenar_yonlu'])} güven puanından (−10…+10) yönlü, işaretli bir ağ kurdum.
Ağ yapısal olarak <b>dengeli</b>: kenar işaretleri rastgele dağıtılsaydı üçgenlerin {pct(dg['null_guclu_ort'])}'i dengeli olurdu; gözlenen oran {pct(dg['guclu_denge_orani'])} (z = {n(dg['z_guclu_denge'],0)}).
Dengesiz "++−" üçgenleri rastlantıya göre {n(bek['++-']/tip['++-'],1)} kat az, "düşmanımın düşmanı dostumdur" (+−−) üçgenleri {n(tip['+--']/bek['+--'],1)} kat fazladır.
Güvensizlik genel olarak toplulukların <b>arasında</b> durur (negatif kenarların {pct(nk['neg_kenarlarin_toplulukar_arasi_payi'],0)}'i, pozitiflerin {pct(nk['poz_kenarlarin_toplulukar_arasi_payi'],0)}'i).
Ancak üç küçük toplulukta (T7–T9) negatif oran %32–67'ye çıkar. Bu kümelerin ikisinde güvensizliği birkaç hesap toplu olarak dağıtmış, birinde ise kullanıcılar karşılıklı olarak birbirine −10 vermiştir.</div>

<h2>1. Giriş ve araştırma sorusu</h2>
<p>Bitcoin OTC, kullanıcıların borsa aracılığı olmadan birbirleriyle Bitcoin alıp sattığı bir platformdur. Karşı tarafın dolandırıcı olma riskine karşı her kullanıcı, işlem yaptığı kişiye −10 (tam güvensizlik) ile +10 (tam güven) arasında bir puan verir. Bu puanlar bir <i>işaretli ağ</i> oluşturur: kenarların yalnızca varlığı değil, olumlu ya da olumsuz olması da anlam taşır.</p>
<p>Araştırma sorularım: <b>(1)</b> Güvensizlik (negatif) kenarları rastgele mi dağılmış, yoksa belirli kümelerde mi toplanıyor? <b>(2)</b> Ağ, Heider'in yapısal denge kuramının öngördüğü gibi "dengeli" mi? Bu sorular pratik açıdan da önemlidir: güvensizlik belirli kümelerde toplanıyorsa platform, şüpheli grupları tek tek kullanıcılardan daha erken fark edebilir.</p>

<h2>2. Veri ve ağın kurulması</h2>
<p><b>Kaynak.</b> Stanford SNAP <span class=m>soc-sign-bitcoin-otc</span> veri seti (Kumar vd., 2016, 2018). Veri <span class=m>scripts/01_veri_indir.py</span> ile otomatik indirilir ve SHA-256 özeti kaydedilir. İndirme bir GitHub Actions iş akışıyla da tekrarlanmıştır, iki kopyanın özeti aynıdır. Kapsam: {t['tarih_araligi'][0]} – {t['tarih_araligi'][1]}.</p>
<p><b>Düğüm:</b> Platformdaki bir kullanıcı. SNAP kimlikleri zaten anonimdir; yine de yayımlanan dosyalarda kimlikler tuzlu SHA-256 ile yeniden adlandırılmıştır (ör. <span class=m>K28a80ce</span>). <b>Kenar:</b> A → B, "A, B'ye bir puan verdi". Puan tek taraflı bir yargı olduğu için <b>yön korunmuştur</b>. <b>Ağırlık:</b> Puanın kendisi (−10…+10). <b>İşaret:</b> Puan &gt; 0 ise güven (+), &lt; 0 ise güvensizlik (−). Aynı yönde tekrar eden puan ve kendine puan bulunmadığı script içinde doğrulanmıştır.</p>
<p><b>Yönsüz görünümler.</b> Kümelenme, yol uzunluğu ve topluluk tespiti yönsüz ağ üzerinde yapılmıştır ({n(t['kenar_yonsuz'])} kenar). Çiftlerin {pct(t['karsilikli_oran'],0)}'i karşılıklı puanlaşmıştır. Yapısal denge için her çiftin işareti, iki puanın toplamının işaretidir. Toplamı tam 0 olan {t['celiskili_cift_atilan']} çelişkili çift bu analizden çıkarılmıştır (çiftlerin %0,3'ü).</p>
<p><b>Örnekleme yoktur:</b> Ağın tamamı ({n(t['dugum'])} düğüm) analiz edilmiştir. Yalnızca görselleştirmede filtre uygulanmıştır (Bölüm 6). Kenar listesi (<span class=m>data/processed/kenarlar.csv</span>), GraphML dosyası ve veri sözlüğü depodadır.</p>

<h2>3. Yöntem</h2>
<ul>
<li><b>Temel ölçüler:</b> Yoğunluk, zayıf ve güçlü bileşenler, ortalama en kısa yol ve çap (en büyük bileşende, örneklemesiz ve kesin), ortalama ve küresel kümelenme, derece benzeşimi.</li>
<li><b>Derece dağılımı:</b> <span class=m>powerlaw</span> paketiyle kuvvet yasası uydurma; log-normal, üstel ve kesik kuvvet yasasıyla olabilirlik oranı (R) testi.</li>
<li><b>Merkeziyet:</b> Derece, betweenness (yönlü, kesin), closeness, PageRank (yönlü), eigenvector; ölçüler arası Spearman korelasyonu.</li>
<li><b>Topluluklar:</b> Louvain ve Leiden algoritmaları, her biri 10 farklı tohumla. Kararlılık için tohumlar arası NMI ve ARI hesaplandı.</li>
<li><b>Null model:</b> Derece dizisi korunarak kenar değiştirmeyle üretilen 100 rastgele ağ (configuration model); kümelenme, ortalama yol ve modülerlik için z-skoru.</li>
<li><b>Kişisel ileri yöntem: işaretli ağ analizi.</b> (a) Tüm üçgenler sayılıp negatif kenar sayısına göre sınıflandırıldı. Negatif kenar sayısı çift olan üçgen dengelidir. Null model olarak üçgen yapısı sabit tutulup işaretler kenarlar arasında 1000 kez karıştırıldı. (b) Pozitif ve negatif alt ağlarda ayrı ayrı ağırlıklı PageRank hesaplandı. (c) Her topluluğun iç negatif oranı, işaret karıştırma null modeliyle karşılaştırıldı.</li>
</ul>
<p>Tüm hesaplar <span class=m>analiz.ipynb</span> defterinde, <span class=m>SEED = 42</span> ile yukarıdan aşağı çalıştırılarak yeniden üretilebilir.</p>

<h2>4. Bulgular</h2>
<h3>4.1 Temel yapı</h3>
<table><thead><tr><th>Ölçü</th><th>Değer</th><th>Bu ağda ne anlama geliyor?</th></tr></thead><tbody>
<tr><td>Düğüm / yönlü kenar</td><td>{n(t['dugum'])} / {n(t['kenar_yonlu'])}</td><td class=l>Kullanıcı başına ortalama {n(ort_derece,1)} farklı işlem ortağı.</td></tr>
<tr><td>Negatif kenar oranı</td><td>{pct(t['negatif_kenar_orani'])}</td><td class=l>Her 10 puandan yaklaşık 1'i güvensizlik bildiriyor.</td></tr>
<tr><td>Yoğunluk</td><td>{n(ol['yogunluk'],5)}</td><td class=l>Olası bağlantıların yalnızca binde biri var; herkes herkesle değil, küçük bir çevreyle işlem yapıyor.</td></tr>
<tr><td>Zayıf bileşen (en büyüğü)</td><td>{ol['zayif_bilesen']} ({n(ol['en_buyuk_zayif_bilesen'])})</td><td class=l>Kullanıcıların %99,9'u dolaylı yoldan birbirine bağlı; pazar tek parça.</td></tr>
<tr><td>Güçlü bileşen (en büyüğü)</td><td>{n(ol['guclu_bilesen'])} ({n(ol['en_buyuk_guclu_bilesen'])})</td><td class=l>Kullanıcıların {pct(ol['en_buyuk_guclu_bilesen']/t['dugum'],0)}'i yönlü puan zincirleriyle karşılıklı ulaşılabilir. Dışarıda kalan {n(o['guclu_bilesen_disi']['dugum'])} kişinin {n(o['guclu_bilesen_disi']['hic_puan_vermemis'])}'i hiç puan vermemiş, yalnızca puan almış hesaplar.</td></tr>
<tr><td>Ortalama en kısa yol / çap</td><td>{n(ol['ort_en_kisa_yol'],2)} / {ol['cap']}</td><td class=l>Rastgele iki kullanıcı arasında ortalama 3–4 adımlık bir "güvendiğimin güvendiği" zinciri var.</td></tr>
<tr><td>Ortalama kümelenme</td><td>{n(ol['ort_kumelenme'],3)}</td><td class=l>Bir kullanıcının iki işlem ortağının birbirini de puanlamış olma olasılığı %18; rastgele ağda %7 (Bölüm 4.4).</td></tr>
<tr><td>Derece benzeşimi</td><td>{n(ol['derece_benzesimi'],3)}</td><td class=l>Negatif: Çok işlem yapan "büyük tüccarlar" daha çok az işlem yapan yeni kullanıcılarla puanlaşıyor. Göbek-ve-jant (hub-and-spoke) yapısında bir pazar.</td></tr>
</tbody></table>

<h3>4.2 Derece dağılımı</h3>
<figure>{img('derece_dagilimi.png','78%')}<figcaption>Şekil 1. Derece dağılımının tamamlayıcı birikimli dağılımı (log-log).</figcaption></figure>
<p>Uydurulan kuvvet yasası üssü α = {n(kp['alpha'],2)} (x<sub>min</sub> = {kp['xmin']}, kuyrukta {n(kp['kuyruktaki_dugum'])} düğüm). Ancak olabilirlik testleri saf kuvvet yasasını desteklemiyor: Log-normal (R = {n(kp['karsilastirma']['lognormal']['R'],2)}, p &lt; 0,001) ve kesik kuvvet yasası (R = {n(kp['karsilastirma']['truncated_power_law']['R'],2)}, p &lt; 0,001) daha iyi uyuyor. Üstel dağılım ise açıkça reddediliyor (R = +{n(kp['karsilastirma']['exponential']['R'],2)}). <b>Yorum:</b> Dağılım ağır kuyruklu, yani birkaç hesap çok sayıda işlem yapıyor. Fakat en büyük tüccarlar bile bir üst sınıra takılıyor. Bir kişinin günde yapabileceği OTC işlemi sınırlı olduğu için bu beklenen bir durum.</p>

<h3>4.3 Merkeziyetler ve kırılganlık</h3>
<table><thead><tr><th>PageRank ilk 10</th><th>Derece</th><th>Aldığı +</th><th>Aldığı −</th><th>PageRank×1000</th><th>Betweenness</th><th>Topluluk</th></tr></thead><tbody>{rows_top}</tbody></table>
<p>PageRank ve betweenness ilk 10 listelerinin {o['ilk10_ortak_pagerank_betweenness']}'u ortaktır. Spearman korelasyonları (Tablo 2) iki ölçü ailesi gösteriyor. Derece, PageRank ve betweenness birbirine çok yakın (ρ ≈ 0,83–0,90): bu ağda "çok işlem yapan" ile "aracı konumdaki" çoğunlukla aynı kişidir. Closeness ve eigenvector ise kendi aralarında ρ = {n(sp.loc['closeness','eigenvector'],2)}, PageRank ile ancak ρ ≈ 0,5 ilişkili. Bu ölçüler hacmi değil, yoğun çekirdeğe yakınlığı ölçüyor.</p>
<table><thead><tr><th>Spearman ρ</th>{''.join(f'<th>{c}</th>' for c in olc)}</tr></thead><tbody>{rows_sp}</tbody></table>
<p><b>Kırılganlık deneyi.</b> Betweenness'ı en yüksek hesap (<span class=m>{hub['dugum']}</span>) ağdan çıkarılırsa ana bileşen {n(kr['once']['ana_bilesen'])} kullanıcıdan {n(hub['ana_bilesen'])} kullanıcıya düşer. Yani <b>{n(kopan)} kullanıcı pazarın geri kalanına hiçbir puan zinciriyle bağlı kalmaz</b>, bileşen sayısı {kr['once']['bilesen_sayisi']}'ten {n(hub['bilesen_sayisi'])}'e çıkar. Bu kullanıcıların pazarın geri kalanıyla tek bağlantısı bu hesaptır: Platform onlar hakkında yalnızca bu hesabın (ve kendi küçük çevrelerinin) görüşünü bilir. İlk 10 aracı birlikte çıkarılırsa ortalama yol {n(kr['once']['ort_yol'],2)}'den {n(kr['ilk10_silinince']['ort_yol'],2)} adıma uzar ve {n(kr['once']['ana_bilesen']-kr['ilk10_silinince']['ana_bilesen'])} kullanıcı kopar.</p>

<h3>4.4 Topluluklar ve null model</h3>
<p>Louvain ortalama modülerlik {n(tp['louvain_modularite_ort'],3)} (±{n(tp['louvain_modularite_std'],3)}), Leiden {n(tp['leiden_modularite_ort'],3)} (±{n(tp['leiden_modularite_std'],3)}) buldu. Leiden'in hafif üstünlüğü, Louvain'in bazen kopuk topluluk üretme sorununu düzeltmesinden gelir. Kararlılık orta düzeydedir: 10 tohum arasında ortalama NMI Louvain'de {n(tp['louvain_nmi_ort'],2)}, Leiden'de {n(tp['leiden_nmi_ort'],2)}; iki algoritma arasında {n(tp['louvain_leiden_nmi'],2)}. Büyük topluluklar her çalıştırmada büyük ölçüde aynı kalırken sınırdaki az bağlantılı kullanıcılar tohuma göre yer değiştiriyor. Bu nedenle analizde en yüksek modülariteli Leiden bölümlemesi kullanıldı ve bulgular yalnızca büyük topluluklar üzerinden yorumlandı.</p>
<figure>{img('null_model.png')}<figcaption>Şekil 2. Gözlenen ağ (turuncu çizgi) ile derece dizisi korunmuş 100 rastgele ağın (gri) karşılaştırması.</figcaption></figure>
<p><b>Null model.</b> Gözlenen kümelenme {n(nm['kumelenme']['gozlenen'],3)}, rastgele ağlarda {n(nm['kumelenme']['null_ort'],3)} ± {n(nm['kumelenme']['null_std'],4)} (z = {n(nm['kumelenme']['z'],0)}). Modülerlik {n(nm['modularite']['gozlenen'],3)}, rastgele ağlarda {n(nm['modularite']['null_ort'],3)} (z = {n(nm['modularite']['z'],0)}). Ortalama yol rastgele ağlardan biraz <i>uzun</i> ({n(nm['ort_yol']['gozlenen'],2)} vs {n(nm['ort_yol']['null_ort'],2)}, z = {n(nm['ort_yol']['z'],0)}): Topluluklar birbirine daha az köprüyle bağlandığı için yollar uzuyor. <b>Null model olmasaydı</b> 0,49'luk bir modülerliğin "yüksek" olduğunu iddia edemezdik, çünkü yalnızca derece dağılımı bile 0,31 üretiyor. Gerçek topluluk yapısının katkısı aradaki farktır ve bu fark rastlantıyla açıklanamaz.</p>

<h3>4.5 Kişisel ileri yöntem I: Yapısal denge</h3>
<p>Ağda {n(dg['ucgen'])} üçgen var. Tablo 3, her üçgen tipinin gözlenen sayısını, işaretler 1000 kez rastgele karıştırıldığındaki beklenen sayıyla karşılaştırıyor.</p>
<table><thead><tr><th>Tip</th><th>Anlamı</th><th>Gözlenen</th><th>Beklenen</th><th>Oran</th><th>z</th></tr></thead><tbody>{rows_tip}</tbody></table>
<figure>{img('yapisal_denge.png')}<figcaption>Şekil 3. Solda üçgen tipleri (log ölçek), sağda rastgele işaretli ağlarda dengeli üçgen oranının dağılımı.</figcaption></figure>
<p><b>Cevap 2: Ağ dengeli.</b> Güçlü denge oranı {pct(dg['guclu_denge_orani'])}, rastgele beklenti {pct(dg['null_guclu_ort'])} ± {pct(dg['null_guclu_std'],2)} (z = {n(dg['z_guclu_denge'],0)}). Somut olarak: İki kullanıcıya güvenen biri, bu ikisi arasında güvensizlik görmeyi rastlantıdan {n(bek['++-']/tip['++-'],1)} kat daha az bekler. Ortak bir "düşmana" sahip iki kullanıcının birbirine güvenmesi ({n(tip['+--'])} üçgen) ise {n(tip['+--']/bek['+--'],1)} kat daha sık görülür. Platformda bir hesabı dolandırıcı olarak işaretleyen kullanıcılar birbirlerini olumlu puanlıyor.</p>
<p>Tek istisna "−−−" üçgenleri: Güçlü denge kuramına göre dengesiz sayılmalarına rağmen rastlantıdan {n(tip['---']/bek['---'],1)} kat fazlalar. Bu bulgu Davis'in <i>zayıf denge</i> kuramıyla uyumludur: Birbirine düşman üç ya da daha fazla grup bir arada var olabilir. Bu {n(o['eksi3_ucgen']['toplam'])} üçgenin yalnızca {o['eksi3_ucgen']['tek_toplulukta']}'ü tek bir topluluğun içindedir (T9'da {o['eksi3_ucgen']['T9_icinde']}). Çoğu farklı toplulukları birbirine bağlar: Pazarda birbirine güvenmeyen ikiden fazla grup var.</p>

<h3>4.6 Kişisel ileri yöntem II: Pozitif ve negatif alt ağların merkeziyetleri</h3>
<p>Pozitif alt ağda ({n(pn['pozitif_kenar'])} kenar) PageRank bir <b>itibar</b> ölçüsüdür: Güvenilen kişilerin güvendiği kişi yükselir. Negatif alt ağda ({n(pn['negatif_kenar'])} kenar) PageRank ise <b>toplanan güvensizliği</b> ölçer. En az 5 puan almış {n(pn['aktif_dugum'])} kullanıcıda iki ölçü arasındaki Spearman korelasyonu ρ = {n(pn['spearman_pr_pos_neg_aktif'],2)}'dir, yani neredeyse sıfır. Her iki listenin ilk 20'sinde yalnızca {pn['ilk20_kesisim']} ortak kullanıcı var. Bu iki ölçü birbirinin tersi değildir; bir hesabın ne kadar güvenildiği, ne kadar güvenilmediği hakkında neredeyse hiçbir şey söylemez. Bu yüzden bir itibar sistemi tek bir "net puan" yerine iki ayrı gösterge sunmalıdır.</p>
<p>Güvensizlik birkaç hesapta toplanmıştır: Kullanıcıların yalnızca {pct(pn['negatif_alanlarin_payi'],0)}'i en az bir negatif puan almıştır, ve negatif puanların {pct(pn['negatif_kenarlarin_yuzde_kaci_ilk_yuzde5'],0)}'i kullanıcıların %5'ine gitmiştir.</p>
<table><thead><tr><th>Negatif ağda PageRank ilk 5</th><th>Aldığı +</th><th>Aldığı −</th><th>Negatif payı</th><th>Topluluk</th></tr></thead><tbody>{rows_neg}</tbody></table>

<h3>4.7 Kişisel ileri yöntem III: Negatif kenar yoğunluğu yüksek topluluklar</h3>
<p><b>Cevap 1: Güvensizlik genel olarak kümelerin içinde değil, arasında.</b> Topluluk içi kenarların {pct(nk['ic_kenar_neg_oran'])}'i negatif, topluluklar arası kenarlarınsa {pct(nk['toplulukar_arasi_neg_oran'])}'i. İşaretler rastgele dağıtılsaydı iç negatif oranı bu kadar düşük çıkmazdı (z = {n(nk['z_ic_neg'],1)}). Bu, dengeli bir ağın beklenen görüntüsüdür: Gruplar kendi içinde güvenir, güvensizlik gruplar arasındaki sınırda yaşanır.</p>
<p><b>Ancak üç topluluk bu kuralı bozuyor</b> (Tablo 5, vurgulu satırlar). Topluluk adları, iç negatif kenarların kimden kime gittiğine bakılarak veriden türetilmiştir:</p>
<table><thead><tr><th></th><th>Ad</th><th>Üye</th><th>İç kenar</th><th>İç negatif</th><th>z</th><th>İlk 3 verenin payı</th><th>−10 payı</th><th>Yıl</th></tr></thead><tbody>{rows_comm}</tbody></table>
<ul>
<li><b>T7 ve T8, toplu işaretleme kümeleri:</b> İç negatif puanların sırasıyla {pct(top.loc[7,'ilk3_veren_payi'],0)} ve {pct(top.loc[8,'ilk3_veren_payi'],0)}'ini yalnızca 3 hesap vermiştir. T8'de bu 3 hesap {int(top.loc[8,'neg_alan'])} farklı kullanıcıyı işaretlemiştir. Bu kümeler "birbirine düşman insanlar" değil, birkaç hesabın çok sayıda kullanıcıyı uyarı amaçlı ya da toplu olarak işaretlemesidir.</li>
<li><b>T9, karşılıklı −10 çatışma kümesi:</b> İç kenarların {pct(top.loc[9,'ic_neg_oran'],0)}'ü negatif ve bunların {pct(top.loc[9,'eksi10_payi'],0)}'u en sert puan olan −10. Puanlar {int(top.loc[9,'neg_veren'])} farklı hesaptan {int(top.loc[9,'neg_alan'])} farklı hesaba gidiyor ve 2013'te yoğunlaşıyor. Topluluk algoritması bu grubu bir arada bulmuştur çünkü üyeler birbirleriyle sık etkileşmiştir, ama etkileşimlerin çoğu düşmancadır.</li>
</ul>
<figure>{img('topluluk_negatif.png','80%')}<figcaption>Şekil 4. Toplulukların aktif olduğu yıl ve iç negatif oranı. Turuncu: Rastlantıyla açıklanamayacak kadar yüksek (z &gt; 2). Daire boyutu üye sayısıyla orantılıdır.</figcaption></figure>

<h2>5. Tartışma</h2>
<p>İki sorunun cevabı birbirini tamamlıyor. Ağ bir bütün olarak dengeli ve güvensizlik gruplar arasındaki sınırda duruyor. Ancak bu dengeli görüntünün içinde üç istisnai küme var ve bunların ikisi farklı bir mekanizmayla oluşmuş. Pratik çıkarım şu: Bir platform, negatif puan oranı yüksek bir topluluk gördüğünde iki soruyu ayrı sormalıdır. Puanlar birkaç hesaptan mı geliyor (toplu işaretleme; ya uyarıcı topluluk üyeleri ya da itibar saldırısı), yoksa grup içinde karşılıklı mı (çatışma)? Bu ayrım yalnızca işaretli ağ analiziyle yapılabilir. Toplam puana bakan basit bir itibar sistemi ikisini aynı gösterir.</p>
<p><b>Nedensellik uyarısı:</b> Bu bulgular ağ yapısından elde edilmiştir ve neden-sonuç ilişkisi kurmaz. T7–T9'daki kullanıcıların dolandırıcı olduğu, işaretleyenlerin haklı olduğu ya da çatışmanın neden çıktığı bu veriden <b>çıkarılamaz</b>.</p>

<h2>6. Sınırlar</h2>
<ul>
<li><b>Dönem:</b> Veri 2010–2016 arasını kapsar ve bugünkü kripto pazarını temsil etmez. Ağ tek bir anlık görüntü olarak incelendi; zaman içindeki değişim yalnızca topluluk yılı düzeyinde kullanıldı.</li>
<li><b>Yön kaybı:</b> Denge analizi için ağ yönsüze indirgendi; iki yönlü çelişkili {t['celiskili_cift_atilan']} çift çıkarıldı. Yönlü denge (statü kuramı) incelenmedi.</li>
<li><b>İşaretsiz topluluk tespiti:</b> Louvain/Leiden yalnızca bağlantının varlığına baktı, işaretine bakmadı. İşaretli topluluk tespiti (ör. negatif kenarları cezalandıran modülerlik) T9 gibi kümeleri bölebilirdi.</li>
<li><b>Kararlılık:</b> Tohumlar arası NMI ≈ 0,7. Küçük topluluk sınırları kesin değildir.</li>
<li><b>Görselleştirme filtresi:</b> Etkileşimli ağ ve poster 786 düğüm gösterir (derece ≥ 20, ya da çatışma kümesinde derece ≥ 8). İkinci kural araştırma sorusunu görünür kılmak için bilinçli bir yanlılıktır. Hesapların tamamı filtresiz ağ üzerinde yapılmıştır.</li>
<li><b>Puan davranışı:</b> Kullanıcıların puan verme alışkanlıkları farklıdır (bazıları yalnızca +1 ya da −10 verir). Puanlar normalize edilmedi.</li>
</ul>

<h2>7. Kaynakça</h2>
<ul class="kaynak">
<li>Kumar, S., Spezzano, F., Subrahmanian, V. S., &amp; Faloutsos, C. (2016). Edge weight prediction in weighted signed networks. <i>IEEE ICDM</i>.</li>
<li>Kumar, S., Hooi, B., Makhija, D., Kumar, M., Faloutsos, C., &amp; Subrahmanian, V. S. (2018). REV2: Fraudulent user prediction in rating platforms. <i>ACM WSDM</i>.</li>
<li>Leskovec, J., &amp; Krevl, A. (2014). SNAP Datasets: Stanford Large Network Dataset Collection. https://snap.stanford.edu/data</li>
<li>Heider, F. (1946). Attitudes and cognitive organization. <i>Journal of Psychology</i>, 21, 107–112.</li>
<li>Cartwright, D., &amp; Harary, F. (1956). Structural balance: A generalization of Heider's theory. <i>Psychological Review</i>, 63(5), 277–293.</li>
<li>Davis, J. A. (1967). Clustering and structural balance in graphs. <i>Human Relations</i>, 20(2), 181–187.</li>
<li>Leskovec, J., Huttenlocher, D., &amp; Kleinberg, J. (2010). Signed networks in social media. <i>ACM CHI</i>.</li>
<li>Blondel, V. D., Guillaume, J.-L., Lambiotte, R., &amp; Lefebvre, E. (2008). Fast unfolding of communities in large networks. <i>J. Stat. Mech.</i></li>
<li>Traag, V. A., Waltman, L., &amp; van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. <i>Scientific Reports</i>, 9, 5233.</li>
<li>Clauset, A., Shalizi, C. R., &amp; Newman, M. E. J. (2009). Power-law distributions in empirical data. <i>SIAM Review</i>, 51(4), 661–703.</li>
<li>Alstott, J., Bullmore, E., &amp; Plenz, D. (2014). powerlaw: A Python package for analysis of heavy-tailed distributions. <i>PLoS ONE</i>, 9(1).</li>
</ul>
<p class="alt">Yapay zekâ beyanı: Kod, analiz iskeleti ve rapor taslağı Claude (Anthropic) yardımıyla hazırlanmıştır. Tüm sayılar defterden otomatik okunmuştur. Ayrıntılı beyan README'dedir.</p>
</body></html>"""

out = ROOT / "rapor"
out.mkdir(exist_ok=True)
(out / "rapor.html").write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    import os
    b = p.chromium.launch(**({"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}))
    pg = b.new_page()
    pg.goto((out / "rapor.html").as_uri())
    pg.pdf(path=str(out / "rapor.pdf"), format="A4", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#777"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
           margin={"top": "16mm", "bottom": "16mm", "left": "16mm", "right": "16mm"})
    b.close()
print("rapor/rapor.pdf yazıldı")
