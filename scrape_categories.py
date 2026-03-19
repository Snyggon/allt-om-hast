#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
scrape_categories.py — Hitta.se Multi-Category Scraper
======================================================
Generic scraper for multiple horse-related business categories on hitta.se.
Re-uses the same fetch/parse approach as scrape_hitta.py (search pages with
__NEXT_DATA__ JSON, then detail page enrichment via HTML regex).

Categories:
  turridning    — Turridning & Ridturer
  hastkalas     — Hästkalas & Ponnykalas
  ridlager      — Ridläger & Sommarläger
  hastpensionat — Hästpensionat & Hästhotell
  hovslagare    — Hovslagare

Usage:
  python scrape_categories.py                        # run ALL categories
  python scrape_categories.py --category turridning  # run one category
  python scrape_categories.py --phase1               # search only, no details
  python scrape_categories.py --resume               # skip already fetched
  python scrape_categories.py --stats                # show stats only
  python scrape_categories.py --debug                # dump first detail page JSON
"""

import json
import re
import time
import os
import argparse
import gzip
import urllib.request
import urllib.parse
import urllib.error
import ssl
from io import BytesIO

# ── Categories ────────────────────────────────────────────────────────────────

CATEGORIES = {
    "turridning": {
        "name": "Turridning & Ridturer",
        "search_terms": ["turridning", "ridtur", "ridturer", "skogsridning", "islandshäst ridtur", "ponnyridning tur"],
        "output_file": "data/turridning.json"
    },
    "hastkalas": {
        "name": "Hästkalas & Ponnykalas",
        "search_terms": ["hästkalas", "ponnykalas", "barnkalas häst", "ponnyridning kalas", "kalas ridning"],
        "output_file": "data/hastkalas.json"
    },
    "ridlager": {
        "name": "Ridläger & Sommarläger",
        "search_terms": ["ridläger", "hästläger", "sommarläger ridning", "ridkurs sommar", "ponnykurs"],
        "output_file": "data/ridlager.json"
    },
    "hastpensionat": {
        "name": "Hästpensionat & Hästhotell",
        "search_terms": ["hästpensionat", "hästhotell", "inackordering häst", "stallplats", "hästpension"],
        "output_file": "data/hastpensionat.json"
    },
    "hovslagare": {
        "name": "Hovslagare",
        "search_terms": ["hovslagare", "hovvård", "hovbeslag"],
        "output_file": "data/hovslagare.json"
    }
}

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL       = "https://www.hitta.se"
HITS_PER_PAGE  = 25
SEARCH_RATE    = 2.0   # seconds between search page requests
DETAIL_RATE    = 1.5   # seconds between detail page requests
MAX_PAGES      = 50    # safety cap per search term
CHECKPOINT_INTERVAL = 50  # save every N companies during detail phase

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


# ── HTTP helpers ──────────────────────────────────────────────────────────────

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


# ── County normalization ──────────────────────────────────────────────────────

def normalize_county(raw):
    """Convert raw county string to canonical Swedish county name."""
    if not raw:
        return ""
    # Already looks like 'Stockholms län' -> keep
    if raw.endswith(" län") or raw.endswith(" Län"):
        return raw[0].upper() + raw[1:]
    key = raw.lower().replace("'", "").strip()
    return COUNTY_NORMALIZE.get(key, raw)


# ── Phase 1: Search pages ────────────────────────────────────────────────────

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
        print(f"  [{term}] Page {page} -> {url}")
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
            uid       = cid
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


# ── Phase 2: Detail pages ────────────────────────────────────────────────────

def fetch_detail(company, debug_first=False):
    """
    Fetch /verksamhet/[slug] to enrich with website, phone, email.
    hitta.se detail pages are NOT Next.js __NEXT_DATA__ -- they render
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
        print(f"\n-- DEBUG: first 300 chars around 'census' --")
        idx = html.find("census-product")
        if idx > 0:
            print(html[max(0, idx-100):idx+300])
        print("--------------------------------------------\n")

    # ── Website ───────────────────────────────────────────────────────────────
    if not company.get("website"):
        m = re.search(
            r'href="(https?://[^"]+)"[^>]*data-census-product="hemsidelank"',
            html
        )
        if m:
            company["website"] = m.group(1)

    # ── Phone ─────────────────────────────────────────────────────────────────
    if not company.get("phone"):
        m = re.search(r'href="tel:([^"]+)"', html)
        if m:
            raw = m.group(1).strip()
            company["phone"] = raw

    # ── Email ─────────────────────────────────────────────────────────────────
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


