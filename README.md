# Game Companies Atlas · Oyun Firmaları Atlası

**219 game companies in Türkiye + 878 global studios/publishers (excl. Türkiye).**  
*Türkiye’de 219 + dünyada (TR hariç) 878 oyun stüdyosu / yayıncı kaydı.*

🌐 **[Browse / Gez](https://gusanmaz.github.io/game-companies-atlas/)** ·
🇹🇷 [Türkçe](https://gusanmaz.github.io/game-companies-atlas/tr/) ·
🇬🇧 [English](https://gusanmaz.github.io/game-companies-atlas/en/) ·
🤝 **[Contribute / Katkı ver](CONTRIBUTING.md)**

---

## English

A practical directory of **game studios, publishers and ecosystem actors** — built to help people exploring careers, internships, publishers and regional clusters.

For each company the atlas records (where public sources allow): region/city, founding year, headcount, revenue/funding signals, genres, sample games, internship notes, remote-work notes, ownership, and a short note.

| List | Records | Files |
|---|---|---|
| Türkiye | 219 | [CSV](data/turkey.en.csv) · [Markdown](catalogue/TURKEY.en.md) · [Excel](catalogue/turkey.tr.xlsx) · [PDF](catalogue/turkey.tr.pdf) |
| Global (excl. Türkiye) | 878 | [CSV](data/global.en.csv) · [Markdown](catalogue/GLOBAL.en.md) · [Excel](catalogue/global.tr.xlsx) · [PDF](catalogue/global.tr.pdf) |

**Language.** The site UI and data dumps are available in **English and Turkish**. English fields were machine-translated from the Turkish source with review-friendly wording kept short.

**Limits.** Headcount and revenue/funding figures are often estimates or company statements. “Unknown” means the fact was not found in public sources — not that it is false. The Türkiye list is not a full census of every registered gaming LLC.

---

## Türkçe

**Oyun stüdyoları, yayıncılar ve ekosistem aktörleri** için pratik bir dizin — kariyer, staj, yayıncı ve bölgesel küme arayanlara yardımcı olmak için derlendi.

Her şirket için (kamuya açık kaynak izin verdiği ölçüde): bölge/şehir, kuruluş yılı, çalışan, gelir/fon sinyalleri, türler, örnek oyunlar, staj notu, uzaktan çalışma, sahiplik ve kısa not.

| Liste | Kayıt | Dosyalar |
|---|---|---|
| Türkiye | 219 | [CSV](data/turkey.tr.csv) · [Markdown](catalogue/TURKEY.tr.md) · [Excel](catalogue/turkey.tr.xlsx) · [PDF](catalogue/turkey.tr.pdf) |
| Küresel (TR hariç) | 878 | [CSV](data/global.tr.csv) · [Markdown](catalogue/GLOBAL.tr.md) · [Excel](catalogue/global.tr.xlsx) · [PDF](catalogue/global.tr.pdf) |

**Dil.** Arayüz ve veri dosyaları **Türkçe ve İngilizce**. İngilizce alanlar Türkçe kaynaktan makine çevirisiyle üretildi.

**Sınırlar.** Çalışan ve gelir/fon çoğu zaman tahmindir. “Bilinmiyor”, kamuya açık kaynakta bulunamadı demektir. Türkiye listesi tam sayım değildir.

---

## Repository layout / Depo düzeni

| Path | Contents |
|---|---|
| `docs/` | GitHub Pages site (`tr/`, `en/`, JSON data, downloads) |
| `data/` | Canonical CSV (TR + EN) |
| `catalogue/` | Markdown, Excel, PDF |
| `scripts/translate.py` | Parallel OpenAI TR→EN translation |
| `scripts/build.py` | Rebuild Pages HTML/JSON |

Rebuild:

```bash
export OPENAI_API_KEY=...   # only needed to re-translate
python3 scripts/translate.py
python3 scripts/build.py
```

## Corrections and additions / Düzeltme ve eklemeler

Companies close, get acquired, move city and grow. If a record is out of date — or your studio is
missing — please open an issue or a pull request. The one rule is that a claim must be backed by the
company's own site or a named public source; where a fact is unknown, the record says so. The English
fields are unreviewed machine translation, so **improving them is an excellent first contribution**.
See **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Şirketler kapanır, satın alınır, şehir değiştirir, büyür. Güncel olmayan bir kayıt görürseniz ya da
stüdyonuz listede yoksa lütfen issue veya pull request açın. Tek kural: her bilgi şirketin kendi
sitesine ya da adı belli bir kamuya açık kaynağa dayanmalı; bilinmeyen alanlar "bilinmiyor" der.
İngilizce alanlar gözden geçirilmemiş makine çevirisidir, **düzeltmek en iyi ilk katkıdır**. Türkçe
pull request'ler de memnuniyetle karşılanır.

## License / Lisans

Content — the CSV data and everything generated from it (`catalogue/`, `docs/`) — is licensed under
**[CC BY 4.0](LICENSE)**: reuse, adapt and redistribute freely, including commercially, as long as
you give attribution.

İçerik — CSV verisi ve ondan üretilen her şey — **[CC BY 4.0](LICENSE)** ile lisanslıdır: kaynak
göstermek koşuluyla, ticari kullanım dahil, serbestçe kullanabilir, uyarlayabilir ve dağıtabilirsiniz.

Suggested citation / Önerilen atıf:

> Usanmaz, G. *Game Companies Atlas.* https://github.com/gusanmaz/game-companies-atlas (CC BY 4.0)

## Who made this / Kim hazırladı

Author: Güvenç Usanmaz · August 2026
