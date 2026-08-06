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

# Columns shown by default on table pages (others can be toggled on).
DEFAULT_VISIBLE_KEYS = [
    "company", "region", "city", "founded", "employees", "genres", "games", "notes",
]

UI = {
    "tr": {
        "lang": "tr",
        "brand": "Oyun Firmaları Atlası",
        "title_home": "Oyun Firmaları Atlası — Türkiye ve küresel stüdyolar",
        "lead": "Türkiye’de 219, dünyada (TR hariç) 878 oyun stüdyosu/yayıncı kaydı. Staj, uzaktan çalışma, sahiplik ve örnek oyunlarla birlikte.",
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
        "cols": [
            "Firma", "Bölge", "Şehir", "Kuruluş", "Çalışan", "Gelir / fon",
            "Tür", "Örnek oyunlar", "Staj", "Uzaktan", "Sahiplik", "Not",
        ],
        "keys": [
            "company", "region", "city", "founded", "employees", "funding",
            "genres", "games", "internship", "remote", "ownership", "notes",
        ],
        "warn_global": "Türk firmalar bu listede yok — Türkiye listesine bakın.",
        "warn_turkey": "Küresel (TR dışı) liste ayrı sayfada.",
        "home": "Ana sayfa",
        "lead_turkey": "Türkiye’deki oyun stüdyoları, yayıncılar ve ekosistem aktörleri. Sütun başlığına tıklayarak sıralayın, arama ve bölge filtresiyle daraltın.",
        "lead_global": "Türkiye dışındaki büyük stüdyolar, yayıncılar ve platformlar. Sütun başlığına tıklayarak sıralayın, arama ve bölge filtresiyle daraltın.",
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
    },
    "en": {
        "lang": "en",
        "brand": "Game Companies Atlas",
        "title_home": "Game Companies Atlas — Türkiye and global studios",
        "lead": "219 companies in Türkiye and 878 global studios/publishers (excl. Türkiye), with internship, remote work, ownership and sample games.",
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
        "cols": [
            "Company", "Region", "City", "Founded", "Employees", "Revenue / funding",
            "Genres", "Sample games", "Internship", "Remote", "Ownership", "Notes",
        ],
        "keys": [
            "company", "region", "city", "founded", "employees", "funding",
            "genres", "games", "internship", "remote", "ownership", "notes",
        ],
        "warn_global": "Turkish companies are not listed here — see the Türkiye list.",
        "warn_turkey": "Global (non-TR) list is on a separate page.",
        "home": "Home",
        "lead_turkey": "Game studios, publishers and ecosystem actors based in Türkiye. Click a column header to sort; narrow the list with search and the region filter.",
        "lead_global": "Major studios, publishers and platforms outside Türkiye. Click a column header to sort; narrow the list with search and the region filter.",
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
    },
}

