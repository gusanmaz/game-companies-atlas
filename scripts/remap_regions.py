#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remap global CSV regions to cleaner continent-style buckets."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# TR region labels
TR = {
    "europe": "Avrupa",
    "mideast": "Ortadoğu",
    "na": "Kuzey Amerika",
    "latam": "Latin Amerika",
    "china": "Çin",
    "japan": "Japonya",
    "korea": "Güney Kore",
    "asia": "Diğer Asya",
    "oceania": "Okyanusya",
    "pub": "Yayıncılar / platformlar",
    "eco": "Ekosistem / fuar / dernek",
}
EN = {
    "europe": "Europe",
    "mideast": "Middle East",
    "na": "North America",
    "latam": "Latin America",
    "china": "China",
    "japan": "Japan",
    "korea": "South Korea",
    "asia": "Rest of Asia",
    "oceania": "Oceania",
    "pub": "Publishers / platforms",
    "eco": "Ecosystem / fair / association",
}

# Country/region tokens (lowercase) -> bucket key
COUNTRY_HINTS: list[tuple[str, str]] = [
    # Middle East (check before Europe for Israel)
    ("israil", "mideast"),
    ("israel", "mideast"),
    ("dubai", "mideast"),
    ("beyrut", "mideast"),
    ("beirut", "mideast"),
    ("abu dhabi", "mideast"),
    ("uae", "mideast"),
    ("bae", "mideast"),
    ("suudi", "mideast"),
    ("saudi", "mideast"),
    ("katar", "mideast"),
    ("qatar", "mideast"),
    ("amman", "mideast"),
    ("ürdün", "mideast"),
    ("jordan", "mideast"),
    ("iran", "mideast"),
    ("ırak", "mideast"),
    ("iraq", "mideast"),
    ("kuwait", "mideast"),
    ("kuveyt", "mideast"),
    ("mena", "mideast"),
    # Oceania
    ("avustralya", "oceania"),
    ("australia", "oceania"),
    ("melbourne", "oceania"),
    ("sydney", "oceania"),
    ("brisbane", "oceania"),
    ("adelaide", "oceania"),
    ("auckland", "oceania"),
    ("wellington", "oceania"),
    ("yeni zelanda", "oceania"),
    ("new zealand", "oceania"),
    ("oceania", "oceania"),
    # East Asia kept separate when city hints say so
    ("çin", "china"),
    ("china", "china"),
    ("pekin", "china"),
    ("beijing", "china"),
    ("şanghay", "china"),
    ("shanghai", "china"),
    ("shenzhen", "china"),
    ("guangzhou", "china"),
    ("hangzhou", "china"),
    ("chengdu", "china"),
    ("hong kong", "china"),
    ("hongkong", "china"),
    ("taiwan", "china"),
    ("tayvan", "china"),
    ("taipei", "china"),
    ("japonya", "japan"),
    ("japan", "japan"),
    ("tokyo", "japan"),
    ("osaka", "japan"),
    ("kyoto", "japan"),
    ("yokohama", "japan"),
    ("güney kore", "korea"),
    ("south korea", "korea"),
    ("korea", "korea"),
    ("seoul", "korea"),
    ("seul", "korea"),
    ("busan", "korea"),
    # Rest of Asia
    ("hindistan", "asia"),
    ("india", "asia"),
    ("bangalore", "asia"),
    ("mumbai", "asia"),
    ("hyderabad", "asia"),
    ("delhi", "asia"),
    ("pune", "asia"),
    ("singapur", "asia"),
    ("singapore", "asia"),
    ("endonezya", "asia"),
    ("indonesia", "asia"),
    ("bandung", "asia"),
    ("jakarta", "asia"),
    ("manila", "asia"),
    ("filipin", "asia"),
    ("philippines", "asia"),
    ("vietnam", "asia"),
    ("hanoi", "asia"),
    ("thailand", "asia"),
    ("tayland", "asia"),
    ("bangkok", "asia"),
    ("malaysia", "asia"),
    ("malezya", "asia"),
    ("kuala", "asia"),
    ("pakistan", "asia"),
    ("bangladesh", "asia"),
    ("sri lanka", "asia"),
    # Latin America
    ("brezilya", "latam"),
    ("brazil", "latam"),
    ("são paulo", "latam"),
    ("sao paulo", "latam"),
    ("rio", "latam"),
    ("meksika", "latam"),
    ("mexico", "latam"),
    ("guadalajara", "latam"),
    ("arjantin", "latam"),
    ("argentina", "latam"),
    ("buenos aires", "latam"),
    ("şili", "latam"),
    ("chile", "latam"),
    ("santiago", "latam"),
    ("kolombiya", "latam"),
    ("colombia", "latam"),
    ("peru", "latam"),
    ("uruguay", "latam"),
    # North America
    ("abd", "na"),
    ("usa", "na"),
    ("u.s.", "na"),
    ("united states", "na"),
    ("amerika", "na"),
    ("canada", "na"),
    ("kanada", "na"),
    ("california", "na"),
    ("ca)", "na"),
    ("ny)", "na"),
    ("wa)", "na"),
    ("tx)", "na"),
    ("montreal", "na"),
    ("toronto", "na"),
    ("vancouver", "na"),
    ("seattle", "na"),
    ("austin", "na"),
    ("los angeles", "na"),
    ("san francisco", "na"),
    ("new york", "na"),
    ("boston", "na"),
    ("chicago", "na"),
    # Europe
    ("bk", "europe"),
    ("uk", "europe"),
    ("ingiltere", "europe"),
    ("england", "europe"),
    ("london", "europe"),
    ("londra", "europe"),
    ("scotland", "europe"),
    ("iskoçya", "europe"),
    ("isveç", "europe"),
    ("sweden", "europe"),
    ("stockholm", "europe"),
    ("almanya", "europe"),
    ("germany", "europe"),
    ("berlin", "europe"),
    ("hamburg", "europe"),
    ("münih", "europe"),
    ("munich", "europe"),
    ("fransa", "europe"),
    ("france", "europe"),
    ("paris", "europe"),
    ("polonya", "europe"),
    ("poland", "europe"),
    ("warsaw", "europe"),
    ("varşova", "europe"),
    ("finlandiya", "europe"),
    ("finland", "europe"),
    ("helsinki", "europe"),
    ("ispanya", "europe"),
    ("spain", "europe"),
    ("madrid", "europe"),
    ("barcelona", "europe"),
    ("kıbrıs", "europe"),
    ("cyprus", "europe"),
    ("lefkoşa", "europe"),
    ("nicosia", "europe"),
    ("danimarka", "europe"),
    ("denmark", "europe"),
    ("copenhagen", "europe"),
    ("romanya", "europe"),
    ("romania", "europe"),
    ("macaristan", "europe"),
    ("hungary", "europe"),
    ("budapest", "europe"),
    ("çekya", "europe"),
    ("czech", "europe"),
    ("prague", "europe"),
    ("hollanda", "europe"),
    ("netherlands", "europe"),
    ("amsterdam", "europe"),
    ("irlanda", "europe"),
    ("ireland", "europe"),
    ("dublin", "europe"),
    ("avusturya", "europe"),
    ("austria", "europe"),
    ("vienna", "europe"),
    ("bulgaristan", "europe"),
    ("bulgaria", "europe"),
    ("sırbistan", "europe"),
    ("serbia", "europe"),
    ("ukrayna", "europe"),
    ("ukraine", "europe"),
    ("kyiv", "europe"),
    ("kiev", "europe"),
    ("hırvatistan", "europe"),
    ("croatia", "europe"),
    ("malta", "europe"),
    ("izlanda", "europe"),
    ("iceland", "europe"),
    ("norveç", "europe"),
    ("norway", "europe"),
    ("belçika", "europe"),
    ("belgium", "europe"),
    ("isviçre", "europe"),
    ("switzerland", "europe"),
    ("slovenya", "europe"),
    ("slovenia", "europe"),
    ("italya", "europe"),
    ("italy", "europe"),
    ("milan", "europe"),
    ("rome", "europe"),
    ("portekiz", "europe"),
    ("portugal", "europe"),
    ("lizbon", "europe"),
    ("lisbon", "europe"),
    ("yunanistan", "europe"),
    ("greece", "europe"),
    ("estonya", "europe"),
    ("estonia", "europe"),
    ("litvanya", "europe"),
    ("lithuania", "europe"),
    ("letonya", "europe"),
    ("latvia", "europe"),
    ("slovak", "europe"),
    ("ab)", "europe"),
]


