#!/usr/bin/env python3
"""
scrape_emails.py — Ridskolor i Sverige Email Scraper
Reads all JSON data files, fetches websites, extracts emails.
Output: contacts.csv
Usage: python scrape_emails.py
"""
import json
import glob
import re
import time
import csv
import ssl
import os
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse
from urllib.error import URLError, HTTPError

SITE_URL = "https://ridskolor-i-sverige.se"
RATE_LIMIT = 1.2  # seconds between requests
OUTPUT_FILE = "contacts.csv"
PATHS_TO_CHECK = ["/", "/kontakt", "/kontakta-oss", "/om-oss", "/about", "/contact"]
EMAIL_BLACKLIST = ["noreply", "wordpress", "example", "test", "info@wordpress", "support@"]

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')


def load_all_data():
    """Load all JSON files from current directory and combine entries."""
    entries = []
    for filepath in glob.glob("*.json"):
        with open(filepath, encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    entries.extend(data)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {filepath}")

    # Deduplicate by (name.lower(), city.lower())
    seen = set()
    unique = []
    for e in entries:
        key = (e.get("name", "").lower(), e.get("city", "").lower())
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def fetch_url(url, timeout=10):
    """Fetch a URL and return its HTML content as a string."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RidskolorBot/1.0)"}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_emails(html):
    """Extract and filter email addresses from HTML content."""
    emails = set(EMAIL_RE.findall(html))
    filtered = set()
    for email in emails:
        email_lower = email.lower()
        if any(b in email_lower for b in EMAIL_BLACKLIST):
            continue
        if len(email) > 60:
            continue
        filtered.add(email.lower())
    return filtered


def get_county_slug(county_name):
    """Convert a county name to its URL slug."""
    slug_map = {
        "Stockholms län": "stockholm",
        "Uppsala län": "uppsala",
        "Södermanlands län": "sodermanland",
        "Östergötlands län": "ostergotland",
        "Jönköpings län": "jonkoping",
        "Kronobergs län": "kronoberg",
        "Kalmars län": "kalmar",
        "Gotlands län": "gotland",
        "Blekinges län": "blekinge",
        "Skånes län": "skane",
        "Hallands län": "halland",
        "Västra Götalands län": "vastra-gotaland",
        "Värmlands län": "varmland",
        "Örebros län": "orebro",
        "Västmanlands län": "vastmanland",
        "Dalarnas län": "dalarna",
        "Gävleborgs län": "gavleborg",
        "Västernorrlands län": "vasternorrland",
        "Jämtlands län": "jamtland",
        "Västerbottens län": "vasterbotten",
        "Norrbottens län": "norrbotten",
    }
    return slug_map.get(county_name, "")


def main():
    """Main scraping function."""
    entries = load_all_data()
    print(f"Loaded {len(entries)} entries")

    results = []

    for i, entry in enumerate(entries):
        website = entry.get("website", "").strip()
        if not website:
            continue

        name = entry.get("name", "")
        county = entry.get("county", "")
        city = entry.get("city", "")
        slug = get_county_slug(county)
        listing_url = f"{SITE_URL}/regions/{slug}.html" if slug else SITE_URL

        print(f"[{i+1}/{len(entries)}] Scraping {name} ({website})...")

        found_emails = set()
        for path in PATHS_TO_CHECK:
            url = urljoin(website, path)
            html = fetch_url(url)
            if html:
                found_emails.update(extract_emails(html))
            time.sleep(RATE_LIMIT)

        if found_emails:
            for email in found_emails:
                results.append({
                    "name": name,
                    "county": county,
                    "city": city,
                    "email": email,
                    "website": website,
                    "listing_url": listing_url
                })
            print(f"  -> Found: {', '.join(found_emails)}")
        else:
            print(f"  -> No emails found")

    # Write CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "county", "city", "email", "website", "listing_url"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone! Saved {len(results)} contacts to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