CSS = """
:root{
  --ink:#1a2330;--muted:#5a6575;--paper:#f4f1ea;--card:#fffdf8;--line:#d8d0c2;
  --navy:#1e3a5f;--navy2:#2d5a87;--teal:#146b57;--teal2:#0e5544;--chip:#eef3f8;
  --warn:#8a5a12;--warn-bg:#fff8eb;--warn-line:#d4a24a;
}
*{box-sizing:border-box}
body{margin:0;font-family:"Source Sans 3",system-ui,sans-serif;color:var(--ink);
background:radial-gradient(1100px 480px at 8% -8%,#d7e6f5 0%,transparent 55%),
radial-gradient(900px 420px at 100% 0%,#e7dfd1 0%,transparent 50%),var(--paper);line-height:1.55}
a{color:var(--teal2);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:2rem 1.15rem 3.5rem}
.wrap.list{max-width:min(1720px,96vw)}
@media(min-width:1400px){.wrap{max-width:1400px}.wrap.list{max-width:min(1720px,96vw)}}
@media(min-width:1800px){.wrap.list{max-width:1760px}}
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
.toolbar{display:flex;flex-wrap:wrap;gap:.65rem;margin:1rem 0 .8rem;align-items:center}
.toolbar input,.toolbar select{font:inherit;padding:.55rem .75rem;border:1px solid var(--line);
border-radius:8px;background:#fff;color:var(--ink)}
.toolbar input{flex:1 1 240px}
.toolbar select{min-width:180px}
.count{color:var(--muted);font-size:.9rem}
.col-toggle{position:relative}
.col-toggle > summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;
padding:.45rem .85rem;border-radius:8px;border:1px solid var(--navy);color:var(--navy);background:#fff;
font-weight:600;font-size:.92rem;user-select:none}
.col-toggle > summary::-webkit-details-marker{display:none}
.col-toggle[open] > summary{background:var(--chip)}
.col-panel{position:absolute;right:0;top:calc(100% + .35rem);z-index:20;min-width:220px;
background:#fff;border:1px solid var(--line);border-radius:10px;padding:.65rem .75rem;
box-shadow:0 8px 24px rgba(30,58,95,.12);display:grid;gap:.35rem}
.col-panel label{display:flex;gap:.5rem;align-items:center;font-size:.9rem;color:var(--ink);cursor:pointer}
.col-panel label input{accent-color:var(--navy)}
.table-wrap{overflow:auto;max-height:min(78vh,920px);border:1px solid var(--line);border-radius:10px;background:#fff}
table{border-collapse:separate;border-spacing:0;width:max-content;min-width:100%;font-size:13px}
th,td{padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{position:sticky;top:0;background:#eef2f7;color:var(--muted);font-size:11.5px;text-transform:uppercase;
letter-spacing:.05em;z-index:2;cursor:pointer;user-select:none;white-space:nowrap}
th:first-child,td:first-child{position:sticky;left:0;background:#fff;z-index:1;min-width:200px;max-width:220px;
box-shadow:2px 0 0 var(--line);font-weight:600}
th:first-child{z-index:3;background:#eef2f7}
th.col-hide,td.col-hide{display:none}
tr:hover td{background:#f7fafc}
tr:hover td:first-child{background:#f0f5f9}
.badge{display:inline-block;font-size:11px;padding:2px 7px;border-radius:4px;background:var(--chip);color:var(--muted);border:1px solid var(--line)}
.warn{background:#fff;border:1px solid var(--line);border-left:3px solid var(--teal);border-radius:8px;
padding:.85rem 1rem;margin:0 0 .75rem;color:var(--muted);font-size:.93rem}
.warn.disclaimer{background:var(--warn-bg);border-color:var(--warn-line);border-left-color:var(--warn);
color:var(--warn);font-weight:600}
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


def build_home(lang: str) -> str:
    u = UI[lang]
    files = "../files"
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
    <p class="lead">{u['lead']}</p>
    <p class="by">{u['byline']}</p>
  </header>
  <div class="warn disclaimer">{u['disclaimer']}</div>
  <section class="grid">
    <article class="card">
      <h2>{u['turkey']}</h2>
      <p class="meta">219 {u['records']}</p>
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
      <p class="meta">878 {u['records']}</p>
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


def build_list_page(lang: str, which: str) -> str:
    u = UI[lang]
    warn = u["warn_turkey"] if which == "turkey" else u["warn_global"]
    lead = u["lead_turkey"] if which == "turkey" else u["lead_global"]
    title = f"{u['turkey'] if which == 'turkey' else u['global']} — {u['brand']}"
    page = f"{which}.html"
    cols_json = json.dumps(u["cols"], ensure_ascii=False)
    keys_json = json.dumps(u["keys"], ensure_ascii=False)
    defaults_json = json.dumps(DEFAULT_VISIBLE_KEYS, ensure_ascii=False)
    storage_key = f"atlas-cols-{which}-{lang}"
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
  <div class="toolbar">
    <input id="q" type="search" placeholder="{u['search']}" autocomplete="off"/>
    <select id="region"><option value="">{u['all_regions']}</option></select>
    <details class="col-toggle" id="colToggle">
      <summary>{u['columns_label']}</summary>
      <div class="col-panel" id="colPanel"></div>
    </details>
    <span class="count" id="count">…</span>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr id="head"></tr></thead>
      <tbody id="body"></tbody>
    </table>
  </div>
  <footer>GitHub Pages · <a href="https://github.com/gusanmaz/game-companies-atlas">gusanmaz/game-companies-atlas</a>
  · {u['contribute_footer']}</footer>
</div>
<script>
const COLS = {cols_json};
const KEYS = {keys_json};
const DEFAULT_VISIBLE = {defaults_json};
const STORAGE_KEY = {json.dumps(storage_key)};
const RECORDS_LABEL = {json.dumps(u['records'], ensure_ascii=False)};
let rows = [];
let sortKey = 'company';
let sortDir = 1;
let visible = new Set(DEFAULT_VISIBLE);

function esc(s){{
  return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
}}

function loadVisible(){{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const arr = JSON.parse(raw);
    if (Array.isArray(arr) && arr.length) {{
      const next = new Set(arr.filter(k => KEYS.includes(k)));
      if (next.size) {{
        next.add('company');
        visible = next;
      }}
    }}
  }} catch (e) {{}}
}}

function saveVisible(){{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify([...visible])); }} catch (e) {{}}
}}

function isVisible(k){{ return visible.has(k); }}

function renderColPanel(){{
  const panel = document.getElementById('colPanel');
  panel.innerHTML = KEYS.map((k,i) => {{
    const locked = k === 'company';
    const checked = isVisible(k) ? 'checked' : '';
    const disabled = locked ? 'disabled' : '';
    return `<label><input type="checkbox" data-k="${{k}}" ${{checked}} ${{disabled}}/> ${{esc(COLS[i])}}</label>`;
  }}).join('');
  panel.querySelectorAll('input[type=checkbox]').forEach(inp => {{
    if (inp.disabled) return;
    inp.addEventListener('change', () => {{
      if (inp.checked) visible.add(inp.dataset.k); else visible.delete(inp.dataset.k);
      visible.add('company');
      saveVisible();
      renderHead();
      render();
    }});
  }});
}}

function renderHead(){{
  const tr = document.getElementById('head');
  tr.innerHTML = COLS.map((c,i) => {{
    const hide = isVisible(KEYS[i]) ? '' : ' col-hide';
    return `<th class="${{hide.trim()}}" data-k="${{KEYS[i]}}">${{esc(c)}}</th>`;
  }}).join('');
  tr.querySelectorAll('th').forEach(th => th.addEventListener('click', () => {{
    if (th.classList.contains('col-hide')) return;
    const k = th.dataset.k;
    if (sortKey === k) sortDir *= -1; else {{ sortKey = k; sortDir = 1; }}
    render();
  }}));
}}

function filtered(){{
  const q = (document.getElementById('q').value || '').toLowerCase().trim();
  const region = document.getElementById('region').value;
  return rows.filter(r => {{
    if (region && r.region !== region) return false;
    if (!q) return true;
    return KEYS.some(k => String(r[k]||'').toLowerCase().includes(q)) || String(r.web||'').toLowerCase().includes(q);
  }}).sort((a,b) => {{
    const av = String(a[sortKey]||'').toLowerCase();
    const bv = String(b[sortKey]||'').toLowerCase();
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  }});
}}

function render(){{
  const list = filtered();
  document.getElementById('count').textContent = list.length + ' / ' + rows.length + ' ' + RECORDS_LABEL;
  document.getElementById('body').innerHTML = list.map(r => {{
    const name = r.web ? `<a href="${{esc(r.web)}}" target="_blank" rel="noopener">${{esc(r.company)}}</a>` : esc(r.company);
    const cells = KEYS.map((k,i) => {{
      const hide = isVisible(k) ? '' : ' col-hide';
      const content = i===0 ? name : esc(r[k]);
      return `<td class="${{hide.trim()}}">${{content}}</td>`;
    }});
    return '<tr>' + cells.join('') + '</tr>';
  }}).join('');
}}

async function boot(){{
  loadVisible();
  renderColPanel();
  const res = await fetch('../data/{which}.{lang}.json');
  if (!res.ok) {{
    document.getElementById('count').textContent = 'HTTP ' + res.status;
    return;
  }}
  rows = await res.json();
  const regions = [...new Set(rows.map(r => r.region).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'{lang}'));
  const sel = document.getElementById('region');
  regions.forEach(r => {{
    const o = document.createElement('option');
    o.value = r; o.textContent = r; sel.appendChild(o);
  }});
  renderHead();
  document.getElementById('q').addEventListener('input', render);
  sel.addEventListener('change', render);
  document.addEventListener('click', (e) => {{
    const details = document.getElementById('colToggle');
    if (details && details.open && !details.contains(e.target)) details.open = false;
  }});
  render();
}}
boot();
</script>
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

    for lang in ("tr", "en"):
        d = DOCS / lang
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build_home(lang), encoding="utf-8")
        (d / "turkey.html").write_text(build_list_page(lang, "turkey"), encoding="utf-8")
        (d / "global.html").write_text(build_list_page(lang, "global"), encoding="utf-8")

    (DOCS / "index.html").write_text(build_root_index(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    copy_downloads()

    # quick counts for README helpers
    stats = {
        "turkey": len(turkey_en),
        "global": len(global_en),
        "regions_tr": len({r["region"] for r in turkey_en if r["region"]}),
        "regions_global": len({r["region"] for r in global_en if r["region"]}),
    }
    (ROOT / "scripts" / ".cache" / "stats.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "scripts" / ".cache" / "stats.json").write_text(json.dumps(stats), encoding="utf-8")
    print("built pages", stats)


if __name__ == "__main__":
    main()
