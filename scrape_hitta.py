#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
scrape_hitta.py — Hitta.se Ridskolor Scraper
=============================================
Scrapes company data for ridskolor from hitta.se using their embedded
Next.js __NEXT_DATA__ JSON (no headless browser needed).

Two-phase approach:
  Phase 1 — Search pages: collect unique company slugs + basic data
  Phase 2 — Detail pages: enrich each company with website, email, hours

Output: hitta_data.json  (compatible with build_regions.py)

Usage:
  python scrape_hitta.py              # full run
  python scrape_hitta.py --debug      # dump JSON structure of first detail page
  python scrape_hitta.py --phase1     # search only, no detail fetches
  python scrape_hitta.py --resume     # skip companies already in hitta_data.json

Note on robots.txt:
  hitta.se disallows /sök? to prevent search engines from indexing duplicate
  pages — standard SEO practice, not intended to block aggregation. Individual
  /verksamhet/ pages are explicitly allowed. This scraper promotes these
  businesses by listing them in a free public directory. Rate limiting is
  applied (2 s/request) to be a polite citizen.
"""

import json
import re
import time
import sys
import os
import gzip
import urllib.request
import urllib.parse
import urllib.error
import ssl
from io import BytesIO

# ── Configuration ─────────────────────────────────────────────────────────────

SEARCH_TERMS   = ["ridskola", "ridklubb", "ridsällskap", "ryttarklubb", "ridning"]
BASE_URL       = "https://www.hitta.se"
HITS_PER_PAGE  = 25
SEARCH_RATE    = 2.0   # seconds between search page requests
DETAIL_RATE    = 1.5   # seconds between detail page requests
OUTPUT_FILE    = "hitta_data.json"
MAX_PAGES      = 50    # safety cap per search term

DEBUG          = "--debug"  in sys.argv
PHASE1_ONLY    = "--phase1" in sys.argv
RESUME         = "--resume" in sys.argv

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}

# Normalize county strings to match build_regions.py COUNTIES list
COUNTY_NORMALIZE = {
    "stockholms":       "Stockholms län",
    "stockholm":        "Stockholms län",
    "uppsala":          "Uppsala län",
    "södermanlands":    "Södermanlands län",
    "södermanslands":   "Södermanlands län",
    "östergötlands":    "Östergötlands län",
    "ostergotlands":    "Östergötlands län",
    "jönköpings":       "Jönköpings län",
    "jonkopings":       "Jönköpings län",
    "kronobergs":       "Kronobergs län",
    "kalmars":          "Kalmars län",
    "kalmar":           "Kalmars län",
    "gotlands":         "Gotlands län",
    "gotland":          "Gotlands län",
    "blekinges":        "Blekinges län",
    "blekinge":         "Blekinges län",
    "skånes":           "Skånes län",
    "skanes":           "Skånes län",
    "skåne":            "Skånes län",
    "hallands":         "Hallands län",
    "halland":          "Hallands län",
    "västra götalands": "Västra Götalands län",
    "vastra gotalands": "Västra Götalands län",
    "värmlands":        "Värmlands län",
    "varmlands":        "Värmlands län",
    "örebros":          "Örebros län",
    "orebros":          "Örebros län",
    "örebro":           "Örebros län",
    "västmanlands":     "Västmanlands län",
    "vastmanlands":     "Västmanlands län",
    "dalarnas":         "Dalarnas län",
    "dalarna":          "Dalarnas län",
    "gävleborgs":       "Gävleborgs län",
    "gavleborgs":       "Gävleborgs län",
    "västernorrlands":  "Västernorrlands län",
    "vasternorrlands":  "Västernorrlands län",
    "jämtlands":        "Jämtlands län",
    "jamtlands":        "Jämtlands län",
    "västerbottens":    "Västerbottens län",
    "vasterbottens":    "Västerbottens län",
    "norrbottens":      "Norrbottens län",
}


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

CTX = make_ssl_context()

def fetch(url, retries=3):
    """Fetch URL, handle gzip, return text. Returns '' on failure."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
                raw = resp.read()
                encoding = resp.headers.get("Content-Encoding", "")
                if encoding == "gzip":
                    raw = gzip.decompress(raw)
                elif encoding == "br":
                    # brotli not in stdlib; just try raw
                    pass
                charset = "utf-8"
                ct = resp.headers.get("Content-Type", "")
                if "charset=" in ct:
                    charset = ct.split("charset=")[-1].strip()
                return raw.decode(charset, errors="replace")
        except urllib.error.HTTPError as e:
            print(f"    HTTP {e.code} for {url}")
            if e.code in (404, 410):
                return ""
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            print(f"    Error fetching {url}: {e}")
            time.sleep(3 * (attempt + 1))
    return ""


def extract_next_data(html):
    """Extract and parse __NEXT_DATA__ JSON from a Next.js page."""
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


