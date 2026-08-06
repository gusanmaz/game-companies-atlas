#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build GitHub Pages site for Game Companies Atlas."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
CAT = ROOT / "catalogue"

CONTRIBUTE_URL = "https://github.com/gusanmaz/game-companies-atlas/blob/main/CONTRIBUTING.md"

# Column catalogue for the table pages.
#   key      – row key in the JSON payload
#   tr / en  – bilingual header label
#   min      – floor width in px; a column is never rendered narrower than this
#   weight   – share of the width left over once every column has its floor
#   cls      – styling hint (name / num / mid / long)
# The floors were measured from the rendered fonts: each is wide enough for the
# longer of the two header labels and for the 90th-percentile unbreakable word in
# the data, so headers are not truncated and values like "bilinmiyor" do not wrap
# mid-word. Weights then favour the prose columns when a wide screen has room to
# spare, keeping year and headcount narrow.
# Every column is visible by default; users may hide or reorder them from the column manager.
COLUMN_DEFS = [
    ("company",    "Firma",         "Company",            94, 30, "c-name"),
    ("region",     "Bölge",         "Region",             88,  4, "c-mid"),
    ("city",       "Şehir",         "City",               94,  6, "c-mid"),
    ("founded",    "Kuruluş",       "Founded",            88,  2, "c-num"),
    ("employees",  "Çalışan",       "Employees",         100,  3, "c-num"),
    ("funding",    "Gelir / fon",   "Revenue / funding",  92, 11, "c-long"),
    ("genres",     "Tür",           "Genres",            100,  8, "c-mid"),
    ("games",      "Örnek oyunlar", "Sample games",       96, 13, "c-long"),
    ("internship", "Staj",          "Internship",        104,  3, "c-mid"),
    ("remote",     "Uzaktan",       "Remote",             86,  2, "c-mid"),
    ("ownership",  "Sahiplik",      "Ownership",         100,  7, "c-mid"),
    ("notes",      "Not",           "Notes",             118, 25, "c-long"),
]

COLUMN_KEYS = [c[0] for c in COLUMN_DEFS]


def column_meta(lang: str) -> list[dict]:
    idx = 1 if lang == "tr" else 2
    return [
        {"k": c[0], "label": c[idx], "min": c[3], "w": c[4], "cls": c[5]}
        for c in COLUMN_DEFS
    ]


# Bumped whenever the default column set changes so that stale localStorage
# values cannot trap returning visitors in an outdated layout.
STORAGE_VERSION = "v2"

UI = {
    "tr": {
        "lang": "tr",
        "brand": "Oyun Firmaları Atlası",
        "title_home": "Oyun Firmaları Atlası — Türkiye ve küresel stüdyolar",
        "lead": "Türkiye’de {turkey}, dünyada (TR hariç) {global} oyun stüdyosu/yayıncı kaydı. Staj, uzaktan çalışma, sahiplik ve örnek oyunlarla birlikte.",
        "byline": "Güvenç Usanmaz · Ağustos 2026",
        "turkey": "Türkiye firmaları",
        "global": "Küresel firmalar",
        "browse": "Tabloda gez",
        "download": "İndir",
        "search": "Firma, şehir, tür veya oyun ara…",
        "all_regions": "Tüm bölgeler",
        "records": "kayıt",
        "weak": "zayıf veri",
        "unknown_note": "Bilinmiyor = kamuya açık kaynakta bulunamadı.",
        "warn_global": "Türk firmalar bu listede yok — Türkiye listesine bakın.",
        "warn_turkey": "Küresel (TR dışı) liste ayrı sayfada.",
        "home": "Ana sayfa",
        "lead_turkey": "Türkiye’deki oyun stüdyoları, yayıncılar ve ekosistem aktörleri. Sütun başlığına tıklayarak sıralayın; arama, bölge, şehir, kuruluş yılı, çalışan sayısı, tür, sahiplik, staj ve uzaktan çalışma filtreleriyle daraltın. Sütunları gizleyebilir ve sırasını değiştirebilirsiniz.",
        "lead_global": "Türkiye dışındaki büyük stüdyolar, yayıncılar ve platformlar. Sütun başlığına tıklayarak sıralayın; arama, bölge, şehir, kuruluş yılı, çalışan sayısı, tür, sahiplik, staj ve uzaktan çalışma filtreleriyle daraltın. Sütunları gizleyebilir ve sırasını değiştirebilirsiniz.",
        "disclaimer": (
            "Uyarı: Bu dizin eksik veya hatalı kayıtlar içerebilir. Çalışan sayısı, gelir/fon ve staj bilgileri "
            "çoğunlukla tahmindir veya kamuya açık kaynaklardan alınmıştır; güncelliğini yitirmiş olabilir. "
            "Tamlık veya doğruluk konusunda garanti veya teminat yoktur."
        ),
        "contribute_title": "Katkıda bulunun",
        "contribute_body": (
            "Eksik firma, düzeltme veya güncel bilgi eklemek isterseniz katkılarınızı bekleriz. "
            f'<a href="{CONTRIBUTE_URL}" target="_blank" rel="noopener">Katkı rehberine</a> bakın.'
        ),
        "contribute_footer": f'<a href="{CONTRIBUTE_URL}" target="_blank" rel="noopener">Katkı</a>',
        "columns_label": "Sütunlar",
        "lang_label": "Dil",
        "filter_heading": "Ara ve filtrele",
        "search_label": "Ara",
        "region_label": "Bölge",
        "sort_hint": "Sütun başlığına tıklayın ya da “Sırala” kutusunu kullanın.",
        "sorted_by": "Sıralama",
        "sort_asc": "artan",
        "sort_desc": "azalan",
        "clear_filters": "Filtreleri temizle",
        "active_filters": "aktif filtre",
        # sorting
        "sort_label": "Sırala",
        "sort_dir_label": "Sıralama yönünü değiştir",
        "sort_by_col": "Sütuna göre sırala",
        # column manager
        "columns_title": "Sütun yönetimi",
        "columns_hint": (
            "Kutucukla göster/gizle; sürükleyerek ya da ok düğmeleriyle sırayı değiştirin."
        ),
        "columns_reset": "Varsayılana dön",
        "columns_all": "Tümünü göster",
        "columns_close": "Kapat",
        "move_up": "Yukarı taşı",
        "move_down": "Aşağı taşı",
        "col_visible": "Sütunu göster",
        "col_locked": "Bu sütun her zaman görünür",
        "columns_count": "sütun görünür",
        # filters
        "city_label": "Şehir",
        "all_cities": "Tüm şehirler",
        "genre_label": "Tür",
        "all_genres": "Tüm türler",
        "ownership_label": "Sahiplik",
        "all_ownership": "Tüm sahiplik türleri",
        "founded_label": "Kuruluş yılı",
        "year_from": "en erken",
        "year_to": "en geç",
        "size_label": "Çalışan sayısı",
        "size_any": "Fark etmez",
        "size_unknown": "Bilinmiyor",
        "size_bands": ["1–10", "11–50", "51–200", "201–1000", "1000+"],
        "internship_label": "Staj",
        "intern_any": "Fark etmez",
        "intern_yes": "Evet",
        "intern_info": "Bilgi var",
        "intern_unknown": "Bilinmiyor",
        "remote_label": "Uzaktan çalışma",
        "remote_any": "Fark etmez",
        "remote_flex": "Uzaktan / hibrit",
        "remote_office": "Ofis",
        "remote_unknown": "Bilinmiyor",
        "no_results": "Bu filtrelerle eşleşen kayıt yok.",
        "no_results_hint": "Aramayı kısaltmayı ya da filtreleri temizlemeyi deneyin.",
        "loading": "Yükleniyor…",
    },
    "en": {
        "lang": "en",
        "brand": "Game Companies Atlas",
        "title_home": "Game Companies Atlas — Türkiye and global studios",
        "lead": "{turkey} companies in Türkiye and {global} global studios/publishers (excl. Türkiye), with internship, remote work, ownership and sample games.",
        "byline": "Güvenç Usanmaz · August 2026",
        "turkey": "Türkiye companies",
        "global": "Global companies",
        "browse": "Browse table",
        "download": "Download",
        "search": "Search company, city, genre or game…",
        "all_regions": "All regions",
        "records": "records",
        "weak": "weak data",
        "unknown_note": "Unknown = not found in public sources.",
        "warn_global": "Turkish companies are not listed here — see the Türkiye list.",
        "warn_turkey": "Global (non-TR) list is on a separate page.",
        "home": "Home",
        "lead_turkey": "Game studios, publishers and ecosystem actors based in Türkiye. Click a column header to sort; narrow the list by search, region, city, founding year, company size, genre, ownership, internship and remote work. Columns can be hidden and reordered.",
        "lead_global": "Major studios, publishers and platforms outside Türkiye. Click a column header to sort; narrow the list by search, region, city, founding year, company size, genre, ownership, internship and remote work. Columns can be hidden and reordered.",
        "disclaimer": (
            "Disclaimer: This directory may contain gaps or inaccuracies. Headcount, revenue/funding and internship "
            "figures are often estimates or drawn from public sources and may be outdated. There is no warranty or "
            "guarantee of completeness or correctness."
        ),
        "contribute_title": "Contribute",
        "contribute_body": (
            "Corrections, missing companies and fresher public data are welcome. "
            f'See the <a href="{CONTRIBUTE_URL}" target="_blank" rel="noopener">contributing guide</a>.'
        ),
        "contribute_footer": f'<a href="{CONTRIBUTE_URL}" target="_blank" rel="noopener">Contribute</a>',
        "columns_label": "Columns",
        "lang_label": "Language",
        "filter_heading": "Search and filter",
        "search_label": "Search",
        "region_label": "Region",
        "sort_hint": "Click a column header, or use the “Sort by” control.",
        "sorted_by": "Sorted by",
        "sort_asc": "ascending",
        "sort_desc": "descending",
        "clear_filters": "Clear filters",
        "active_filters": "active filters",
        # sorting
        "sort_label": "Sort by",
        "sort_dir_label": "Toggle sort direction",
        "sort_by_col": "Sort by this column",
        # column manager
        "columns_title": "Column manager",
        "columns_hint": (
            "Tick to show or hide; drag a row or use the arrow buttons to reorder."
        ),
        "columns_reset": "Reset to defaults",
        "columns_all": "Show all",
        "columns_close": "Close",
        "move_up": "Move up",
        "move_down": "Move down",
        "col_visible": "Show column",
        "col_locked": "This column is always visible",
        "columns_count": "columns visible",
        # filters
        "city_label": "City",
        "all_cities": "All cities",
        "genre_label": "Genre",
        "all_genres": "All genres",
        "ownership_label": "Ownership",
        "all_ownership": "All ownership types",
        "founded_label": "Founded year",
        "year_from": "from",
        "year_to": "to",
        "size_label": "Company size",
        "size_any": "Any size",
        "size_unknown": "Unknown",
        "size_bands": ["1–10", "11–50", "51–200", "201–1000", "1000+"],
        "internship_label": "Internship",
        "intern_any": "Any",
        "intern_yes": "Yes",
        "intern_info": "Has info",
        "intern_unknown": "Unknown",
        "remote_label": "Remote work",
        "remote_any": "Any",
        "remote_flex": "Remote / hybrid",
        "remote_office": "Office",
        "remote_unknown": "Unknown",
        "no_results": "No records match these filters.",
        "no_results_hint": "Try a shorter search term or clear the filters.",
        "loading": "Loading…",
    },
}

