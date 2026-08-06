#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parallel TR→EN translation for game-company CSV fields via OpenAI."""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = ROOT / "scripts" / ".cache" / "translations.json"
FIELDS = [
    "Bölge",
    "Şehir",
    "Kuruluş",
    "Çalışan",
    "Gelir_fon",
    "Türler",
    "Örnek_oyunlar",
    "Staj",
    "Uzaktan",
    "Sahiplik",
    "Not",
]
HEADERS_EN = {
    "Firma": "Company",
    "Bölge": "Region",
    "Şehir": "City",
    "Kuruluş": "Founded",
    "Çalışan": "Employees",
    "Gelir_fon": "Revenue_funding",
    "Web": "Web",
    "Türler": "Genres",
    "Örnek_oyunlar": "Sample_games",
    "Staj": "Internship",
    "Uzaktan": "Remote",
    "Sahiplik": "Ownership",
    "Not": "Notes",
}
FIXED = {
    "bilinmiyor": "unknown",
    "Bilinmiyor": "Unknown",
    "—": "—",
    "-": "-",
    "evet": "yes",
    "hayır": "no",
    "bağımsız": "independent",
    "karışık": "mixed",
    "hibrit": "hybrid",
    "ofis odaklı": "office-focused",
}

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_URL = "https://api.openai.com/v1/chat/completions"
WORKERS = int(os.environ.get("TRANSLATE_WORKERS", "12"))
BATCH_SIZE = int(os.environ.get("TRANSLATE_BATCH", "35"))


def load_cache() -> dict[str, str]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    tmp.replace(CACHE)


def collect_strings() -> list[str]:
    uniq: set[str] = set()
    for path in sorted(DATA.glob("*.tr.csv")):
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                for key in FIELDS:
                    val = (row.get(key) or "").strip()
                    if not val:
                        continue
                    if val in FIXED or val.lower() in FIXED:
                        continue
                    uniq.add(val)
    return sorted(uniq, key=lambda s: (-len(s), s))


def chunks(items: list[str], n: int) -> list[list[str]]:
    return [items[i : i + n] for i in range(0, len(items), n)]