# ── Output formatting ─────────────────────────────────────────────────────────

def to_output_record(c, category_key):
    """Convert internal dict to output format with category field."""
    return {
        "name":     c.get("name", "").strip(),
        "category": category_key,
        "county":   c.get("county", "").strip(),
        "city":     c.get("city", "").strip(),
        "phone":    c.get("phone", "").strip(),
        "website":  c.get("website", "").strip(),
        "services": c.get("services") or [],
        "_slug":    c.get("_slug", "").strip(),
        "hours":    c.get("hours", "").strip(),
        "lat":      c.get("lat"),
        "lng":      c.get("lng"),
        "street":   c.get("street", "").strip(),
        "email":    c.get("_email", "").strip(),
        "source":   "hitta.se",
    }


def write_output(data, output_file, quiet=False):
    """Write data to JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if not quiet:
        print(f"\n  Saved {len(data)} records -> {output_file}")


# ── Stats command ─────────────────────────────────────────────────────────────

def show_stats():
    """Display statistics for all category data files."""
    print("=" * 60)
    print("scrape_categories.py — Statistik")
    print("=" * 60)

    total_all = 0
    for key, cat in CATEGORIES.items():
        output_file = cat["output_file"]
        if not os.path.exists(output_file):
            print(f"\n  {cat['name']} ({key})")
            print(f"    Fil: {output_file} — saknas")
            continue

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        total = len(data)
        total_all += total

        with_website = sum(1 for d in data if d.get("website"))
        with_email   = sum(1 for d in data if d.get("email"))
        with_phone   = sum(1 for d in data if d.get("phone"))
        with_coords  = sum(1 for d in data if d.get("lat") and d.get("lng"))

        # County distribution
        counties = {}
        for d in data:
            c = d.get("county", "Okänt") or "Okänt"
            counties[c] = counties.get(c, 0) + 1

        print(f"\n  {cat['name']} ({key})")
        print(f"    Fil:      {output_file}")
        print(f"    Totalt:   {total} verksamheter")
        print(f"    Hemsida:  {with_website} ({100*with_website//max(total,1)}%)")
        print(f"    E-post:   {with_email} ({100*with_email//max(total,1)}%)")
        print(f"    Telefon:  {with_phone} ({100*with_phone//max(total,1)}%)")
        print(f"    Karta:    {with_coords} ({100*with_coords//max(total,1)}%)")

        # Top 5 counties
        sorted_counties = sorted(counties.items(), key=lambda x: -x[1])[:5]
        if sorted_counties:
            print(f"    Topp län:")
            for county, count in sorted_counties:
                print(f"      {county}: {count}")

    print(f"\n  {'='*40}")
    print(f"  Totalt alla kategorier: {total_all} verksamheter")
    print()


# ── Run one category ─────────────────────────────────────────────────────────

def run_category(key, cat, phase1_only=False, resume=False, debug=False):
    """Run scraping for a single category."""
    print(f"\n{'='*60}")
    print(f"  Kategori: {cat['name']} ({key})")
    print(f"  Söktermer: {', '.join(cat['search_terms'])}")
    print(f"  Output: {cat['output_file']}")
    print(f"{'='*60}")

    output_file = cat["output_file"]

    # ── Phase 1: Collect from search pages ────────────────────────────────────
    print(f"\n  PHASE 1: Sök ({cat['name']})\n")

    all_companies = {}  # key: _id

    # Load existing data for --resume mode
    if resume and os.path.exists(output_file):
        with open(output_file, encoding="utf-8") as f:
            existing = json.load(f)
        for e in existing:
            # Use _slug as key if available, else (name, city)
            slug = e.get("_slug", "")
            if slug:
                all_companies[slug] = e
            else:
                k = (e.get("name", "").lower(), e.get("city", "").lower())
                all_companies[str(k)] = e
        print(f"  Loaded {len(all_companies)} existing entries (resume mode)")

    for term in cat["search_terms"]:
        print(f"\n  -- Searching: '{term}' --")
        results = search_term(term)
        new_count = 0
        for c in results:
            cid = c["_id"]
            if cid not in all_companies:
                all_companies[cid] = c
                new_count += 1
        print(f"  -> {new_count} new companies (total unique: {len(all_companies)})")

    companies_list = list(all_companies.values())
    print(f"\n  Phase 1 complete: {len(companies_list)} unique companies for {cat['name']}")

    if phase1_only:
        print(f"\n  --phase1 flag set, skipping detail fetch.")
        output = [to_output_record(c, key) for c in companies_list if c.get("name")]
        write_output(output, output_file)
        return output

    # ── Phase 2: Enrich with detail pages ─────────────────────────────────────
    # Determine which companies need detail fetching
    need_detail = []
    skip_count = 0
    for c in companies_list:
        if not c.get("_slug"):
            continue
        # In resume mode, skip entries that already have website or email
        if resume and (c.get("website") or c.get("_email") or c.get("email")):
            skip_count += 1
            continue
        need_detail.append(c)

    if skip_count > 0:
        print(f"\n  Skipped {skip_count} already-enriched companies (resume mode)")

    print(f"\n  PHASE 2: Detail pages ({len(need_detail)} requests)")
    if need_detail:
        print(f"  Estimated time: {len(need_detail) * DETAIL_RATE / 60:.0f}-"
              f"{len(need_detail) * DETAIL_RATE * 1.5 / 60:.0f} minutes\n")

    debug_done = False
    for i, company in enumerate(need_detail):
        slug = company.get("_slug")
        if not slug:
            continue

        do_debug = debug and not debug_done
        print(f"  [{i+1}/{len(need_detail)}] {company.get('name', slug)[:50]}")
        fetch_detail(company, debug_first=do_debug)
        if do_debug:
            debug_done = True

        time.sleep(DETAIL_RATE)

        # Save checkpoint every CHECKPOINT_INTERVAL companies
        if (i + 1) % CHECKPOINT_INTERVAL == 0:
            output = [to_output_record(c, key) for c in companies_list if c.get("name")]
            write_output(output, output_file, quiet=True)
            print(f"  Checkpoint saved ({i+1}/{len(need_detail)} processed)")

    # ── Write final output ────────────────────────────────────────────────────
    output = [to_output_record(c, key) for c in companies_list if c.get("name")]

    # Final dedup by (name, city)
    seen = set()
    deduped = []
    for r in output:
        dedup_key = (r["name"].lower(), r["city"].lower())
        if dedup_key not in seen:
            seen.add(dedup_key)
            deduped.append(r)

    write_output(deduped, output_file)
    print(f"\n  Done! {len(deduped)} unique {cat['name']} saved to {output_file}")

    return deduped


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hitta.se Multi-Category Scraper for horse businesses in Sweden"
    )
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORIES.keys()),
        help="Run only this category (default: all)"
    )
    parser.add_argument(
        "--phase1",
        action="store_true",
        help="Search only, skip detail page fetching"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip companies already in output files"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics for existing data files"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Dump JSON structure of first detail page per category"
    )
    args = parser.parse_args()

    # Ensure data/ directory exists
    os.makedirs("data", exist_ok=True)

    # Stats mode — just show stats and exit
    if args.stats:
        show_stats()
        return

    print("=" * 60)
    print("scrape_categories.py — Hästverksamheter i Sverige")
    print("=" * 60)

    # Determine which categories to run
    if args.category:
        categories_to_run = {args.category: CATEGORIES[args.category]}
        print(f"\n  Running single category: {args.category}")
    else:
        categories_to_run = CATEGORIES
        print(f"\n  Running ALL {len(CATEGORIES)} categories")

    if args.phase1:
        print("  Mode: Phase 1 only (search, no details)")
    if args.resume:
        print("  Mode: Resume (skip already fetched)")

    grand_total = 0
    summary = []

    for key, cat in categories_to_run.items():
        try:
            results = run_category(
                key, cat,
                phase1_only=args.phase1,
                resume=args.resume,
                debug=args.debug
            )
            count = len(results) if results else 0
            grand_total += count
            summary.append((cat["name"], count, cat["output_file"]))
        except KeyboardInterrupt:
            print(f"\n\n  Interrupted during {cat['name']}. Partial data may be saved.")
            break
        except Exception as e:
            print(f"\n  ERROR in {cat['name']}: {e}")
            summary.append((cat["name"], -1, cat["output_file"]))
            continue

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SAMMANFATTNING")
    print(f"{'='*60}")
    for name, count, path in summary:
        if count < 0:
            print(f"    {name}: FEL")
        else:
            print(f"    {name}: {count} verksamheter -> {path}")
    print(f"\n    Totalt: {grand_total} verksamheter")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