CSS = """
:root{
  --ink:#1a2330;--muted:#5a6575;--paper:#f4f1ea;--card:#fffdf8;--line:#d8d0c2;
  --navy:#1e3a5f;--navy2:#2d5a87;--teal:#146b57;--teal2:#0e5544;--chip:#eef3f8;
  --warn:#8a5a12;--warn-bg:#fff8eb;--warn-line:#d4a24a;
  --r:10px;--shadow:0 1px 3px rgba(30,58,95,.07);--shadow-lg:0 12px 32px rgba(30,58,95,.16);
  --ring:0 0 0 3px rgba(45,90,135,.32);--bleed:min(2100px,96vw);
}
*{box-sizing:border-box}
body{margin:0;font-family:"Source Sans 3",system-ui,sans-serif;color:var(--ink);
background:radial-gradient(1100px 480px at 8% -8%,#d7e6f5 0%,transparent 55%),
radial-gradient(900px 420px at 100% 0%,#e7dfd1 0%,transparent 50%),var(--paper);line-height:1.55}
a{color:var(--teal2);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:2rem 1.15rem 3.5rem}
@media(min-width:1400px){.wrap:not(.list){max-width:1400px}}
/* A list page widens as one block, so the masthead rule, headings and notices
   end on the same line as the table rather than floating in a narrower column. */
@media(min-width:1100px){.wrap.list{max-width:var(--bleed)}}
.bleed{margin-top:1.15rem}
.top{display:flex;flex-wrap:wrap;gap:.75rem 1rem;align-items:center;justify-content:space-between;
margin-bottom:1.4rem;padding-bottom:.9rem;border-bottom:2px solid var(--navy)}
.brand{font-family:"Source Serif 4",Georgia,serif;font-weight:700;font-size:1.15rem;color:var(--navy);text-decoration:none}
.nav{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.nav a,.btn{display:inline-flex;align-items:center;padding:.45rem .85rem;border-radius:8px;
border:1px solid var(--navy);color:var(--navy);background:#fff;font-weight:600;font-size:.92rem;text-decoration:none}
.nav a:hover,.btn:hover{background:var(--chip);text-decoration:none}
.nav a.on,.btn.primary{background:var(--navy);color:#fff}
.langs{display:inline-flex;gap:.35rem;margin-left:.25rem;padding-left:.55rem;border-left:1px solid var(--line)}
.langs a{min-width:4.6rem;justify-content:center}
.hero h1{font-family:"Source Serif 4",Georgia,serif;font-size:clamp(1.8rem,4vw,2.55rem);
margin:0 0 .5rem;color:var(--navy);letter-spacing:-.02em;line-height:1.15}
.lead{margin:0;color:var(--muted);max-width:46rem;font-size:1.05rem}
.by{margin:.8rem 0 0;font-weight:600;color:var(--navy)}
.grid{display:grid;gap:1.1rem;margin-top:1.6rem}
@media(min-width:780px){.grid{grid-template-columns:1fr 1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1.25rem 1.3rem;
box-shadow:0 1px 3px rgba(30,58,95,.06);display:flex;flex-direction:column;gap:.85rem}
.card h2{font-family:"Source Serif 4",Georgia,serif;margin:0;font-size:1.25rem;color:var(--navy)}
.meta{margin:0;color:var(--muted);font-size:.95rem}
.actions{display:flex;flex-wrap:wrap;gap:.5rem}
.dl{display:flex;flex-wrap:wrap;gap:.55rem .9rem;padding-top:.75rem;border-top:1px solid var(--line);
font-size:.92rem;color:var(--muted)}
.dl a{color:var(--navy);font-weight:600}
.contribute{margin-top:1.5rem;padding:1.1rem 1.2rem;background:var(--card);border:1px solid var(--line);
border-radius:10px}
.contribute h2{font-family:"Source Serif 4",Georgia,serif;margin:0 0 .45rem;font-size:1.15rem;color:var(--navy)}
.contribute p{margin:0;color:var(--muted);font-size:.95rem}
footer{margin-top:2.2rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted);font-size:.88rem}
/* ── search & filter panel ─────────────────────────────── */
.controls{padding:1rem 1.1rem 1.05rem;background:var(--card);border:1px solid var(--line);
border-radius:var(--r);box-shadow:var(--shadow)}
.controls-head{display:flex;flex-wrap:wrap;gap:.3rem 1rem;align-items:baseline;justify-content:space-between;
margin-bottom:.85rem}
.controls-title{margin:0;font-family:"Source Serif 4",Georgia,serif;font-size:1.08rem;color:var(--navy)}
.sort-hint{margin:0;font-size:.86rem;color:var(--muted)}
.filters{display:grid;gap:.7rem .8rem;grid-template-columns:repeat(auto-fit,minmax(176px,1fr))}
.field{display:flex;flex-direction:column;gap:.28rem;min-width:0}
.field > .flabel{font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--navy2)}
.field input,.field select{font:inherit;font-size:.94rem;padding:.5rem .6rem;border:1.5px solid var(--line);
border-radius:8px;background:#fff;color:var(--ink);min-height:2.5rem;width:100%;min-width:0}
.field input:focus,.field select:focus{outline:none;border-color:var(--navy);box-shadow:var(--ring)}
@media(min-width:640px){.field-search{grid-column:span 2}}
.pair{display:flex;gap:.4rem;align-items:center}
.pair input{text-align:center}
.pair select{flex:1 1 auto}
.dir-btn{flex:0 0 auto;width:2.6rem;min-height:2.5rem;border:1.5px solid var(--navy);border-radius:8px;
background:var(--navy);color:#fff;font-size:1rem;font-weight:700;cursor:pointer;
display:inline-flex;align-items:center;justify-content:center}
.dir-btn:hover{background:var(--navy2)}
.dir-btn:focus-visible{outline:none;box-shadow:var(--ring)}
.controls-foot{display:flex;flex-wrap:wrap;gap:.6rem .9rem;align-items:center;justify-content:space-between;
margin-top:.9rem;padding-top:.75rem;border-top:1px dashed var(--line)}
.status-row{display:flex;flex-wrap:wrap;gap:.4rem .7rem;align-items:center}
.btn-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.count{color:var(--ink);font-size:.92rem;font-weight:700}
.count b{color:var(--navy);font-size:1.02rem}
.sort-status{display:inline-flex;align-items:center;gap:.3rem;padding:.24rem .6rem;border-radius:999px;
background:var(--chip);border:1px solid var(--navy2);color:var(--navy);font-size:.82rem;font-weight:700}
.filter-pill{display:inline-flex;align-items:center;padding:.24rem .6rem;border-radius:999px;
background:#fff4d6;border:1px solid var(--warn-line);color:var(--warn);font-size:.82rem;font-weight:700}
.filter-pill[hidden]{display:none!important}
.btn-ghost{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem .8rem;border-radius:8px;
border:1.5px solid var(--navy);color:var(--navy);background:#fff;font:inherit;font-weight:700;font-size:.88rem;
cursor:pointer}
.btn-ghost:hover{background:var(--chip)}
.btn-ghost:focus-visible{outline:none;box-shadow:var(--ring)}
.btn-ghost[aria-expanded=true]{background:var(--navy);color:#fff}
.btn-ghost[hidden]{display:none!important}
/* ── column manager ────────────────────────────────────── */
.colmgr{margin-top:.9rem;padding:.85rem .95rem 1rem;border:1.5px solid var(--navy2);border-radius:var(--r);
background:#f7fafe}
.colmgr[hidden]{display:none}
.colmgr-head{display:flex;flex-wrap:wrap;gap:.4rem .9rem;align-items:center;justify-content:space-between}
.colmgr-head h3{margin:0;font-family:"Source Serif 4",Georgia,serif;font-size:1rem;color:var(--navy)}
.colmgr-hint{flex:1 1 100%;margin:.15rem 0 .7rem;font-size:.84rem;color:var(--muted)}
.collist{list-style:none;margin:0;padding:0;display:grid;gap:.45rem;
grid-template-columns:repeat(auto-fill,minmax(232px,1fr))}
.colitem{display:flex;align-items:center;gap:.4rem;padding:.32rem .45rem;background:#fff;
border:1px solid var(--line);border-radius:8px}
.colitem.dragging{opacity:.35}
.colitem.over{border-color:var(--navy);box-shadow:var(--ring)}
.colitem.off{background:#f2f1ee}
.colitem.off label{color:var(--muted)}
.colitem .idx{flex:0 0 1.4rem;height:1.4rem;border-radius:50%;background:var(--chip);color:var(--navy2);
font-size:.7rem;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.colitem .grip{flex:0 0 auto;color:var(--muted);cursor:grab;font-size:1rem;line-height:1;padding:0 .1rem}
.colitem label{display:flex;align-items:center;gap:.4rem;flex:1 1 auto;min-width:0;font-size:.88rem;
font-weight:600;cursor:pointer}
.colitem label .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.colitem input[type=checkbox]{flex:0 0 auto;width:1rem;height:1rem;accent-color:var(--navy)}
.mini{flex:0 0 auto;width:1.7rem;height:1.7rem;border:1px solid var(--line);border-radius:6px;background:#fff;
color:var(--navy);cursor:pointer;font-size:.78rem;line-height:1;padding:0;
display:inline-flex;align-items:center;justify-content:center}
.mini:hover:not(:disabled){background:var(--chip);border-color:var(--navy)}
.mini:focus-visible{outline:none;box-shadow:var(--ring)}
.mini:disabled{opacity:.28;cursor:default}
/* ── table ─────────────────────────────────────────────── */
.table-wrap{margin-top:.9rem;overflow:auto;max-height:min(74vh,880px);border:1px solid var(--line);
border-radius:var(--r);background:#fff;box-shadow:var(--shadow);overscroll-behavior-x:contain}
.table-wrap[hidden],.cards[hidden],.empty[hidden]{display:none!important}
table.atlas{border-collapse:separate;border-spacing:0;table-layout:fixed;width:100%;
min-width:var(--tmin,900px);font-size:13.5px}
.atlas th,.atlas td{text-align:left;vertical-align:top;border-bottom:1px solid #e9e4da;overflow-wrap:anywhere}
.atlas td{padding:8px 11px}
.atlas td.c-num{font-variant-numeric:tabular-nums}
.atlas thead th{position:sticky;top:0;z-index:3;padding:0;background:#e7edf5;
border-bottom:2px solid var(--navy2)}
.th-btn{display:flex;align-items:flex-start;gap:.3rem;width:100%;padding:9px 10px;border:0;background:transparent;
font:inherit;font-size:11.5px;font-weight:700;letter-spacing:.02em;text-transform:uppercase;color:var(--navy2);
text-align:left;cursor:pointer;line-height:1.25}
/* Headers wrap rather than truncate: a clipped label hides which column you are
   sorting, and forcing every label onto one line starves the data columns. */
.th-btn .nm{flex:1 1 auto;min-width:0;overflow-wrap:break-word}
.th-btn .ico{flex:0 0 auto;font-size:.9rem;opacity:.45}
.th-btn:hover{background:#d7e2f0;color:var(--navy)}
.th-btn:hover .ico{opacity:.9}
.th-btn:focus-visible{outline:2px solid var(--navy);outline-offset:-3px}
.atlas th[aria-sort=ascending],.atlas th[aria-sort=descending]{background:var(--navy)}
.atlas th[aria-sort=ascending] .th-btn,.atlas th[aria-sort=descending] .th-btn{color:#fff}
.atlas th[aria-sort=ascending] .th-btn:hover,.atlas th[aria-sort=descending] .th-btn:hover{background:var(--navy2)}
.atlas th[aria-sort=ascending] .ico,.atlas th[aria-sort=descending] .ico{opacity:1}
.atlas .stick{position:sticky;left:0;z-index:2;background:#fff;box-shadow:1px 0 0 var(--line)}
.atlas thead th.stick{z-index:4;background:#e7edf5}
.atlas tbody td.stick{font-weight:600}
.atlas tbody tr:nth-child(even) td,.atlas tbody tr:nth-child(even) td.stick{background:#fbfaf7}
.atlas tbody tr:hover td,.atlas tbody tr:hover td.stick{background:#edf3fb}
.atlas tbody td.sorted{background:#eaf1fa}
.atlas tbody tr:nth-child(even) td.sorted{background:#e5eef9}
.atlas tbody tr:hover td.sorted{background:#dde9f7}
/* ── card list (small screens) ─────────────────────────── */
.cards{display:grid;gap:.7rem;margin-top:.9rem}
.rowcard{background:#fff;border:1px solid var(--line);border-left:4px solid var(--navy2);
border-radius:var(--r);padding:.8rem .9rem;box-shadow:var(--shadow)}
.rowcard h3{margin:0 0 .55rem;font-family:"Source Serif 4",Georgia,serif;font-size:1.05rem;
line-height:1.25;color:var(--navy)}
.rowcard dl{display:grid;grid-template-columns:minmax(5rem,7rem) 1fr;gap:.3rem .7rem;margin:0;font-size:.9rem}
.rowcard dt{font-size:.68rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
color:var(--navy2);padding-top:.18rem}
.rowcard dd{margin:0;overflow-wrap:anywhere}
@media(max-width:400px){
  .rowcard dl{grid-template-columns:1fr;gap:.05rem}
  .rowcard dd{margin:0 0 .4rem}
}
.empty{margin-top:.9rem;padding:2.4rem 1rem;text-align:center;color:var(--muted);background:#fff;
border:1px dashed var(--line);border-radius:var(--r)}
.empty strong{display:block;margin-bottom:.25rem;color:var(--ink);font-size:1.05rem}
.badge{display:inline-block;font-size:11px;padding:2px 7px;border-radius:4px;background:var(--chip);color:var(--muted);border:1px solid var(--line)}
.warn{background:#fff;border:1px solid var(--line);border-left:3px solid var(--teal);border-radius:8px;
padding:.85rem 1rem;margin:0 0 .75rem;color:var(--muted);font-size:.93rem}
.warn.disclaimer{background:var(--warn-bg);border-color:var(--warn-line);border-left-color:var(--warn);
color:var(--warn);font-weight:600}
@media(max-width:560px){
  .wrap{padding:1.25rem .8rem 2.5rem}
  .controls{padding:.85rem .8rem .9rem}
  .filters{gap:.6rem;grid-template-columns:1fr 1fr}
  .field-search{grid-column:span 2}
  .btn-row,.status-row{width:100%}
  .btn-ghost{flex:1 1 auto;justify-content:center}
  .collist{grid-template-columns:1fr}
}
@media(max-width:380px){.filters{grid-template-columns:1fr}.field-search{grid-column:span 1}}
"""