def call_openai(batch: list[str], api_key: str, attempt: int = 0) -> list[str]:
    system = (
        "You translate Turkish game-industry directory fields into concise natural English. "
        "Keep proper nouns, company names, game titles, URLs, currencies, numbers, and "
        "abbreviations unchanged. Preserve meaning; do not add explanations. "
        'Return ONLY a JSON object of the form {"items":["..."]} with the same '
        "length and order as the input items array."
    )
    payload = {
        "model": MODEL,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    "Translate each string in items to English. "
                    + json.dumps({"items": batch}, ensure_ascii=False)
                ),
            },
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "replace")
        if e.code in (429, 500, 502, 503) and attempt < 6:
            time.sleep(1.5 * (2**attempt))
            return call_openai(batch, api_key, attempt + 1)
        raise RuntimeError("OpenAI HTTP %s: %s" % (e.code, err[:500])) from e

    content = body["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    if isinstance(parsed, dict):
        for key in ("items", "translations", "result", "data"):
            if key in parsed and isinstance(parsed[key], list):
                parsed = parsed[key]
                break
        else:
            # single-key object wrapping a list
            vals = list(parsed.values())
            if len(vals) == 1 and isinstance(vals[0], list):
                parsed = vals[0]
            else:
                raise RuntimeError("Unexpected JSON object: %s" % content[:300])
    if not isinstance(parsed, list) or len(parsed) != len(batch):
        raise RuntimeError(
            "Length mismatch: got %s expected %s; sample=%s"
            % (len(parsed) if isinstance(parsed, list) else type(parsed), len(batch), content[:200])
        )
    return [str(x) for x in parsed]


def translate_all(api_key: str) -> dict[str, str]:
    cache = load_cache()
    for src, dst in FIXED.items():
        cache.setdefault(src, dst)
    strings = collect_strings()
    pending = [s for s in strings if s not in cache]
    print("cache hit %d / total unique %d / pending %d" % (len(strings) - len(pending), len(strings), len(pending)))
    if not pending:
        return cache

    batches = chunks(pending, BATCH_SIZE)
    print("batches %d workers %d model %s" % (len(batches), WORKERS, MODEL))
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(call_openai, batch, api_key): batch for batch in batches}
        for fut in as_completed(futures):
            batch = futures[fut]
            try:
                outs = fut.result()
            except Exception as exc:
                print("BATCH FAIL (%d items): %s" % (len(batch), exc), file=sys.stderr)
                # retry once serially with smaller chunks
                for sub in chunks(batch, max(8, BATCH_SIZE // 3)):
                    outs = call_openai(sub, api_key)
                    for src, dst in zip(sub, outs):
                        cache[src] = dst
                done += len(batch)
                save_cache(cache)
                print("progress %d/%d" % (done, len(pending)))
                continue
            for src, dst in zip(batch, outs):
                cache[src] = dst
            done += len(batch)
            if done % (BATCH_SIZE * 4) < BATCH_SIZE or done == len(pending):
                save_cache(cache)
                print("progress %d/%d" % (done, len(pending)))
    save_cache(cache)
    return cache


def tr(cache: dict[str, str], value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    if v in cache:
        return cache[v]
    if v.lower() in cache:
        return cache[v.lower()]
    if v in FIXED:
        return FIXED[v]
    if v.lower() in FIXED:
        return FIXED[v.lower()]
    return v


def write_en_csv(src: Path, dst: Path, cache: dict[str, str]) -> int:
    with src.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    fieldnames = [HEADERS_EN.get(h, h) for h in (rows[0].keys() if rows else HEADERS_EN.values())]
    # stable header order from Turkish file
    with src.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        src_headers = reader.fieldnames or []
        rows = list(reader)
    out_headers = [HEADERS_EN.get(h, h) for h in src_headers]
    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_headers)
        w.writeheader()
        for row in rows:
            out = {}
            for h in src_headers:
                en_h = HEADERS_EN.get(h, h)
                val = row.get(h) or ""
                if h == "Firma" or h == "Web":
                    out[en_h] = val
                else:
                    out[en_h] = tr(cache, val)
            w.writerow(out)
    return len(rows)


def write_en_markdown(csv_path: Path, md_path: Path, title: str, intro: str) -> None:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        md_path.write_text("# %s\n\n(empty)\n" % title, encoding="utf-8")
        return
    headers = list(rows[0].keys())
    lines = [
        "# %s" % title,
        "",
        intro,
        "",
        "%d records · August 2026" % len(rows),
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        cells = []
        for h in headers:
            val = (row.get(h) or "").replace("|", "\\|").replace("\n", " ")
            if h in ("Company", "Firma") and (row.get("Web") or "").startswith("http"):
                cells.append("[%s](%s)" % (val, row["Web"]))
            else:
                cells.append(val)
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY missing", file=sys.stderr)
        return 2
    cache = translate_all(api_key)
    n1 = write_en_csv(DATA / "turkey.tr.csv", DATA / "turkey.en.csv", cache)
    n2 = write_en_csv(DATA / "global.tr.csv", DATA / "global.en.csv", cache)
    write_en_markdown(
        DATA / "turkey.en.csv",
        ROOT / "catalogue" / "TURKEY.en.md",
        "Türkiye Game Companies",
        "Directory of game studios, publishers and ecosystem actors in Türkiye.",
    )
    write_en_markdown(
        DATA / "global.en.csv",
        ROOT / "catalogue" / "GLOBAL.en.md",
        "Global Game Companies (excl. Türkiye)",
        "Directory of major game studios, publishers and platforms outside Türkiye.",
    )
    print("wrote EN CSVs: turkey=%d global=%d cache=%d" % (n1, n2, len(cache)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
