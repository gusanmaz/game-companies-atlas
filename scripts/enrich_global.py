#!/usr/bin/env python3
"""Enrich data/global.{tr,en}.csv — Email, Sample_games/Örnek_oyunlar, Notes/Not.

Never invents emails. Keeps Company/Firma and Region/Bölge unchanged.
Syncs TR/EN by company name (row order is already aligned).
"""
from __future__ import annotations

import csv
import json
import re
import ssl
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "data" / "global.en.csv"
TR_PATH = ROOT / "data" / "global.tr.csv"
CACHE_DIR = ROOT / "scripts" / ".cache"
EMAILS_PATH = CACHE_DIR / "global_emails_curated.json"
SCRAPE_PATH = CACHE_DIR / "global_emails_scraped.json"
GAMES_PATH = CACHE_DIR / "global_games_curated.json"
NOTES_PATH = CACHE_DIR / "global_notes_curated.json"

UA = {"User-Agent": "Mozilla/5.0 (compatible; OyunFirmalariAtlas/1.0)"}
CTX = ssl.create_default_context()
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
JUNK_RE = re.compile(
    r"(example\.|sentry\.|wixpress|schema\.org|godaddy|domain\.|email\.com|"
    r"your@|noreply|no-reply|donotreply|@2x\.|\.png|\.jpg|\.gif|\.svg|"
    r"sentry\.io|cloudflare|w3\.org|github\.com|google\.com|facebook\.com)",
    re.I,
)
ROLE_LOCAL = {
    "info": "genel",
    "contact": "genel",
    "hello": "genel",
    "office": "genel",
    "mail": "genel",
    "enquiries": "genel",
    "team": "genel",
    "studio": "genel",
    "careers": "İK",
    "jobs": "İK",
    "recruit": "İK",
    "recruiting": "İK",
    "hr": "İK",
    "talent": "İK",
    "press": "basın",
    "pr": "basın",
    "media": "basın",
    "communications": "basın",
    "support": "destek",
    "help": "destek",
    "business": "iş",
    "bd": "iş",
    "bizdev": "iş",
    "partnerships": "iş",
    "partner": "iş",
    "licensing": "iş",
}
ROLE_EN = {"genel": "general", "İK": "HR", "basın": "press", "destek": "support", "iş": "biz"}


def clean_email(email: str) -> str | None:
    """Normalize scraped/curated addresses; drop obvious junk."""
    if not email:
        return None
    m = email.strip().lower()
    m = re.sub(r"^%20", "", m)
    m = m.strip(" ._<>\"'")
    m = re.sub(r"^_+", "", m)
    if not EMAIL_RE.fullmatch(m):
        return None
    if JUNK_RE.search(m):
        return None
    # reject temp/dev hosts sometimes left in page builders
    host = m.split("@", 1)[1]
    if any(x in host for x in (".dev", "wixsite", "squarespace", "example.", "test.")):
        return None
    return m


class MailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.mails: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        if href.startswith("mailto:"):
            m = href[7:].split("?")[0].strip().lower()
            if "@" in m:
                self.mails.add(m)


def fetch(url: str, timeout: int = 8) -> str | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read(350_000)
            ct = r.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in ct:
                charset = ct.split("charset=")[-1].split(";")[0].strip() or "utf-8"
            return raw.decode(charset, errors="ignore")
    except Exception:
        return None


def role_of(email: str) -> str | None:
    local = email.split("@", 1)[0].lower()
    local = re.sub(r"[^a-z]", "", local)
    for key, role in ROLE_LOCAL.items():
        if local == key or local.startswith(key):
            return role
    return None


def format_email_field(pairs: list[tuple[str, str]], lang: str) -> str:
    # Prefer genel + İK; else first two distinct roles
    by_role: dict[str, str] = {}
    for email, role in pairs:
        by_role.setdefault(role, email)
    ordered: list[tuple[str, str]] = []
    for pref in ("genel", "İK", "basın", "destek", "iş"):
        if pref in by_role:
            ordered.append((by_role[pref], pref))
    if not ordered:
        return "unknown" if lang == "en" else "bilinmiyor"
    parts = []
    for email, role in ordered[:3]:
        label = ROLE_EN.get(role, role) if lang == "en" else role
        parts.append(f"{email} ({label})")
    return "; ".join(parts)