def load_csv(path: Path, lang: str) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    if lang == "tr":
        mapping = {
            "company": "Firma",
            "region": "Bölge",
            "city": "Şehir",
            "founded": "Kuruluş",
            "employees": "Çalışan",
            "funding": "Gelir_fon",
            "web": "Web",
            "genres": "Türler",
            "games": "Örnek_oyunlar",
            "internship": "Staj",
            "remote": "Uzaktan",
            "ownership": "Sahiplik",
            "notes": "Not",
        }
    else:
        mapping = {
            "company": "Company",
            "region": "Region",
            "city": "City",
            "founded": "Founded",
            "employees": "Employees",
            "funding": "Revenue_funding",
            "web": "Web",
            "genres": "Genres",
            "games": "Sample_games",
            "internship": "Internship",
            "remote": "Remote",
            "ownership": "Ownership",
            "notes": "Notes",
        }
    for r in rows:
        item = {k: (r.get(src) or "").strip() for k, src in mapping.items()}
        out.append(item)
    return out


def write_json(name: str, lang: str, rows: list[dict]) -> None:
    dest = DOCS / "data" / f"{name}.{lang}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def lang_switcher(lang: str, page: str) -> str:
    """Both language links always visible; active language marked with .on."""
    u = UI[lang]
    tr_cls = "on" if lang == "tr" else ""
    en_cls = "on" if lang == "en" else ""
    return f"""<span class="langs" role="navigation" aria-label="{u['lang_label']}">
        <a class="{tr_cls}" href="../tr/{page}" hreflang="tr" lang="tr">Türkçe</a>
        <a class="{en_cls}" href="../en/{page}" hreflang="en" lang="en">English</a>
      </span>"""