def norm(s: str) -> str:
    return (s or "").casefold()


def bucket_from_text(*parts: str) -> str | None:
    blob = " | ".join(norm(p) for p in parts if p)
    for token, key in COUNTRY_HINTS:
        if token in blob:
            return key
    return None


def map_row_tr(region: str, city: str, company: str) -> str:
    r = region.strip()
    rn = norm(r)

    # Preserve publisher / ecosystem buckets
    if r.startswith("Yayıncılar") or "publishers" in rn or "platform" in rn:
        return TR["pub"]
    if r.startswith("Ekosistem") or "ecosystem" in rn or "fuar" in rn:
        return TR["eco"]

    # Already-clean single buckets
    clean = {
        "çin": "china",
        "china": "china",
        "japonya": "japan",
        "japan": "japan",
        "güney kore": "korea",
        "south korea": "korea",
        "latin amerika": "latam",
        "latin america": "latam",
        "avrupa": "europe",
        "europe": "europe",
        "ortadoğu": "mideast",
        "middle east": "mideast",
        "kuzey amerika": "na",
        "north america": "na",
        "diğer asya": "asia",
        "rest of asia": "asia",
        "okyanusya": "oceania",
        "oceania": "oceania",
    }
    if rn in clean and r not in (
        "Avrupa / İsrail",
        "Europe / Israel",
        "Diğer Asya / Okyanusya / MENA",
        "Other Asia / Oceania / MENA",
    ):
        return TR[clean[rn]]

    # Messy combined regions: split by city/company hints
    if r in (
        "Avrupa / İsrail",
        "Europe / Israel",
        "Diğer Asya / Okyanusya / MENA",
        "Other Asia / Oceania / MENA",
        "ABD / Kanada (+ ilk parti uzantılar)",
        "US / Canada (+ first-party extensions)",
    ) or "abd / kanada" in rn or "us / canada" in rn:
        hint = bucket_from_text(city, company)
        if hint:
            return TR[hint]
        if "asya" in rn or "asia" in rn:
            return TR["asia"]
        if "abd" in rn or "canada" in rn or "kanada" in rn:
            return TR["na"]
        return TR["europe"]

    hint = bucket_from_text(city, company, r)
    if hint:
        return TR[hint]
    if r in TR.values():
        return r
    return TR["europe"] if "avrupa" in rn or "europe" in rn else r