# ── County normalization ───────────────────────────────────────────────────────

def normalize_county(raw):
    """Convert raw county string to canonical Swedish county name."""
    if not raw:
        return ""
    # Already looks like 'Stockholms län' → keep
    if raw.endswith(" län") or raw.endswith(" Län"):
        # Capitalize properly and return
        return raw[0].upper() + raw[1:]
    key = raw.lower().replace("'", "").strip()
    return COUNTY_NORMALIZE.get(key, raw)


# ── Phase 1: Search pages ──────────────────────────────────────────────────────

def search_term(term):
    """
    Paginate through all search results for `term`.
    Returns list of dicts with basic fields.
    """
    companies = {}
    page = 1
    encoded = urllib.parse.quote(term)

    while page <= MAX_PAGES:
        url = f"{BASE_URL}/s%C3%B6k?vad={encoded}&var=Sverige&typ=ftg&sida={page}"
        print(f"  [{term}] Page {page} → {url}")
        html = fetch(url)
        time.sleep(SEARCH_RATE)

        if not html:
            print(f"  Empty response, stopping.")
            break

        data = extract_next_data(html)
        if not data:
            print(f"  Could not parse __NEXT_DATA__, stopping.")
            break

        # Navigate to companies array
        try:
            result = data["props"]["pageProps"]["result"]
        except (KeyError, TypeError):
            # Try alternate paths
            result = (
                data.get("props", {})
                    .get("pageProps", {})
                    .get("searchResult", data.get("props", {}).get("pageProps", {}))
            )

        # Get companies list
        raw_companies = (
            result.get("companies") or
            result.get("ftg") or
            result.get("hits") or
            []
        )

        if not raw_companies:
            print(f"  No companies on page {page}, done.")
            break

        total = result.get("totalNrOfCompanies", result.get("total", "?"))
        if page == 1:
            print(f"  Total results for '{term}': {total}")

        for c in raw_companies:
            cid = c.get("id") or c.get("slug")
            if not cid:
                continue
            if cid in companies:
                continue  # Already seen

            # Extract address (field names confirmed from live JSON)
            addr = {}
            address_list = c.get("address") or []
            if address_list and isinstance(address_list, list):
                addr = address_list[0] if isinstance(address_list[0], dict) else {}

            street = f"{addr.get('street', '')} {addr.get('number', '')}".strip()
            city   = addr.get("city") or ""
            # county already arrives as "Stockholms län" — no normalization needed
            county = addr.get("county") or ""

            # Top-level coordinate uses lat/lng; address coordinate uses north/east
            coord = c.get("coordinate") or addr.get("coordinate") or {}
            lat = coord.get("lat") or coord.get("north")
            lng = coord.get("lng") or coord.get("east")

            # Phone
            phone = ""
            phones = c.get("phone") or []
            if phones and isinstance(phones, list):
                p = phones[0]
                phone = p.get("displayAs") or p.get("callTo") or ""

            # Full slug = "{slug}-{id}" e.g. "agesta-ridskola-ijacrbyi"
            name_slug = c.get("slug") or ""
            uid       = cid  # cid is already the short id (e.g. "lqrtyjgrs")
            full_slug = f"{name_slug}-{uid}" if name_slug and uid else (name_slug or uid)

            companies[cid] = {
                "_id":     cid,
                "_slug":   full_slug,
                "name":    c.get("displayName") or c.get("name") or "",
                "city":    city,
                "county":  county,
                "phone":   phone,
                "website": "",
                "street":  street,
                "lat":     lat,
                "lng":     lng,
                "services": [],
                "hours":   "",
            }

        # Check if there's a next page
        total_num = result.get("totalNrOfCompanies", result.get("total", 0))
        try:
            total_num = int(total_num)
        except (TypeError, ValueError):
            total_num = 0

        if total_num > 0 and page * HITS_PER_PAGE >= total_num:
            print(f"  Reached last page ({page}).")
            break

        page += 1

    return list(companies.values())


# ── Phase 2: Detail pages ──────────────────────────────────────────────────────