def page_shell(title: str, body: str, lang: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,700&display=swap" rel="stylesheet"/>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def build_home(lang: str, counts: dict[str, int]) -> str:
    u = UI[lang]
    files = "../files"
    lead = u["lead"].format(turkey=counts["turkey"], **{"global": counts["global"]})
    body = f"""
<div class="wrap">
  <div class="top">
    <a class="brand" href="index.html">{u['brand']}</a>
    <nav class="nav">
      <a class="on" href="index.html">{u['home']}</a>
      <a href="turkey.html">{u['turkey']}</a>
      <a href="global.html">{u['global']}</a>
      {lang_switcher(lang, "index.html")}
    </nav>
  </div>
  <header class="hero">
    <h1>{u['brand']}</h1>
    <p class="lead">{lead}</p>
    <p class="by">{u['byline']}</p>
  </header>
  <div class="warn disclaimer">{u['disclaimer']}</div>
  <section class="grid">
    <article class="card">
      <h2>{u['turkey']}</h2>
      <p class="meta">{counts['turkey']} {u['records']}</p>
      <div class="actions">
        <a class="btn primary" href="turkey.html">{u['browse']}</a>
      </div>
      <div class="dl">
        <span>{u['download']}:</span>
        <a href="{files}/TURKEY.{lang}.md">Markdown</a>
        <a href="{files}/turkey.{lang}.csv">CSV</a>
        <a href="{files}/turkey.tr.xlsx">Excel</a>
        <a href="{files}/turkey.tr.pdf">PDF</a>
      </div>
    </article>
    <article class="card">
      <h2>{u['global']}</h2>
      <p class="meta">{counts['global']} {u['records']}</p>
      <div class="actions">
        <a class="btn primary" href="global.html">{u['browse']}</a>
      </div>
      <div class="dl">
        <span>{u['download']}:</span>
        <a href="{files}/GLOBAL.{lang}.md">Markdown</a>
        <a href="{files}/global.{lang}.csv">CSV</a>
        <a href="{files}/global.tr.xlsx">Excel</a>
        <a href="{files}/global.tr.pdf">PDF</a>
      </div>
    </article>
  </section>
  <section class="contribute">
    <h2>{u['contribute_title']}</h2>
    <p>{u['contribute_body']}</p>
  </section>
  <footer>GitHub Pages · <a href="https://github.com/gusanmaz/game-companies-atlas">gusanmaz/game-companies-atlas</a>
  · {u['contribute_footer']}</footer>
</div>
"""
    return page_shell(u["title_home"], body, lang)


# Client-side behaviour for the table pages. Kept as a plain (non f-string)
# template so the JavaScript can use braces normally; __TOKENS__ are substituted
# by build_list_page().
LIST_JS = r"""
const CDEF = __CDEF__;
const T = __T__;
const LANG = __LANG__;
const SRC = __SRC__;
const SKEY = __SKEY__;
const SKEY_OLD = __SKEY_OLD__;

const ALL_KEYS = CDEF.map(function(c){ return c.k; });
const DEF_ORDER = ALL_KEYS.slice();
const META = {};
CDEF.forEach(function(c){ META[c.k] = c; });

let rows = [];
let order = DEF_ORDER.slice();
let visible = new Set(ALL_KEYS);
let sortKey = 'company';
let sortDir = 1;
let dragKey = null;

const $ = function(id){ return document.getElementById(id); };
const collator = new Intl.Collator(LANG, { numeric: true, sensitivity: 'base' });
const cardMQ = window.matchMedia('(max-width: 860px)');

function esc(s){
  return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
  });
}

// Diacritic-insensitive key so "istanbul" matches "İstanbul" and "sehir" matches "şehir".
function norm(s){
  return String(s == null ? '' : s)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ı/g, 'i');
}

function label(k){ return (META[k] && META[k].label) || k; }

/* ── defensive parsing of the free-text data ──────────────────────────── */

function unknownish(v){
  const t = norm(v).trim();
  if (!t || t === '-' || t === '—' || t === '–' || t === '?' || t === 'n/a') return true;
  return /(^|[^a-z])(bilinmiyor|unknown|belirsiz)([^a-z]|$)/.test(t);
}

// Collapses the qualifiers the data attaches to city names so that the filter
// offers one option per city:
//   "İstanbul (Şişli; Londra ofisi)" -> "İstanbul"
//   "Los Angeles, CA"                -> "Los Angeles"
//   "Gebze / Bilişim Vadisi"         -> "Gebze"
//   "Ankara + İstanbul"              -> "Ankara"
//   "Eskişehir ofisi"                -> "Eskişehir"
function cityKey(v){
  const t = String(v || '')
    .split(/[(;\/+,]/)[0]
    .trim()
    .replace(/[,\s.]+$/, '')
    .replace(/\s+(ofisi|ofis|office|studio|hq)$/i, '')
    .trim();
  return unknownish(t) ? '' : t;
}

// "2012/2013" -> 2012;  "bilinmiyor" -> null
function yearOf(v){
  const m = String(v || '').match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return m ? parseInt(m[1], 10) : null;
}

// "350+ (Mobidictum 2025)" -> 350;  "~50-100" -> 75;  "küçük" -> null
function sizeOf(v){
  const t = String(v || '').replace(/\([^)]*\)/g, ' ');
  const nums = (t.match(/\d[\d.,]*/g) || [])
    .map(function(x){ return parseInt(x.replace(/[.,]/g, ''), 10); })
    .filter(function(n){ return Number.isFinite(n) && n > 0; });
  if (!nums.length) return null;
  if (nums.length === 1) return nums[0];
  return Math.round((Math.min.apply(null, nums) + Math.max.apply(null, nums)) / 2);
}

const BANDS = [[1, 10], [11, 50], [51, 200], [201, 1000], [1001, Infinity]];
function bandOf(n){
  if (n === null) return -1;
  for (let i = 0; i < BANDS.length; i++) if (n >= BANDS[i][0] && n <= BANDS[i][1]) return i;
  return -1;
}

function internOf(v){
  if (unknownish(v)) return 'unknown';
  return /(^|[^a-z])(evet|yes)([^a-z]|$)/.test(norm(v)) ? 'yes' : 'info';
}

function remoteOf(v){
  if (unknownish(v)) return 'unknown';
  const t = norm(v);
  if (/(uzaktan|remote|hibrit|hybrid|karisik|mixed|dagitik|distributed|esnek|flexible)/.test(t)) return 'flex';
  if (/(ofis|office)/.test(t)) return 'office';
  return 'other';
}

function genreTokens(v){
  return String(v || '').split(/[\/,;+|]/)
    .map(function(t){ return t.trim().replace(/^[-–—\s]+/, '').replace(/[-–—\s.]+$/, '').toLowerCase(); })
    .filter(function(t){ return t.length > 1 && !unknownish(t); });
}

function prep(){
  rows.forEach(function(r){
    const parts = ALL_KEYS.map(function(k){ return norm(r[k]); });
    parts.push(norm(r.web));
    r._blob = parts.join(' \u00b7 ');
    r._unk = {};
    ALL_KEYS.forEach(function(k){ r._unk[k] = unknownish(r[k]); });
    r._city = cityKey(r.city);
    r._year = yearOf(r.founded);
    r._size = sizeOf(r.employees);
    r._band = bandOf(r._size);
    r._int = internOf(r.internship);
    r._rem = remoteOf(r.remote);
    r._gen = norm(r.genres);
  });
}

/* ── persisted column layout ──────────────────────────────────────────── */

function loadState(){
  try { localStorage.removeItem(SKEY_OLD); } catch (e) {}
  let st = null;
  try { st = JSON.parse(localStorage.getItem(SKEY) || 'null'); } catch (e) { st = null; }
  if (!st || typeof st !== 'object') return;
  if (Array.isArray(st.order)) {
    const seen = new Set();
    const ord = [];
    st.order.forEach(function(k){
      if (ALL_KEYS.indexOf(k) >= 0 && !seen.has(k)) { seen.add(k); ord.push(k); }
    });
    DEF_ORDER.forEach(function(k){ if (!seen.has(k)) { seen.add(k); ord.push(k); } });
    if (ord.length === ALL_KEYS.length) order = ord;
  }
  if (Array.isArray(st.visible)) {
    // A stored list that names no column we still recognise is treated as stale
    // rather than obeyed, so a bad value cannot strand the reader on one column.
    const known = st.visible.filter(function(k){ return ALL_KEYS.indexOf(k) >= 0; });
    if (known.length) {
      const vis = new Set(known);
      vis.add('company');
      visible = vis;
    }
  }
  if (typeof st.sortKey === 'string' && ALL_KEYS.indexOf(st.sortKey) >= 0) sortKey = st.sortKey;
  if (st.sortDir === -1) sortDir = -1;
}

function saveState(){
  try {
    localStorage.setItem(SKEY, JSON.stringify({
      order: order,
      visible: Array.from(visible),
      sortKey: sortKey,
      sortDir: sortDir
    }));
  } catch (e) {}
}

function visKeys(){ return order.filter(function(k){ return visible.has(k); }); }

/* ── column manager ───────────────────────────────────────────────────── */

function renderColMgr(){
  $('colList').innerHTML = order.map(function(k, i){
    const on = visible.has(k);
    const locked = k === 'company';
    return '<li class="colitem' + (on ? '' : ' off') + '" draggable="true" data-k="' + k + '">' +
      '<span class="idx" aria-hidden="true">' + (i + 1) + '</span>' +
      '<span class="grip" aria-hidden="true">&#8942;&#8942;</span>' +
      '<label' + (locked ? ' title="' + esc(T.col_locked) + '"' : '') + '>' +
        '<input type="checkbox" data-k="' + k + '"' + (on ? ' checked' : '') +
          (locked ? ' disabled' : '') +
          ' aria-label="' + esc(T.col_visible + ': ' + label(k)) + '"/>' +
        '<span class="nm">' + esc(label(k)) + '</span></label>' +
      '<button type="button" class="mini" data-mv="-1" data-k="' + k + '"' +
        (i === 0 ? ' disabled' : '') + ' title="' + esc(T.move_up) +
        '" aria-label="' + esc(T.move_up + ': ' + label(k)) + '">&#9650;</button>' +
      '<button type="button" class="mini" data-mv="1" data-k="' + k + '"' +
        (i === order.length - 1 ? ' disabled' : '') + ' title="' + esc(T.move_down) +
        '" aria-label="' + esc(T.move_down + ': ' + label(k)) + '">&#9660;</button>' +
      '</li>';
  }).join('');
  $('colCount').textContent = visKeys().length + ' / ' + ALL_KEYS.length + ' ' + T.columns_count;
}

function afterLayoutChange(){
  saveState();
  renderColMgr();
  renderSortSelect();
  render();
}

function moveCol(k, delta){
  const i = order.indexOf(k);
  const j = i + delta;
  if (i < 0 || j < 0 || j >= order.length) return;
  order.splice(i, 1);
  order.splice(j, 0, k);
  afterLayoutChange();
  const same = $('colList').querySelector('[data-mv="' + delta + '"][data-k="' + k + '"]');
  const other = $('colList').querySelector('[data-mv="' + (-delta) + '"][data-k="' + k + '"]');
  if (same && !same.disabled) same.focus(); else if (other) other.focus();
}

function clearDrag(){
  dragKey = null;
  Array.prototype.forEach.call($('colList').querySelectorAll('.colitem'), function(n){
    n.classList.remove('dragging');
    n.classList.remove('over');
  });
}

function wireColMgr(){
  const ul = $('colList');
  ul.addEventListener('change', function(e){
    const inp = e.target.closest('input[type=checkbox]');
    if (!inp) return;
    if (inp.checked) visible.add(inp.dataset.k); else visible.delete(inp.dataset.k);
    visible.add('company');
    afterLayoutChange();
  });
  ul.addEventListener('click', function(e){
    const btn = e.target.closest('button[data-mv]');
    if (btn) moveCol(btn.dataset.k, parseInt(btn.dataset.mv, 10));
  });
  ul.addEventListener('dragstart', function(e){
    const li = e.target.closest('.colitem');
    if (!li) return;
    dragKey = li.dataset.k;
    li.classList.add('dragging');
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
      try { e.dataTransfer.setData('text/plain', dragKey); } catch (err) {}
    }
  });
  ul.addEventListener('dragover', function(e){
    if (!dragKey) return;
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
    const li = e.target.closest('.colitem');
    Array.prototype.forEach.call(ul.querySelectorAll('.colitem.over'), function(n){
      n.classList.remove('over');
    });
    if (li && li.dataset.k !== dragKey) li.classList.add('over');
  });
  ul.addEventListener('drop', function(e){
    e.preventDefault();
    const li = e.target.closest('.colitem');
    const key = dragKey;
    if (!key || !li || li.dataset.k === key) { clearDrag(); return; }
    const to = order.indexOf(li.dataset.k);
    order.splice(order.indexOf(key), 1);
    order.splice(to, 0, key);
    clearDrag();
    afterLayoutChange();
  });
  ul.addEventListener('dragend', clearDrag);

  $('colToggle').addEventListener('click', function(){
    const open = $('colMgr').hidden;
    $('colMgr').hidden = !open;
    $('colToggle').setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $('showAllCols').addEventListener('click', function(){
    visible = new Set(ALL_KEYS);
    afterLayoutChange();
  });
  $('resetCols').addEventListener('click', function(){
    order = DEF_ORDER.slice();
    visible = new Set(ALL_KEYS);
    afterLayoutChange();
  });
}

/* ── sorting ──────────────────────────────────────────────────────────── */

function renderSortSelect(){
  $('f-sort').innerHTML = order.map(function(k){
    return '<option value="' + k + '"' + (k === sortKey ? ' selected' : '') + '>' +
      esc(label(k)) + '</option>';
  }).join('');
}

function updateDirBtn(){
  const b = $('dirBtn');
  b.textContent = sortDir === 1 ? '\u2191' : '\u2193';
  b.setAttribute('aria-label', T.sort_dir_label + ' — ' + (sortDir === 1 ? T.sort_asc : T.sort_desc));
  b.title = b.getAttribute('aria-label');
}

function setSort(k, dir){
  if (dir) { sortKey = k; sortDir = dir; }
  else if (sortKey === k) sortDir = -sortDir;
  else { sortKey = k; sortDir = 1; }
  saveState();
  render();
}

function cmp(a, b){
  // Numeric columns sort by their parsed value; unparseable/blank values last.
  if (sortKey === 'founded' || sortKey === 'employees') {
    const av = sortKey === 'founded' ? a._year : a._size;
    const bv = sortKey === 'founded' ? b._year : b._size;
    if (av === null && bv === null) return collator.compare(a.company || '', b.company || '');
    if (av === null) return 1;
    if (bv === null) return -1;
    if (av !== bv) return (av - bv) * sortDir;
    return collator.compare(a.company || '', b.company || '');
  }
  const av = String(a[sortKey] || '');
  const bv = String(b[sortKey] || '');
  // Blank and "bilinmiyor"/"unknown" cells always sink to the bottom, in either
  // direction, so a reader sorting a column never has to page past the gaps.
  const ax = !av || a._unk[sortKey];
  const bx = !bv || b._unk[sortKey];
  if (ax !== bx) return ax ? 1 : -1;
  return collator.compare(av, bv) * sortDir || collator.compare(a.company || '', b.company || '');
}

/* ── filters ──────────────────────────────────────────────────────────── */

function fillSelect(id, items, allLabel){
  const sel = $(id);
  const keep = sel.value;
  sel.innerHTML = '<option value="">' + esc(allLabel) + '</option>' +
    items.map(function(it){
      return '<option value="' + esc(it.v) + '">' + esc(it.v) + '  (' + it.n + ')</option>';
    }).join('');
  if (keep) sel.value = keep;
}

function tally(values){
  const m = new Map();
  values.forEach(function(v){ if (v) m.set(v, (m.get(v) || 0) + 1); });
  return Array.from(m.entries()).map(function(e){ return { v: e[0], n: e[1] }; });
}

function alphabetical(items){
  return items.sort(function(a, b){ return collator.compare(a.v, b.v); });
}

function buildFilterOptions(){
  fillSelect('f-region', alphabetical(tally(rows.map(function(r){ return r.region; }))), T.all_regions);
  fillSelect('f-city', alphabetical(tally(rows.map(function(r){ return r._city; }))), T.all_cities);
  fillSelect('f-owner', alphabetical(tally(rows.map(function(r){
    return unknownish(r.ownership) ? '' : r.ownership;
  }))), T.all_ownership);

  // Genre options come from tokenised genre text; counts use the same substring
  // rule the filter applies, so the number in the option matches the result set.
  const cand = new Map();
  rows.forEach(function(r){
    new Set(genreTokens(r.genres)).forEach(function(t){ cand.set(t, (cand.get(t) || 0) + 1); });
  });
  const genres = [];
  cand.forEach(function(n, t){
    if (n < 2) return;
    const nt = norm(t);
    let hits = 0;
    for (let i = 0; i < rows.length; i++) if (rows[i]._gen.indexOf(nt) >= 0) hits++;
    if (hits >= 2) genres.push({ v: t, n: hits });
  });
  genres.sort(function(a, b){ return b.n - a.n || collator.compare(a.v, b.v); });
  fillSelect('f-genre', genres, T.all_genres);

  const years = rows.map(function(r){ return r._year; }).filter(function(y){ return y !== null; });
  if (years.length) {
    const lo = Math.min.apply(null, years);
    const hi = Math.max.apply(null, years);
    $('f-yfrom').min = String(lo); $('f-yfrom').max = String(hi);
    $('f-yto').min = String(lo); $('f-yto').max = String(hi);
    // The two year boxes are too narrow to spell the range out as placeholder
    // text, so the span in the field label carries it instead.
    $('yearRange').textContent = ' (' + lo + '\u2013' + hi + ')';
  }
}

function readFilters(){
  const raw = $('q').value.trim();
  return {
    raw: raw,
    q: norm(raw).split(/\s+/).filter(Boolean),
    region: $('f-region').value,
    city: $('f-city').value,
    genre: $('f-genre').value,
    owner: $('f-owner').value,
    yfrom: parseInt($('f-yfrom').value, 10),
    yto: parseInt($('f-yto').value, 10),
    size: $('f-size').value,
    intern: $('f-intern').value,
    remote: $('f-remote').value
  };
}

function matches(r, f){
  if (f.region && r.region !== f.region) return false;
  if (f.city && r._city !== f.city) return false;
  if (f.owner && r.ownership !== f.owner) return false;
  if (f.genre && r._gen.indexOf(norm(f.genre)) < 0) return false;
  if (!isNaN(f.yfrom) && (r._year === null || r._year < f.yfrom)) return false;
  if (!isNaN(f.yto) && (r._year === null || r._year > f.yto)) return false;
  if (f.size === 'u') { if (r._band !== -1) return false; }
  else if (f.size && r._band !== parseInt(f.size, 10)) return false;
  if (f.intern === 'yes' && r._int !== 'yes') return false;
  if (f.intern === 'info' && r._int === 'unknown') return false;
  if (f.intern === 'unknown' && r._int !== 'unknown') return false;
  if (f.remote && r._rem !== f.remote) return false;
  for (let i = 0; i < f.q.length; i++) if (r._blob.indexOf(f.q[i]) < 0) return false;
  return true;
}

function countFilters(f){
  let n = f.raw ? 1 : 0;
  ['region', 'city', 'genre', 'owner', 'size', 'intern', 'remote'].forEach(function(k){
    if (f[k]) n++;
  });
  if (!isNaN(f.yfrom) || !isNaN(f.yto)) n++;
  return n;
}

function clearFilters(){
  $('q').value = '';
  ['f-region', 'f-city', 'f-genre', 'f-owner', 'f-size', 'f-intern', 'f-remote',
   'f-yfrom', 'f-yto'].forEach(function(id){ $(id).value = ''; });
  render();
  $('q').focus();
}

/* ── rendering ────────────────────────────────────────────────────────── */

function cellHtml(r, k){
  if (k === 'company') {
    return r.web
      ? '<a href="' + esc(r.web) + '" target="_blank" rel="noopener">' + esc(r.company) + '</a>'
      : esc(r.company);
  }
  return esc(r[k]);
}

// Gives every visible column its floor width and shares whatever is left over
// between them by weight, so a wide screen widens the prose columns instead of
// stretching all twelve equally. A <col> width has to be a single percentage:
// table-layout:fixed ignores a calc() that mixes px and %, and silently falls
// back to equal columns.
let lastSized = -1;
function sizeCols(force){
  const vis = visKeys();
  if (!vis.length) return;
  let wsum = 0, minsum = 0;
  vis.forEach(function(k){ wsum += META[k].w; minsum += META[k].min; });
  const avail = Math.max($('tableWrap').clientWidth, minsum);
  if (!force && Math.abs(avail - lastSized) < 1) return;
  lastSized = avail;
  const extra = Math.max(0, avail - minsum);
  $('tbl').style.setProperty('--tmin', minsum + 'px');
  $('colGroup').innerHTML = vis.map(function(k){
    const m = META[k];
    const px = m.min + extra * (m.w / (wsum || 1));
    return '<col style="width:' + (px / avail * 100).toFixed(4) + '%"/>';
  }).join('');
}

function renderTable(list){
  const vis = visKeys();
  const stick = vis[0] === 'company';
  sizeCols(true);
  $('head').innerHTML = vis.map(function(k, i){
    const aria = sortKey === k ? (sortDir === 1 ? 'ascending' : 'descending') : 'none';
    const ico = sortKey === k ? (sortDir === 1 ? '\u25b2' : '\u25bc') : '\u21c5';
    return '<th scope="col" data-k="' + k + '" aria-sort="' + aria + '"' +
      (stick && i === 0 ? ' class="stick"' : '') + '>' +
      '<button type="button" class="th-btn" data-k="' + k + '" title="' +
      esc(label(k) + ' — ' + T.sort_by_col) + '"><span class="nm">' + esc(label(k)) +
      '</span><span class="ico" aria-hidden="true">' + ico + '</span></button></th>';
  }).join('');
  const out = [];
  for (let n = 0; n < list.length; n++) {
    const r = list[n];
    let tds = '';
    for (let i = 0; i < vis.length; i++) {
      const k = vis[i];
      let cls = META[k].cls;
      if (stick && i === 0) cls += ' stick';
      if (k === sortKey) cls += ' sorted';
      tds += '<td class="' + cls + '">' + cellHtml(r, k) + '</td>';
    }
    out.push('<tr>' + tds + '</tr>');
  }
  $('tbody').innerHTML = out.join('');
}

function renderCards(list){
  const vis = visKeys().filter(function(k){ return k !== 'company'; });
  const out = [];
  for (let n = 0; n < list.length; n++) {
    const r = list[n];
    let dl = '';
    for (let i = 0; i < vis.length; i++) {
      const v = r[vis[i]];
      if (!v) continue;
      dl += '<dt>' + esc(label(vis[i])) + '</dt><dd>' + esc(v) + '</dd>';
    }
    out.push('<article class="rowcard"><h3>' + cellHtml(r, 'company') + '</h3>' +
      (dl ? '<dl>' + dl + '</dl>' : '') + '</article>');
  }
  $('cardList').innerHTML = out.join('');
}

function updateStatus(shown, f){
  $('count').innerHTML = '<b>' + shown + '</b> / ' + rows.length + ' ' + esc(T.records);
  $('sortStatus').textContent = T.sorted_by + ': ' + label(sortKey) +
    ' (' + (sortDir === 1 ? T.sort_asc : T.sort_desc) + ')';
  const n = countFilters(f);
  $('filterPill').hidden = n === 0;
  $('clearFilters').hidden = n === 0;
  if (n) $('filterPill').textContent = n + ' ' + T.active_filters;
  updateDirBtn();
  if ($('f-sort').value !== sortKey) $('f-sort').value = sortKey;
}

function render(){
  const f = readFilters();
  const list = rows.filter(function(r){ return matches(r, f); }).sort(cmp);
  updateStatus(list.length, f);
  const cards = cardMQ.matches;
  const none = list.length === 0;
  $('emptyBox').hidden = !none;
  $('tableWrap').hidden = cards || none;
  $('cardList').hidden = !cards || none;
  if (none) return;
  if (cards) renderCards(list); else renderTable(list);
}

/* ── boot ─────────────────────────────────────────────────────────────── */

function wire(){
  wireColMgr();
  $('filters').addEventListener('input', function(e){
    if (e.target.id === 'f-sort') return;
    render();
  });
  $('f-sort').addEventListener('change', function(){ setSort($('f-sort').value, sortDir); });
  $('dirBtn').addEventListener('click', function(){ setSort(sortKey, -sortDir); });
  $('clearFilters').addEventListener('click', clearFilters);
  $('head').addEventListener('click', function(e){
    const btn = e.target.closest('.th-btn');
    if (btn) setSort(btn.dataset.k);
  });
  if (cardMQ.addEventListener) cardMQ.addEventListener('change', render);
  else if (cardMQ.addListener) cardMQ.addListener(render);
  // Column widths are computed from the measured container, so they have to be
  // recomputed when it changes size. sizeCols() no-ops unless the width moved,
  // which keeps this from feeding back into the observer.
  if (window.ResizeObserver) {
    new ResizeObserver(function(){ if (!$('tableWrap').hidden) sizeCols(false); })
      .observe($('tableWrap'));
  } else {
    window.addEventListener('resize', function(){ if (!$('tableWrap').hidden) sizeCols(false); });
  }
}

async function boot(){
  loadState();
  wire();
  renderColMgr();
  renderSortSelect();
  updateDirBtn();
  let res;
  try {
    res = await fetch(SRC);
  } catch (err) {
    $('count').textContent = String(err);
    return;
  }
  if (!res.ok) { $('count').textContent = 'HTTP ' + res.status; return; }
  rows = await res.json();
  prep();
  buildFilterOptions();
  render();
}
boot();
"""


def build_list_page(lang: str, which: str) -> str:
    u = UI[lang]
    warn = u["warn_turkey"] if which == "turkey" else u["warn_global"]
    lead = u["lead_turkey"] if which == "turkey" else u["lead_global"]
    title = f"{u['turkey'] if which == 'turkey' else u['global']} — {u['brand']}"
    page = f"{which}.html"
    meta = column_meta(lang)
    storage_key = f"atlas-cols-{which}-{lang}-{STORAGE_VERSION}"
    legacy_key = f"atlas-cols-{which}-{lang}"

    size_opts = "".join(
        f'<option value="{i}">{band}</option>' for i, band in enumerate(u["size_bands"])
    )
    js_strings = {
        k: u[k]
        for k in (
            "records", "sorted_by", "sort_asc", "sort_desc", "active_filters",
            "sort_dir_label", "sort_by_col", "col_locked", "col_visible",
            "move_up", "move_down", "columns_count",
            "all_regions", "all_cities", "all_genres", "all_ownership",
            "year_from", "year_to",
        )
    }
    script = (
        LIST_JS
        .replace("__CDEF__", json.dumps(meta, ensure_ascii=False))
        .replace("__T__", json.dumps(js_strings, ensure_ascii=False))
        .replace("__LANG__", json.dumps(lang))
        .replace("__SRC__", json.dumps(f"../data/{which}.{lang}.json"))
        .replace("__SKEY_OLD__", json.dumps(legacy_key))
        .replace("__SKEY__", json.dumps(storage_key))
    )

    body = f"""
<div class="wrap list">
  <div class="top">
    <a class="brand" href="index.html">{u['brand']}</a>
    <nav class="nav">
      <a href="index.html">{u['home']}</a>
      <a class="{'on' if which=='turkey' else ''}" href="turkey.html">{u['turkey']}</a>
      <a class="{'on' if which=='global' else ''}" href="global.html">{u['global']}</a>
      {lang_switcher(lang, page)}
    </nav>
  </div>
  <header class="hero">
    <h1>{u['turkey'] if which=='turkey' else u['global']}</h1>
    <p class="lead">{lead}</p>
  </header>
  <div class="warn disclaimer">{u['disclaimer']}</div>
  <div class="warn">{warn} {u['unknown_note']}</div>
  <div class="bleed">
    <section class="controls" aria-label="{u['filter_heading']}">
      <div class="controls-head">
        <h2 class="controls-title">{u['filter_heading']}</h2>
        <p class="sort-hint">{u['sort_hint']}</p>
      </div>
      <div class="filters" id="filters">
        <label class="field field-search">
          <span class="flabel">{u['search_label']}</span>
          <input id="q" type="search" placeholder="{u['search']}" autocomplete="off"/>
        </label>
        <label class="field">
          <span class="flabel">{u['region_label']}</span>
          <select id="f-region"><option value="">{u['all_regions']}</option></select>
        </label>
        <label class="field">
          <span class="flabel">{u['city_label']}</span>
          <select id="f-city"><option value="">{u['all_cities']}</option></select>
        </label>
        <label class="field">
          <span class="flabel">{u['genre_label']}</span>
          <select id="f-genre"><option value="">{u['all_genres']}</option></select>
        </label>
        <label class="field">
          <span class="flabel">{u['ownership_label']}</span>
          <select id="f-owner"><option value="">{u['all_ownership']}</option></select>
        </label>
        <div class="field">
          <span class="flabel">{u['founded_label']}<span id="yearRange"></span></span>
          <div class="pair">
            <input id="f-yfrom" type="number" inputmode="numeric" placeholder="{u['year_from']}"
                   aria-label="{u['founded_label']} — {u['year_from']}"/>
            <input id="f-yto" type="number" inputmode="numeric" placeholder="{u['year_to']}"
                   aria-label="{u['founded_label']} — {u['year_to']}"/>
          </div>
        </div>
        <label class="field">
          <span class="flabel">{u['size_label']}</span>
          <select id="f-size">
            <option value="">{u['size_any']}</option>
            {size_opts}
            <option value="u">{u['size_unknown']}</option>
          </select>
        </label>
        <label class="field">
          <span class="flabel">{u['internship_label']}</span>
          <select id="f-intern">
            <option value="">{u['intern_any']}</option>
            <option value="yes">{u['intern_yes']}</option>
            <option value="info">{u['intern_info']}</option>
            <option value="unknown">{u['intern_unknown']}</option>
          </select>
        </label>
        <label class="field">
          <span class="flabel">{u['remote_label']}</span>
          <select id="f-remote">
            <option value="">{u['remote_any']}</option>
            <option value="flex">{u['remote_flex']}</option>
            <option value="office">{u['remote_office']}</option>
            <option value="unknown">{u['remote_unknown']}</option>
          </select>
        </label>
        <div class="field">
          <span class="flabel">{u['sort_label']}</span>
          <div class="pair">
            <select id="f-sort" aria-label="{u['sort_label']}"></select>
            <button type="button" class="dir-btn" id="dirBtn">&#8593;</button>
          </div>
        </div>
      </div>
      <div class="controls-foot">
        <div class="status-row" aria-live="polite">
          <span class="count" id="count">{u['loading']}</span>
          <span class="sort-status" id="sortStatus"></span>
          <span class="filter-pill" id="filterPill" hidden></span>
        </div>
        <div class="btn-row">
          <button type="button" class="btn-ghost" id="clearFilters" hidden>{u['clear_filters']}</button>
          <button type="button" class="btn-ghost" id="colToggle" aria-expanded="false"
                  aria-controls="colMgr">{u['columns_label']}</button>
        </div>
      </div>
      <div class="colmgr" id="colMgr" hidden>
        <div class="colmgr-head">
          <h3>{u['columns_title']}</h3>
          <div class="btn-row">
            <span class="badge" id="colCount"></span>
            <button type="button" class="btn-ghost" id="showAllCols">{u['columns_all']}</button>
            <button type="button" class="btn-ghost" id="resetCols">{u['columns_reset']}</button>
          </div>
          <p class="colmgr-hint">{u['columns_hint']}</p>
        </div>
        <ul class="collist" id="colList"></ul>
      </div>
    </section>
    <div class="table-wrap" id="tableWrap">
      <table class="atlas" id="tbl">
        <colgroup id="colGroup"></colgroup>
        <thead><tr id="head"></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    <div class="cards" id="cardList" hidden></div>
    <div class="empty" id="emptyBox" hidden>
      <strong>{u['no_results']}</strong>{u['no_results_hint']}
    </div>
  </div>
  <footer>GitHub Pages · <a href="https://github.com/gusanmaz/game-companies-atlas">gusanmaz/game-companies-atlas</a>
  · {u['contribute_footer']}</footer>
</div>
<script>{script}</script>
"""
    return page_shell(title, body, lang)


def build_root_index() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Game Companies Atlas</title>
<meta http-equiv="refresh" content="0; url=en/index.html"/>
<link rel="canonical" href="en/index.html"/>
<style>body{font-family:system-ui,sans-serif;padding:2rem;background:#f4f1ea;color:#1a2330}
a{color:#146b57;font-weight:600}</style>
</head>
<body>
<p><a href="en/index.html">English</a> · <a href="tr/index.html">Türkçe</a></p>
</body>
</html>
"""


def copy_downloads() -> None:
    files = DOCS / "files"
    files.mkdir(parents=True, exist_ok=True)
    for lang in ("tr", "en"):
        for name in ("turkey", "global"):
            src = DATA / f"{name}.{lang}.csv"
            if src.exists():
                shutil.copy2(src, CAT / f"{name}.{lang}.csv")
                shutil.copy2(src, files / f"{name}.{lang}.csv")
    for name in (
        "TURKEY.tr.md",
        "TURKEY.en.md",
        "GLOBAL.tr.md",
        "GLOBAL.en.md",
        "turkey.tr.xlsx",
        "turkey.tr.pdf",
        "global.tr.xlsx",
        "global.tr.pdf",
    ):
        src = CAT / name
        if src.exists():
            shutil.copy2(src, files / name)


def main() -> None:
    turkey_tr = load_csv(DATA / "turkey.tr.csv", "tr")
    turkey_en = load_csv(DATA / "turkey.en.csv", "en")
    global_tr = load_csv(DATA / "global.tr.csv", "tr")
    global_en = load_csv(DATA / "global.en.csv", "en")
    write_json("turkey", "tr", turkey_tr)
    write_json("turkey", "en", turkey_en)
    write_json("global", "tr", global_tr)
    write_json("global", "en", global_en)

    counts = {"turkey": len(turkey_en), "global": len(global_en)}

    for lang in ("tr", "en"):
        d = DOCS / lang
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build_home(lang, counts), encoding="utf-8")
        (d / "turkey.html").write_text(build_list_page(lang, "turkey"), encoding="utf-8")
        (d / "global.html").write_text(build_list_page(lang, "global"), encoding="utf-8")

    (DOCS / "index.html").write_text(build_root_index(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    copy_downloads()

    # quick counts for README helpers
    stats = {
        **counts,
        "regions_tr": len({r["region"] for r in turkey_en if r["region"]}),
        "regions_global": len({r["region"] for r in global_en if r["region"]}),
    }
    (ROOT / "scripts" / ".cache" / "stats.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "scripts" / ".cache" / "stats.json").write_text(json.dumps(stats), encoding="utf-8")
    print("built pages", stats)


if __name__ == "__main__":
    main()
