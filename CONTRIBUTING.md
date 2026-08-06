# Contributing / Katkı

Corrections and additions are very welcome. **[English](#english) · [Türkçe](#türkçe)**

---

## English

### The one rule

**Every factual claim must be traceable to the company's own site or a named public source.**

A studio's own website, careers page, press release, investment announcement or an identified news
report is acceptable. A number you remember, a figure from an unsourced list, or an LLM's guess is
not. Company headcounts and revenues move fast and are widely misreported, so when a fact cannot be
verified, **write `bilinmiyor` / `unknown` rather than guessing**. "Unknown" is a real answer here,
not a gap to be filled in with something plausible.

If the source needs context — a figure is a company self-report, a headcount is a press estimate, an
internship ran in 2024 and may not run again — put that context in the field itself. The existing
records already do this (`350+ (Mobidictum 2025)`, `evet — yaz stajı (ofis, 2024 örneği)`).

### What to contribute

| | |
|---|---|
| **Better English** | `data/*.en.csv` is machine translation from Turkish, **not reviewed by a human** — fixing it is the best first contribution |
| **A missing company** | A studio, publisher, service provider or ecosystem actor that belongs on either list |
| **A correction** | Company closed, acquired, moved city, renamed, changed headcount or ownership |
| **A deepening** | Filling `bilinmiyor` fields with a sourced fact — especially internship, remote-work and funding notes |

### Translations — the easiest useful contribution

`data/turkey.tr.csv` and `data/global.tr.csv` are the **source of truth**. `data/turkey.en.csv` and
`data/global.en.csv` were produced from them with OpenAI and **nobody has read them line by line**.
Expect mistranslated genre names, awkward internship notes, city names that should have stayed
Turkish, and free-text notes that lost their meaning.

You do not need to research anything to fix these — you only need to read the Turkish row next to the
English one. Please do **one file, or one clearly bounded slice of a file, at a time** so the data
never sits half-corrected. When the Turkish and the English disagree about a fact, the Turkish wins;
if the Turkish itself looks wrong, fix the Turkish first and say so in the pull request.

### The columns

Both languages carry the same thirteen columns, in the same order:

| Turkish | English | Notes |
|---|---|---|
| `Firma` | `Company` | Company name as the company writes it |
| `Bölge` | `Region` | Country, or Turkish region for the Türkiye list |
| `Şehir` | `City` | City, with offices in parentheses when useful |
| `Kuruluş` | `Founded` | Founding year |
| `Çalışan` | `Employees` | Headcount **with its source and date** |
| `Gelir_fon` | `Revenue_funding` | Revenue, funding round or valuation signals |
| `Web` | `Web` | Official site, `https://`, no tracking parameters |
| `Türler` | `Genres` | Genres, `/`-separated |
| `Örnek_oyunlar` | `Sample_games` | A few representative titles, `;`-separated |
| `Staj` | `Internship` | What is known about internships, and when it was true |
| `Uzaktan` | `Remote` | Remote / hybrid / office |
| `Sahiplik` | `Ownership` | Independent, parent company, investor |
| `Not` | `Notes` | Free text — anything a reader should know |

Semicolons separate items inside a field; a field containing a comma must be quoted, as in any CSV.
Do not add, remove or reorder columns, and do not change the header row — the generators read it.

### How

1. Edit the CSVs in **`data/`**. The Turkish files are the source of truth; `catalogue/`,
   `docs/data/*.json` and `docs/files/` are **generated** — do not edit those by hand.
2. Regenerate the derived files:

   ```bash
   python3 scripts/build.py
   ```

   Only if you are re-translating (you usually are not — hand-edit `*.en.csv` instead):

   ```bash
   export OPENAI_API_KEY=...
   python3 scripts/translate.py
   ```

3. Open a pull request describing what you changed and where you verified it. **Pull requests and
   issues in Turkish or English are equally welcome.**

If CSVs are not your thing, **just open an issue** with the company name and a link. That is a
genuinely useful contribution and someone will do the data entry.

### Known limitations — each one is an opening

These are the places the atlas is weakest, and therefore where a contribution helps most:

- **Headcount and revenue** are often estimates or company self-reports; a sourced, dated correction
  is always an improvement.
- **`bilinmiyor` / `unknown`** means the fact was not found in public sources — not that it does not
  exist. Many of these can be closed by someone who knows the company.
- **Internship notes** may describe a programme that ran in a past year rather than an open position.
  Anything that says which year it applies to is better than anything that does not.
- **The Türkiye list is not a full census** of registered game companies. Small and new studios are
  under-represented.
- **The English fields are unreviewed machine translation**, as described above.

### Scope

Companies that **make, publish or directly serve games**: studios, publishers, porting and QA houses,
audio and art outsourcers, engine and tooling vendors, and the funds, accelerators and associations
that sit around them. General software consultancies with one game in their portfolio, marketing
agencies and individual freelancers are out of scope, however good they are.

---

## Türkçe

### Tek kural

**Her bilgi şirketin kendi sitesinden ya da adı belli bir kamuya açık kaynaktan doğrulanabilir olmalı.**

Şirketin kendi sitesi, kariyer sayfası, basın bülteni, yatırım duyurusu veya kaynağı belli bir haber
kabul edilir. Hatırladığınız bir sayı, kaynaksız bir listedeki rakam veya bir dil modelinin tahmini
kabul edilmez. Çalışan sayıları ve gelirler hızla değişiyor ve sık sık yanlış aktarılıyor; bir bilgi
doğrulanamıyorsa **tahmin etmek yerine `bilinmiyor` yazın**. "Bilinmiyor" burada gerçek bir cevaptır,
makul görünen bir şeyle doldurulacak bir boşluk değil.

Kaynağın bağlama ihtiyacı varsa — rakam şirketin kendi beyanıysa, çalışan sayısı basın tahminiyse,
staj 2024'te açılmış ve tekrarlanmayabilecekse — bunu alanın içine yazın. Mevcut kayıtlar zaten böyle
yapıyor (`350+ (Mobidictum 2025)`, `evet — yaz stajı (ofis, 2024 örneği)`).

### Ne katkı verilebilir

| | |
|---|---|
| **Daha iyi İngilizce** | `data/*.en.csv` Türkçeden makine çevirisidir, **insan eliyle gözden geçirilmedi** — düzeltmek en iyi ilk katkıdır |
| **Eksik şirket** | İki listeden birine giren stüdyo, yayıncı, hizmet sağlayıcı veya ekosistem aktörü |
| **Düzeltme** | Şirket kapanmış, satın alınmış, şehir değiştirmiş, ad değiştirmiş, çalışan veya sahiplik güncellenmiş |
| **Derinleştirme** | `bilinmiyor` alanlarını kaynaklı bilgiyle doldurmak — özellikle staj, uzaktan çalışma ve fon notları |

### Çeviri — en kolay işe yarar katkı

`data/turkey.tr.csv` ve `data/global.tr.csv` **asıl kaynaktır**. `data/turkey.en.csv` ve
`data/global.en.csv` bunlardan OpenAI ile üretildi ve **kimse satır satır okumadı**. Yanlış çevrilmiş
tür adları, tuhaf staj notları, Türkçe kalması gereken şehir adları ve anlamını yitirmiş serbest metin
notları bulacaksınız.

Bunları düzeltmek için araştırma yapmanız gerekmiyor — yalnızca İngilizce satırın yanındaki Türkçe
satırı okumanız yeterli. Lütfen **bir dosyayı ya da bir dosyanın sınırları belli bir bölümünü** bir
seferde bitirin ki veri yarı düzeltilmiş halde kalmasın. Türkçe ile İngilizce bir bilgide çelişiyorsa
Türkçe geçerlidir; Türkçenin kendisi yanlış görünüyorsa önce onu düzeltin ve pull request'te belirtin.

### Sütunlar

İki dilde de aynı on üç sütun, aynı sırayla:

| Türkçe | İngilizce | Not |
|---|---|---|
| `Firma` | `Company` | Şirketin kendini yazdığı ad |
| `Bölge` | `Region` | Ülke; Türkiye listesinde bölge |
| `Şehir` | `City` | Şehir, gerekiyorsa parantez içinde ofisler |
| `Kuruluş` | `Founded` | Kuruluş yılı |
| `Çalışan` | `Employees` | Çalışan sayısı, **kaynağı ve tarihiyle** |
| `Gelir_fon` | `Revenue_funding` | Gelir, yatırım turu veya değerleme sinyalleri |
| `Web` | `Web` | Resmî site, `https://`, takip parametresiz |
| `Türler` | `Genres` | Türler, `/` ile ayrılmış |
| `Örnek_oyunlar` | `Sample_games` | Birkaç temsilî oyun, `;` ile ayrılmış |
| `Staj` | `Internship` | Staj hakkında bilinenler ve hangi yıla ait olduğu |
| `Uzaktan` | `Remote` | Uzaktan / hibrit / ofis |
| `Sahiplik` | `Ownership` | Bağımsız, ana şirket, yatırımcı |
| `Not` | `Notes` | Serbest metin — okurun bilmesi gereken her şey |

Alan içindeki maddeler noktalı virgülle ayrılır; virgül içeren alan tırnaklanır, her CSV'de olduğu
gibi. Sütun eklemeyin, silmeyin, sırasını değiştirmeyin ve başlık satırına dokunmayın — üretici
betikler onu okuyor.

### Nasıl

1. **`data/`** içindeki CSV'leri düzenleyin. Türkçe dosyalar asıl kaynaktır; `catalogue/`,
   `docs/data/*.json` ve `docs/files/` **üretilmiş** dosyalardır, elle düzenlemeyin.
2. Türetilmiş dosyaları yeniden üretin:

   ```bash
   python3 scripts/build.py
   ```

   Yalnızca yeniden çeviri yapıyorsanız (genelde gerekmez, `*.en.csv` dosyasını elle düzeltmek daha
   iyidir):

   ```bash
   export OPENAI_API_KEY=...
   python3 scripts/translate.py
   ```

3. Neyi değiştirdiğinizi ve nereden doğruladığınızı anlatan bir pull request açın. **Türkçe ya da
   İngilizce pull request ve issue'lar eşit derecede memnuniyetle karşılanır.**

CSV ile uğraşmak istemiyorsanız **sadece issue açın** — şirket adı ve bir bağlantı yeterli. Bu da
gerçekten işe yarar bir katkıdır, veri girişini biri yapar.

### Bilinen sınırlar — her biri bir katkı fırsatı

Atlasın en zayıf olduğu, dolayısıyla katkının en çok işe yaradığı yerler:

- **Çalışan ve gelir** çoğu zaman tahmin ya da şirket beyanıdır; kaynaklı ve tarihli bir düzeltme her
  zaman iyileştirmedir.
- **`bilinmiyor`**, bilginin kamuya açık kaynakta bulunamadığı anlamına gelir; var olmadığı anlamına
  gelmez. Şirketi tanıyan biri bunların çoğunu kapatabilir.
- **Staj notları** açık bir pozisyondan çok geçmiş bir yılda açılmış programı anlatıyor olabilir.
  Hangi yıla ait olduğunu söyleyen not, söylemeyenden iyidir.
- **Türkiye listesi tam sayım değildir.** Küçük ve yeni stüdyolar eksik temsil ediliyor.
- **İngilizce alanlar gözden geçirilmemiş makine çevirisidir**, yukarıda anlatıldığı gibi.

### Kapsam

**Oyun üreten, yayınlayan veya doğrudan oyuna hizmet veren** şirketler: stüdyolar, yayıncılar, port ve
QA firmaları, ses ve sanat dış kaynak ekipleri, oyun motoru ve araç sağlayıcıları, bir de bunların
etrafındaki fonlar, hızlandırıcılar ve dernekler. Portföyünde bir oyun bulunan genel yazılım
danışmanlıkları, pazarlama ajansları ve bireysel serbest çalışanlar — ne kadar iyi olurlarsa olsunlar
— kapsam dışı.

---

## Code of conduct

Be decent to each other. Disagreements about a fact are settled by looking at the company's own page,
not by argument. Contributions are credited in the commit history; if you would like to be named in
the README as a contributor, say so in your pull request.