def tr_to_en_region(tr_region: str) -> str:
    inv = {v: k for k, v in TR.items()}
    key = inv.get(tr_region)
    if key:
        return EN[key]
    # Manual EN leftovers
    return {
        "Avrupa": "Europe",
        "Ortadoğu": "Middle East",
        "Kuzey Amerika": "North America",
        "Latin Amerika": "Latin America",
        "Çin": "China",
        "Japonya": "Japan",
        "Güney Kore": "South Korea",
        "Diğer Asya": "Rest of Asia",
        "Okyanusya": "Oceania",
        "Yayıncılar / platformlar": "Publishers / platforms",
        "Ekosistem / fuar / dernek": "Ecosystem / fair / association",
    }.get(tr_region, tr_region)


def rewrite_global() -> None:
    tr_path = DATA / "global.tr.csv"
    en_path = DATA / "global.en.csv"
    with tr_path.open(encoding="utf-8-sig", newline="") as f:
        tr_rows = list(csv.DictReader(f))
        tr_fields = list(tr_rows[0].keys())
    with en_path.open(encoding="utf-8-sig", newline="") as f:
        en_rows = list(csv.DictReader(f))
        en_fields = list(en_rows[0].keys())

    en_by_name = {r["Company"]: r for r in en_rows}
    counts: dict[str, int] = {}
    changed = 0
    for tr in tr_rows:
        old = tr["Bölge"]
        new = map_row_tr(tr["Bölge"], tr["Şehir"], tr["Firma"])
        if new != old:
            changed += 1
        tr["Bölge"] = new
        counts[new] = counts.get(new, 0) + 1
        en = en_by_name.get(tr["Firma"])
        if en:
            en["Region"] = tr_to_en_region(new)

    with tr_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=tr_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(tr_rows)
    with en_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=en_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(en_rows)

    print(f"remapped global regions: {changed} changed of {len(tr_rows)}")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4}  {k}  /  {tr_to_en_region(k)}")


if __name__ == "__main__":
    rewrite_global()
