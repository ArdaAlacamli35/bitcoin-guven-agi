# Kripto Takas Platformunda Güven Ağı

**Bulgu (tek cümle):** Bitcoin OTC güven ağı yapısal olarak dengeli: dengesiz üçgenler rastlantıya göre 2,7 kat az ve güvensizlik genel olarak toplulukların *arasında* duruyor; ancak üç küçük topluluk (T7–T9) bu kuralı bozuyor ve ikisinde güvensizliği birkaç hesap toplu olarak dağıtmış, birinde kullanıcılar birbirine karşılıklı −10 vermiş.

**CV cümlesi:** 5.881 kullanıcılı Bitcoin OTC işaretli güven ağında yapısal denge analizi yaptım; dengeli üçgen oranını 1.000 rastgele ağla karşılaştırıp (z = 31) güvensizliğin yoğunlaştığı 3 topluluğu Leiden + null model ile tespit ettim (Python, igraph, Sigma.js).

Sosyal Ağ Analizi dönem ödevi · Manisa Celal Bayar Üniversitesi, Büyük Veri Analistliği · Arda Alaçamlı (2516016006)

| | |
|---|---|
| Rapor | [`rapor/rapor.pdf`](rapor/rapor.pdf) |
| Sunum | [`sunum/sunum.pdf`](sunum/sunum.pdf) |
| Poster (A3) | [`poster/poster_A3.pdf`](poster/poster_A3.pdf) |
| Etkileşimli ağ | Portföyde: https://ardaalacamli.vercel.app/projeler/bitcoin-guven-agi · kaynak: [`web/`](web/) |
| Defter | [`analiz.ipynb`](analiz.ipynb) (`analiz.py` ile eşlenik, jupytext) |
| Veri sözlüğü | [`docs/veri_sozlugu.md`](docs/veri_sozlugu.md) |

## Araştırma sorusu

Güvensizlik (negatif) kenarları belirli kümelerde toplanıyor mu? Ağ yapısal olarak "dengeli" mi?

## Öne çıkan sonuçlar

| | Gözlenen | Rastgele beklenti | z |
|---|---|---|---|
| Dengeli üçgen oranı | %87,2 | %67,6 (işaret karıştırma, 1000 ağ) | 31 |
| "++−" (dengesiz) üçgen | 3.875 | 10.583 | −33 |
| "+−−" ("düşmanımın düşmanı dostum") | 5.378 | 1.823 | 36 |
| Ortalama kümelenme | 0,178 | 0,074 (100 configuration model) | 57 |
| Modülerlik (Louvain) | 0,489 | 0,310 | 192 |
| Topluluk içi negatif oranı | %9,0 | işaret karıştırmaya göre düşük | −9,2 |

## Depo yapısı

```
scripts/01_veri_indir.py      SNAP'ten indir, SHA-256 ile doğrula
scripts/02_ag_kur.py          anonimleştir, kenar listesi + GraphML yaz
analiz.ipynb / analiz.py      tüm ölçüler, topluluklar, null model, yapısal denge (SEED = 42)
scripts/03_gorsellestirme.py  web/ag.json (filtreli ağ) + poster/poster_A3.pdf
scripts/04_rapor.py           rapor/rapor.pdf (sayılar results/ klasöründen okunur)
scripts/05_sunum.py           sunum/sunum.pdf
web/                          Sigma.js etkileşimli ağ (arama, detay paneli, topluluk filtresi, TR/EN)
data/raw, data/processed      ham veri, kenarlar.csv, ag.graphml
results/, figures/            sayısal sonuçlar ve şekiller
```

## Yeniden üretme

```bash
python -m pip install -r requirements.txt
python scripts/01_veri_indir.py
python scripts/02_ag_kur.py
jupyter nbconvert --to notebook --execute --inplace analiz.ipynb
python scripts/03_gorsellestirme.py
python -m playwright install chromium   # rapor ve sunum PDF'i için
python scripts/04_rapor.py && python scripts/05_sunum.py
cd web && npm install && npm run build   # etkileşimli ağ
```

Tüm rastgele işlemler sabit tohumla (`SEED = 42`) çalışır. Ham veri indirme adımı GitHub Actions ile de tekrarlanmıştır (`.github/workflows/veri-indir.yml`); iki kopyanın SHA-256 özeti aynıdır.

## Etik ve gizlilik

- Veri açık bir akademik veri setidir (SNAP); kazıma yapılmamıştır.
- SNAP kimlikleri zaten anonimdir; yayımlanan tüm dosyalarda kimlikler ek olarak tuzlu SHA-256 ile yeniden adlandırılmıştır. Saat bilgisi yayımlanmaz, yalnızca gün.
- Bulgular ağ yapısından çıkarılmıştır, **nedensellik iddiası taşımaz**: T7–T9'daki kullanıcıların dolandırıcı olduğu veya işaretleyenlerin haklı olduğu bu veriden çıkarılamaz.

## Yapay zekâ kullanım beyanı

Bu projede **Claude (Anthropic)** kullanıldı.
- **Hangi iş için:** Veri indirme ve ağ kurma script'leri, analiz defteri, Sigma.js görselleştirmesi ile rapor, sunum ve poster üretim script'lerinin hazırlanması.
- **Doğrulama:** Defter baştan sona yeniden çalıştırıldı. Rapor ve sunumdaki tüm sayılar elle yazılmadı, `results/ozet.json` dosyasından otomatik okunuyor. Kontrol sırasında rapordaki iki ifade yanlış çıktı ve düzeltildi ("−−−" üçgenlerinin nerede olduğu ve güçlü bileşenin dışındaki hesapların türü). Bu iki hesap deftere ayrı hücre olarak eklendi. Topluluk adları elle verilmedi, defterdeki kurallarla türetildi.
- **Benim katkım / değişikliklerim:** _(Arda: defteri kendin çalıştırıp incelediğinde neyi değiştirdiğini, neyi kendi cümlelerinle yeniden yazdığını buraya ekle.)_

## Kaynak

Kumar, S., Spezzano, F., Subrahmanian, V. S., & Faloutsos, C. (2016). Edge weight prediction in weighted signed networks. *IEEE ICDM*.
Kumar, S., Hooi, B., Makhija, D., Kumar, M., Faloutsos, C., & Subrahmanian, V. S. (2018). REV2: Fraudulent user prediction in rating platforms. *ACM WSDM*.
