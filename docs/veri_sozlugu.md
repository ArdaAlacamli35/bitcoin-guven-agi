# Veri sözlüğü

**Kaynak:** Stanford SNAP — *soc-sign-bitcoin-otc* (Kumar vd., 2016).
https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html
**Toplama tarihi:** 29 Ekim 2026 (`scripts/01_veri_indir.py`, SHA-256 `data/raw/indirme_bilgisi.json` içinde)
**Kapsam:** 8 Kasım 2010 – 25 Ocak 2016 arası verilen puanlar
**Lisans / kullanım:** SNAP veri setleri araştırma ve eğitim amaçlı serbestçe kullanılabilir; kullanımda
Kumar vd. (2016, 2018) makalelerine atıf istenir. Kimlikler SNAP tarafından zaten anonimleştirilmiştir.

## `data/raw/soc-sign-bitcoinotc.csv.gz` (ham, başlıksız)

| Sütun | Tür | Anlam |
|---|---|---|
| SOURCE | tamsayı | Puanı veren kullanıcının SNAP kimliği |
| TARGET | tamsayı | Puanı alan kullanıcının SNAP kimliği |
| RATING | tamsayı (−10…+10, 0 hariç) | −10 tam güvensizlik, +10 tam güven |
| TIME | Unix zaman damgası (saniye) | Puanın verildiği an |

## `data/processed/kenarlar.csv` (yayımlanan kenar listesi)

| Sütun | Tür | Anlam |
|---|---|---|
| kaynak | metin | Puanı veren kullanıcı; `K` + tuzlu SHA-256'nın ilk 7 hanesi |
| hedef | metin | Puanı alan kullanıcı (aynı anonimleştirme) |
| puan | tamsayı | Ham puan (−10…+10) |
| isaret | +1 / −1 | puan > 0 ise +1 (güven), < 0 ise −1 (güvensizlik) |
| tarih | YYYY-AA-GG (UTC) | Puanın verildiği gün (saat bilgisi yayımlanmaz) |

## `data/processed/ag.graphml`

Yönlü ağ. Düğüm kimliği = anonim kimlik. Kenar öznitelikleri: `puan`, `isaret`, `tarih`.

## `results/dugum_olculeri.csv`

| Sütun | Anlam |
|---|---|
| derece, gelen | Toplam derece; gelen derece (aldığı puan sayısı) |
| betweenness | Yönlü betweenness, (n−1)(n−2) ile normalize |
| closeness | Yönsüz ağda normalize closeness |
| pagerank | Yönlü ağda PageRank |
| eigenvector | Yönsüz ağda eigenvector merkeziyeti (en büyüğü 1) |
| pr_pozitif / pr_negatif | Yalnızca pozitif / negatif kenarlardan oluşan ağda, |puan| ağırlıklı PageRank |
| gelen_pozitif / gelen_negatif | Alınan güven / güvensizlik puanı sayısı |
| neg_pay_gelen | Alınan puanlar içinde negatif payı |
| topluluk | Leiden topluluğu (0 = en büyük) |

## `results/topluluklar.csv`

| Sütun | Anlam |
|---|---|
| uye, ic_kenar | Üye sayısı, topluluk içi yönlü kenar sayısı |
| ic_neg_oran | İç kenarlarda negatif oranı |
| neg_z | İç negatif oranının, işaretler 1000 kez karıştırıldığındaki dağılıma göre z-skoru |
| ilk3_veren_payi | İç negatif puanların en aktif 3 hesap tarafından verilen payı |
| eksi10_payi | İç negatif puanların −10 olan payı |
| medyan_yil | Topluluğa dokunan kenarların medyan yılı |
| ad | Yukarıdaki ölçülerden kurallı olarak türetilen topluluk adı |
