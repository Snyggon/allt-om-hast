#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
import_to_wordpress.py — Import JSON data into WordPress
=========================================================
Generates a WordPress WXR (XML) import file from all JSON data files.
This can be imported directly via WordPress Admin > Tools > Import.

No WP-CLI or server access needed — just upload the XML file.

Usage:
  python import_to_wordpress.py              # Generate import file
  python import_to_wordpress.py --stats      # Show stats only
"""

import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import argparse

# ── Data files to import ──────────────────────────────────────────────────────

DATA_FILES = {
    "ridskolor": {
        "file": "hitta_data.json",
        "category": "Ridskolor",
        "category_slug": "ridskolor",
    },
    "turridning": {
        "file": "data/turridning.json",
        "category": "Turridning & Ridturer",
        "category_slug": "turridning",
    },
    "hastkalas": {
        "file": "data/hastkalas.json",
        "category": "Hästkalas & Ponnykalas",
        "category_slug": "hastkalas",
    },
    "ridlager": {
        "file": "data/ridlager.json",
        "category": "Ridläger & Sommarläger",
        "category_slug": "ridlager",
    },
    "hastpensionat": {
        "file": "data/hastpensionat.json",
        "category": "Hästpensionat & Hästhotell",
        "category_slug": "hastpensionat",
    },
    "hovslagare": {
        "file": "data/hovslagare.json",
        "category": "Hovslagare",
        "category_slug": "hovslagare",
    },
}

OUTPUT_FILE = "wordpress_import.xml"

# ── County slug mapping ──────────────────────────────────────────────────────

COUNTY_SLUGS = {
    "stockholms län":       "stockholms-lan",
    "uppsala län":          "uppsala-lan",
    "södermanlands län":    "sodermanlands-lan",
    "östergötlands län":    "ostergotlands-lan",
    "jönköpings län":       "jonkopings-lan",
    "kronobergs län":       "kronobergs-lan",
    "kalmars län":          "kalmars-lan",
    "gotlands län":         "gotlands-lan",
    "blekinges län":        "blekinges-lan",
    "skånes län":           "skanes-lan",
    "hallands län":         "hallands-lan",
    "västra götalands län": "vastra-gotalands-lan",
    "värmlands län":        "varmlands-lan",
    "örebros län":          "orebros-lan",
    "västmanlands län":     "vastmanlands-lan",
    "dalarnas län":         "dalarnas-lan",
    "gävleborgs län":       "gavleborgs-lan",
    "västernorrlands län":  "vasternorrlands-lan",
    "jämtlands län":        "jamtlands-lan",
    "västerbottens län":    "vasterbottens-lan",
    "norrbottens län":      "norrbottens-lan",
}


def slugify(text):
    """Simple slug generator."""
    import re
    text = text.lower().strip()
    text = text.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def show_stats():
    """Show statistics for all data files."""
    print("=" * 60)
    print("Data Import Statistik")
    print("=" * 60)

    grand_total = 0
    for key, info in DATA_FILES.items():
        path = info["file"]
        if not os.path.exists(path):
            print(f"\n  {info['category']}: FIL SAKNAS ({path})")
            continue

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        total = len(data)
        grand_total += total
        with_coords = sum(1 for d in data if d.get("lat") and d.get("lng"))
        with_web = sum(1 for d in data if d.get("website"))
        with_phone = sum(1 for d in data if d.get("phone"))

        print(f"\n  {info['category']} ({key})")
        print(f"    Fil: {path}")
        print(f"    Poster: {total}")
        print(f"    Med koordinater: {with_coords}")
        print(f"    Med hemsida: {with_web}")
        print(f"    Med telefon: {with_phone}")

    print(f"\n  {'='*40}")
    print(f"  Totalt: {grand_total} verksamheter")
    print()


def xml_escape(text):
    """Escape XML special characters."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def generate_wxr():
    """Generate WordPress WXR import XML file."""
    print("=" * 60)
    print("Genererar WordPress Import (WXR)")
    print("=" * 60)

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<rss version="2.0"')
    lines.append('  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"')
    lines.append('  xmlns:content="http://purl.org/rss/1.0/modules/content/"')
    lines.append('  xmlns:wfw="http://wellformedweb.org/CommentAPI/"')
    lines.append('  xmlns:dc="http://purl.org/dc/elements/1.1/"')
    lines.append('  xmlns:wp="http://wordpress.org/export/1.2/">')
    lines.append('<channel>')
    lines.append('  <title>HästSverige Import</title>')
    lines.append('  <wp:wxr_version>1.2</wp:wxr_version>')

    post_id = 1000
    total = 0

    for key, info in DATA_FILES.items():
        path = info["file"]
        if not os.path.exists(path):
            print(f"  Hoppar över {info['category']} — fil saknas: {path}")
            continue

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n  Processar {info['category']}: {len(data)} poster")

        for entry in data:
            name = (entry.get("name") or "").strip()
            if not name:
                continue

            post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            post_name = slugify(name)

            lines.append('  <item>')
            lines.append(f'    <title>{xml_escape(name)}</title>')
            lines.append(f'    <dc:creator>admin</dc:creator>')
            lines.append(f'    <content:encoded><![CDATA[]]></content:encoded>')
            lines.append(f'    <excerpt:encoded><![CDATA[]]></excerpt:encoded>')
            lines.append(f'    <wp:post_id>{post_id}</wp:post_id>')
            lines.append(f'    <wp:post_date>{post_date}</wp:post_date>')
            lines.append(f'    <wp:status>publish</wp:status>')
            lines.append(f'    <wp:post_type>listing</wp:post_type>')
            lines.append(f'    <wp:post_name>{xml_escape(post_name)}</wp:post_name>')

            # Category taxonomy
            lines.append(f'    <category domain="listing_category" nicename="{xml_escape(info["category_slug"])}">{xml_escape(info["category"])}</category>')

            # County taxonomy
            county = (entry.get("county") or "").strip()
            if county:
                county_slug = COUNTY_SLUGS.get(county.lower(), slugify(county))
                lines.append(f'    <category domain="county" nicename="{xml_escape(county_slug)}">{xml_escape(county)}</category>')

            # Meta fields
            meta_map = {
                "_listing_phone":   entry.get("phone", ""),
                "_listing_email":   entry.get("email", ""),
                "_listing_website": entry.get("website", ""),
                "_listing_street":  entry.get("street", ""),
                "_listing_city":    entry.get("city", ""),
                "_listing_lat":     str(entry.get("lat", "")) if entry.get("lat") else "",
                "_listing_lng":     str(entry.get("lng", "")) if entry.get("lng") else "",
                "_listing_hours":   entry.get("hours", ""),
                "_listing_tier":    "free",
            }

            for meta_key, meta_value in meta_map.items():
                val = str(meta_value).strip() if meta_value else ""
                if val:
                    lines.append(f'    <wp:postmeta>')
                    lines.append(f'      <wp:meta_key>{xml_escape(meta_key)}</wp:meta_key>')
                    lines.append(f'      <wp:meta_value><![CDATA[{val}]]></wp:meta_value>')
                    lines.append(f'    </wp:postmeta>')

            lines.append('  </item>')
            post_id += 1
            total += 1

    lines.append('</channel>')
    lines.append('</rss>')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n{'='*60}")
    print(f"  WordPress import-fil skapad!")
    print(f"  Fil: {OUTPUT_FILE}")
    print(f"  Verksamheter: {total}")
    print(f"")
    print(f"  Importera via:")
    print(f"  WordPress Admin > Verktyg > Importera > WordPress")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate WordPress import from JSON data")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    args = parser.parse_args()

    if args.stats:
        show_stats()
    else:
        generate_wxr()


if __name__ == "__main__":
    main()
