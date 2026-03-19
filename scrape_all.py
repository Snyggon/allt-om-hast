#!/usr/bin/env python3
"""
scrape_all.py — Master Ridskolor Scraper
=========================================
Runs all available scrapers in sequence, then merges + deduplicates
all JSON data files and triggers a site rebuild.

Usage:
  python scrape_all.py              # run everything
  python scrape_all.py --hitta      # hitta.se only
  python scrape_all.py --svrf       # ridsport.se only (needs playwright)
  python scrape_all.py --merge      # merge existing JSON files + rebuild only
  python scrape_all.py --stats      # print statistics about current data

What it does:
  1. scrape_hitta.py  → hitta_data.json     (~500 entries, ~20 min)
  2. scrape_svrf.py   → svrf_data.json      (~450 entries, ~5 min + playwright)
  3. Merges all *.json data files           (dedup by name+city, fuzzy)
  4. python build_regions.py               (regenerate all 21 region pages)
"""

import json
import os
import sys
import re
import glob
import subprocess
import unicodedata
from collections import defaultdict

RUN_HITTA  = "--hitta" in sys.argv or len(sys.argv) == 1
RUN_SVRF   = "--svrf"  in sys.argv or len(sys.argv) == 1
MERGE_ONLY = "--merge" in sys.argv
STATS_ONLY = "--stats" in sys.argv

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))


# ── Fuzzy deduplication ────────────────────────────────────────────────────────

def slugify(text):
    """Convert to lowercase ASCII slug for fuzzy comparison."""
    if not text:
        return ""
    text = text.lower().strip()
    # Normalize unicode (ä→a, ö→o, etc.)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Remove common suffixes that vary between sources
    for suffix in [" ab", " hb", " ef", " ideell förening", " ridklubb",
                   " ridskola", " ridsallskap", " ridsällskap"]:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
    text = re.sub(r'[^a-z0-9]', '', text)
    return text


def dedup_entries(entries):
    """
    Deduplicate entries by fuzzy (name, city) match.
    Merges fields from multiple sources, preferring hitta.se for addresses
    and svrf for 'official' status.
    """
    # Group by fuzzy key
    groups = defaultdict(list)
    for e in entries:
        key = (slugify(e.get("name", "")), slugify(e.get("city", "")))
        groups[key].append(e)

    merged = []
    for key, group in groups.items():
        if not group:
            continue
        # Start with first entry as base
        base = dict(group[0])
        for other in group[1:]:
            # Prefer non-empty values from other sources
            for field in ["phone", "website", "email", "street", "hours"]:
                if not base.get(field) and other.get(field):
                    base[field] = other[field]
            # Merge services (union)
            svcs = list(set(
                (base.get("services") or []) +
                (other.get("services") or [])
            ))
            base["services"] = svcs[:6]
            # Prefer precise coordinates
            if base.get("lat") is None and other.get("lat") is not None:
                base["lat"] = other["lat"]
                base["lng"] = other["lng"]
        merged.append(base)

    return merged


# ── Statistics ─────────────────────────────────────────────────────────────────

def print_stats():
    json_files = [f for f in glob.glob(os.path.join(BASE_DIR, "*.json"))
                  if not f.endswith(("ridskolor.json",))]  # skip template

    all_entries = []
    for path in json_files:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                all_entries.extend(data)
                print(f"  {os.path.basename(path):30s}  {len(data):>5} entries")
        except Exception as e:
            print(f"  {os.path.basename(path):30s}  ERROR: {e}")

    deduped = dedup_entries(all_entries)
    print(f"\n  {'TOTAL (raw)':30s}  {len(all_entries):>5}")
    print(f"  {'TOTAL (after dedup)':30s}  {len(deduped):>5}")

    # Per county breakdown
    county_counts = defaultdict(int)
    for e in deduped:
        county_counts[e.get("county", "Unknown")] += 1
    print("\n  Per county:")
    for county, count in sorted(county_counts.items()):
        print(f"    {county:35s}  {count:>4}")

    # Fields coverage
    print("\n  Field coverage:")
    fields = ["phone", "website", "email", "lat", "hours", "street"]
    for field in fields:
        filled = sum(1 for e in deduped if e.get(field))
        pct = filled / len(deduped) * 100 if deduped else 0
        print(f"    {field:12s}  {filled:>4} / {len(deduped)}  ({pct:.0f}%)")


# ── Run a scraper script ───────────────────────────────────────────────────────

def run_script(script_name, extra_args=None):
    args = [sys.executable, os.path.join(BASE_DIR, script_name)]
    if extra_args:
        args.extend(extra_args)
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(args)}")
    print('='*60)
    result = subprocess.run(args, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"WARNING: {script_name} exited with code {result.returncode}")
    return result.returncode == 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("scrape_all.py — Ridskolor i Sverige Master Scraper")
    print("=" * 60)

    if STATS_ONLY:
        print("\nCurrent data statistics:")
        print_stats()
        return

    if MERGE_ONLY:
        print("\nMerge-only mode: skipping scrapers.")
    else:
        if RUN_HITTA:
            run_script("scrape_hitta.py")

        if RUN_SVRF:
            # Check playwright is available
            try:
                import playwright
                run_script("scrape_svrf.py")
            except ImportError:
                print("\nSkipping scrape_svrf.py — playwright not installed.")
                print("To install:  pip install playwright && playwright install chromium")

    # ── Post-scrape: rebuild site ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("Rebuilding site with build_regions.py...")
    print('='*60)
    run_script("build_regions.py")

    # ── Final stats ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("Final data statistics:")
    print_stats()

    print(f"\n✓ All done! Site has been rebuilt.")
    print(f"  Open index.html in your browser to verify.")


if __name__ == "__main__":
    main()