def split_games(s: str) -> list[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def join_games(items: list[str], limit: int = 8) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for g in items:
        key = g.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(g)
        if len(out) >= limit:
            break
    return "; ".join(out)


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def scrape_emails(rows_en: list[dict], limit: int = 180) -> dict[str, list[dict]]:
    cached = load_json(SCRAPE_PATH, {})
    # Priority: majors with websites still unknown in curated
    curated = load_json(EMAILS_PATH, {})
    targets = []
    for r in rows_en:
        name = r["Company"]
        web = (r.get("Web") or "").strip()
        if not web.startswith("http"):
            continue
        if name in curated and curated[name]:
            continue
        if name in cached:  # already attempted (hit or empty)
            continue
        targets.append((name, web))
    targets = targets[:limit]
    print(f"Scraping up to {len(targets)} sites for public emails…", flush=True)
    for i, (name, web) in enumerate(targets, 1):
        found: list[dict] = []
        mails: set[str] = set()
        pages = [web.rstrip("/") + "/"]
        for path in ("/contact", "/contact-us", "/press", "/about", "/careers", "/company"):
            pages.append(urljoin(web.rstrip("/") + "/", path.lstrip("/")))
        for page in pages[:4]:
            html = fetch(page)
            if not html:
                continue
            p = MailParser()
            try:
                p.feed(html)
            except Exception:
                pass
            mails |= p.mails
            for m in EMAIL_RE.findall(html):
                mails.add(m.lower())
        for m in sorted(mails):
            cleaned = clean_email(m)
            if not cleaned:
                continue
            role = role_of(cleaned)
            if not role:
                continue
            found.append({"email": cleaned, "role": role})
        # Dedup by role
        by_role = {}
        for item in found:
            by_role.setdefault(item["role"], item)
        cached[name] = list(by_role.values())
        if i % 20 == 0:
            SCRAPE_PATH.write_text(json.dumps(cached, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  …{i}/{len(targets)}")
        time.sleep(0.15)
    SCRAPE_PATH.write_text(json.dumps(cached, ensure_ascii=False, indent=1), encoding="utf-8")
    return cached


def enrich_notes(existing: str, curated: str | None) -> tuple[str, bool]:
    """Return (note, changed). Use curated when provided and meaningfully richer."""
    cur = (existing or "").strip()
    if curated and (not cur or len(curated) >= len(cur)):
        return curated.strip(), curated.strip() != cur
    return cur, False


def apply(do_scrape: bool = True, scrape_limit: int = 120) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    curated_emails = load_json(EMAILS_PATH, {})
    games = load_json(GAMES_PATH, {})
    notes = load_json(NOTES_PATH, {})

    with EN_PATH.open(newline="", encoding="utf-8") as f:
        en_reader = csv.DictReader(f)
        en_fields = list(en_reader.fieldnames or [])
        en_rows = list(en_reader)
    with TR_PATH.open(newline="", encoding="utf-8") as f:
        tr_reader = csv.DictReader(f)
        tr_fields = list(tr_reader.fieldnames or [])
        tr_rows = list(tr_reader)

    # Ensure Email / E-posta columns exist (after Web)
    if "Email" not in en_fields:
        if "Web" in en_fields:
            i = en_fields.index("Web") + 1
            en_fields = en_fields[:i] + ["Email"] + en_fields[i:]
        else:
            en_fields.append("Email")
        for r in en_rows:
            r.setdefault("Email", "unknown")
    if "E-posta" not in tr_fields:
        if "Web" in tr_fields:
            i = tr_fields.index("Web") + 1
            tr_fields = tr_fields[:i] + ["E-posta"] + tr_fields[i:]
        else:
            tr_fields.append("E-posta")
        for r in tr_rows:
            r.setdefault("E-posta", "bilinmiyor")

    assert len(en_rows) == len(tr_rows), "TR/EN row count mismatch"
    for a, b in zip(en_rows, tr_rows):
        assert a["Company"] == b["Firma"], f"Name mismatch: {a['Company']} vs {b['Firma']}"

    scraped = scrape_emails(en_rows, limit=scrape_limit) if do_scrape else load_json(SCRAPE_PATH, {})

    stats = {
        "email_filled": 0,
        "email_already": 0,
        "email_still_unknown": 0,
        "games_expanded": 0,
        "games_already_ok": 0,
        "notes_enriched": 0,
        "rows": len(en_rows),
    }

    for en, tr in zip(en_rows, tr_rows):
        name = en["Company"]

        # --- Email ---
        pairs: list[tuple[str, str]] = []
        for src in (curated_emails.get(name), scraped.get(name)):
            if not src:
                continue
            for item in src:
                cleaned = clean_email(item.get("email", ""))
                if not cleaned:
                    continue
                role = item.get("role") or role_of(cleaned) or "genel"
                pairs.append((cleaned, role))
        # Dedup preserving order
        seen_e = set()
        uniq: list[tuple[str, str]] = []
        for email, role in pairs:
            if email in seen_e:
                continue
            seen_e.add(email)
            uniq.append((email, role))

        prev_en = (en.get("Email") or "").strip().lower()
        already_good = prev_en not in ("", "unknown", "bilinmiyor") and "@" in prev_en
        if uniq:
            en["Email"] = format_email_field(uniq, "en")
            tr["E-posta"] = format_email_field(uniq, "tr")
            if already_good:
                stats["email_already"] += 1
            else:
                stats["email_filled"] += 1
        else:
            if already_good:
                # keep existing public listing; sync TR label style lightly
                stats["email_already"] += 1
                if (tr.get("E-posta") or "").strip().lower() in ("", "bilinmiyor", "unknown"):
                    tr["E-posta"] = en.get("Email") or "bilinmiyor"
            else:
                en["Email"] = "unknown"
                tr["E-posta"] = "bilinmiyor"
                stats["email_still_unknown"] += 1

        # --- Games (prefer curated + EN titles; strip Turkish descriptive crumbs) ---
        old_en = split_games(en.get("Sample_games", ""))
        old_tr = split_games(tr.get("Örnek_oyunlar", ""))
        curated_g = split_games(games.get(name, ""))

        def usable(items: list[str]) -> list[str]:
            out = []
            for g in items:
                gl = g.lower().strip()
                if gl in ("various", "çeşitli", "—", "-", "in development", "geliştirmede"):
                    continue
                if re.search(r"[ğüşıöçĞÜŞİÖÇ]", g):
                    continue
                if any(
                    t in gl
                    for t in (
                        "geliştirme",
                        "çeşitli",
                        "altyapı",
                        "açıklanmamış",
                        "iptal",
                        "dönemsel",
                        "destek",
                    )
                ) and not any(c.isascii() and c.isalpha() for c in g[:1]):
                    continue
                # Drop pure TR descriptive tails mixed after English
                if " / " in g and re.search(r"[ğüşıöç]", g):
                    g = g.split(" / ")[0].strip()
                if " (" in g and re.search(r"[ğüşıöç]", g):
                    # keep English side before Turkish parenthetical if present
                    pass
                if re.search(r"[ğüşıöçĞÜŞİÖÇ]", g):
                    continue
                out.append(g)
            return out

        merged = usable(curated_g) + usable(old_en) + usable(old_tr)
        new_games = join_games(merged, 8)
        n_new = len(split_games(new_games))
        prev = (en.get("Sample_games") or "").strip()
        if n_new >= 3 or curated_g:
            en["Sample_games"] = new_games
            tr["Örnek_oyunlar"] = new_games
            if new_games != prev and n_new >= 3:
                stats["games_expanded"] += 1
            elif n_new >= 3:
                stats["games_already_ok"] += 1
        elif n_new:
            en["Sample_games"] = new_games
            tr["Örnek_oyunlar"] = new_games

        # --- Notes ---
        note_pack = notes.get(name) or {}
        new_en, ch_en = enrich_notes(en.get("Notes", ""), note_pack.get("en"))
        new_tr, ch_tr = enrich_notes(tr.get("Not", ""), note_pack.get("tr"))
        en["Notes"] = new_en
        tr["Not"] = new_tr
        if ch_en or ch_tr:
            stats["notes_enriched"] += 1

    with EN_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=en_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(en_rows)
    with TR_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tr_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(tr_rows)

    # Final counts
    filled = sum(
        1
        for r in en_rows
        if (r.get("Email") or "").strip().lower() not in ("", "unknown", "bilinmiyor")
    )
    games_ge3 = sum(1 for r in en_rows if len(split_games(r.get("Sample_games", ""))) >= 3)
    print("\n=== Enrichment stats ===")
    print(f"Rows:                 {stats['rows']}")
    print(f"Emails newly filled:  {stats['email_filled']}")
    print(f"Emails still unknown: {stats['email_still_unknown']}")
    print(f"Emails total filled:  {filled}")
    print(f"Games expanded:       {stats['games_expanded']}")
    print(f"Games >=3 titles:     {games_ge3}")
    print(f"Notes enriched:       {stats['notes_enriched']}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-scrape", action="store_true", help="Skip website mailto scrape")
    ap.add_argument("--scrape-limit", type=int, default=120)
    args = ap.parse_args()
    apply(do_scrape=not args.no_scrape, scrape_limit=args.scrape_limit)