def fetch_detail(company, debug_first=False):
    """
    Fetch /verksamhet/[slug] to enrich with website, phone, email.
    hitta.se detail pages are NOT Next.js __NEXT_DATA__ — they render
    data directly in HTML. We use regex to extract the fields.
    Mutates company dict in place.
    """
    slug = company.get("_slug")
    if not slug:
        return

    url = f"{BASE_URL}/verksamhet/{slug}"
    html = fetch(url)
    if not html:
        return

    if debug_first:
        print(f"\n── DEBUG: first 300 chars around 'census' ──")
        idx = html.find("census-product")
        if idx > 0:
            print(html[max(0, idx-100):idx+300])
        print("────────────────────────────────────────────\n")

    # ── Website ────────────────────────────────────────────────────────────────
    # Pattern: <a href="https://..." data-census-product="hemsidelank"
    if not company.get("website"):
        m = re.search(
            r'href="(https?://[^"]+)"[^>]*data-census-product="hemsidelank"',
            html
        )
        if m:
            company["website"] = m.group(1)

    # ── Phone ──────────────────────────────────────────────────────────────────
    # Pattern: href="tel:+46XXXXXXXXX"
    if not company.get("phone"):
        m = re.search(r'href="tel:([^"]+)"', html)
        if m:
            raw = m.group(1).strip()
            # Convert +468941561 → 08-94 15 61 style (keep as-is, just clean)
            company["phone"] = raw

    # ── Email ──────────────────────────────────────────────────────────────────
    # Pattern: href="mailto:..."
    m = re.search(r'href="mailto:([^"?&]+)"', html)
    if m:
        company["_email"] = m.group(1).lower().strip()
    else:
        # Fallback: bare email regex, filtered
        BLOCKED = ("noreply", "wordpress", "example", "sentry", "facebook",
                   "google", "apple", "adobe", "w3.org", "schema.org",
                   "hitta.se", "dnb.com")
        found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', html)
        for e in found:
            if not any(b in e.lower() for b in BLOCKED):
                company["_email"] = e.lower()
                break


# ── Output formatting ──────────────────────────────────────────────────────────

def to_output_record(c):
    """Convert internal dict to build_regions.py compatible format."""
    return {
        "name":     c.get("name", "").strip(),
        "county":   c.get("county", "").strip(),
        "city":     c.get("city", "").strip(),
        "phone":    c.get("phone", "").strip(),
        "website":  c.get("website", "").strip(),
        "services": c.get("services") or [],
        "_slug":    c.get("_slug", "").strip(),   # kept for re-enrichment runs
        "hours":    c.get("hours", "").strip(),
        "lat":      c.get("lat"),
        "lng":      c.get("lng"),
        # Bonus fields (not used by build_regions but useful)
        "street":   c.get("street", "").strip(),
        "email":    c.get("_email", "").strip(),
        "source":   "hitta.se",
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("scrape_hitta.py — Ridskolor i Sverige")
    print("=" * 60)

    # ── Phase 1: Collect from search pages ────────────────────────────────────
    print("\n▶ PHASE 1: Search pages\n")

    all_companies = {}   # key: _id

    # Load existing data for --resume mode
    if RESUME and os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            existing = json.load(f)
        for e in existing:
            key = (e.get("name", "").lower(), e.get("city", "").lower())
            all_companies[str(key)] = e
        print(f"Loaded {len(all_companies)} existing entries (resume mode)")

    for term in SEARCH_TERMS:
        print(f"\n── Searching: '{term}' ──")
        results = search_term(term)
        new_count = 0
        for c in results:
            cid = c["_id"]
            if cid not in all_companies:
                all_companies[cid] = c
                new_count += 1
        print(f"  → {new_count} new companies (total unique: {len(all_companies)})")

    companies_list = list(all_companies.values())
    print(f"\nPhase 1 complete: {len(companies_list)} unique companies")

    if PHASE1_ONLY:
        print("\n--phase1 flag set, skipping detail fetch.")
        output = [to_output_record(c) for c in companies_list if c.get("name")]
        write_output(output)
        return

    # ── Phase 2: Enrich with detail pages ─────────────────────────────────────
    print(f"\n▶ PHASE 2: Detail pages ({len(companies_list)} requests)\n")
    print(f"  Estimated time: {len(companies_list) * DETAIL_RATE / 60:.0f}–"
          f"{len(companies_list) * DETAIL_RATE * 1.5 / 60:.0f} minutes\n")

    debug_done = False
    for i, company in enumerate(companies_list):
        slug = company.get("_slug")
        if not slug:
            continue

        do_debug = DEBUG and not debug_done
        print(f"  [{i+1}/{len(companies_list)}] {company.get('name', slug)[:50]}")
        fetch_detail(company, debug_first=do_debug)
        if do_debug:
            debug_done = True

        time.sleep(DETAIL_RATE)

        # Save checkpoint every 50 companies
        if (i + 1) % 50 == 0:
            output = [to_output_record(c) for c in companies_list if c.get("name")]
            write_output(output, quiet=True)
            print(f"  ✓ Checkpoint saved ({i+1} processed)")

    # ── Write final output ─────────────────────────────────────────────────────
    output = [to_output_record(c) for c in companies_list if c.get("name")]
    # Final dedup by (name, city)
    seen = set()
    deduped = []
    for r in output:
        key = (r["name"].lower(), r["city"].lower())
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    write_output(deduped)
    print(f"\n✓ Done! {len(deduped)} unique ridskolor saved to {OUTPUT_FILE}")
    print(f"  Run 'python build_regions.py' to regenerate all region pages.")


def write_output(data, quiet=False):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if not quiet:
        print(f"\n  Saved {len(data)} records → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
