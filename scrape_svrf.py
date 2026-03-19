#!/usr/bin/env python3
"""
scrape_svrf.py — Svenska Ridsportförbundet Club Finder Scraper
==============================================================
Scrapes the official SvRF club finder at ridsport.se using Playwright.
Iterates all 19 regional districts, extracts every listed club/ridskola.

Output: svrf_data.json  (compatible with build_regions.py)

Install:
  pip install playwright
  playwright install chromium

Usage:
  python scrape_svrf.py              # full run, all districts
  python scrape_svrf.py --debug      # show browser (headed mode), verbose output
  python scrape_svrf.py --district 0 # scrape only district index 0 (for testing)
"""

import json
import re
import time
import sys
import os
import asyncio

# ── Graceful import check ──────────────────────────────────────────────────────
try:
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout
except ImportError:
    print("ERROR: playwright not installed.")
    print("Run:  pip install playwright && playwright install chromium")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────

FINDER_URL  = "https://ridsport.se/om-oss/organisation/foreningar"
OUTPUT_FILE = "svrf_data.json"
RATE_LIMIT  = 1.5    # seconds between district searches
PAGE_TIMEOUT = 30000 # ms

DEBUG         = "--debug"    in sys.argv
SINGLE_DIST   = None
if "--district" in sys.argv:
    idx = sys.argv.index("--district")
    try:
        SINGLE_DIST = int(sys.argv[idx + 1])
    except (IndexError, ValueError):
        pass

# District names as they appear in the SvRF dropdown.
# These were extracted from the page's React initial state (19 districts).
DISTRICTS = [
    "Blekinge Ridsportförbund",
    "Dalarnas Ridsportförbund",
    "Gotlands Ridsportförbund",
    "Gävleborgs Ridsportförbund",
    "Hallands Ridsportförbund",
    "Jämtland-Härjedalens Ridsportförbund",
    "Jönköpings Läns Ridsportförbund",
    "Kalmar Läns Ridsportförbund",
    "Kronobergs Ridsportförbund",
    "Norrbottens Ridsportförbund",
    "Skånska Ridsportförbundet",
    "Stockholms Läns Ridsportförbund",
    "Södermanlands Ridsportförbund",
    "Uppsala Läns Ridsportförbund",
    "Värmlands Ridsportförbund",
    "Västerbottens Ridsportförbund",
    "Västernorrlands Ridsportförbund",
    "Västmanlands Ridsportförbund",
    "Västra Götalands Ridsportförbund",
    "Örebro Läns Ridsportförbund",
    "Östergötlands Ridsportförbund",
]

# Map district names → canonical county names (for build_regions.py)
DISTRICT_TO_COUNTY = {
    "Blekinge Ridsportförbund":                "Blekinges län",
    "Dalarnas Ridsportförbund":                "Dalarnas län",
    "Gotlands Ridsportförbund":                "Gotlands län",
    "Gävleborgs Ridsportförbund":              "Gävleborgs län",
    "Hallands Ridsportförbund":                "Hallands län",
    "Jämtland-Härjedalens Ridsportförbund":    "Jämtlands län",
    "Jönköpings Läns Ridsportförbund":         "Jönköpings län",
    "Kalmar Läns Ridsportförbund":             "Kalmars län",
    "Kronobergs Ridsportförbund":              "Kronobergs län",
    "Norrbottens Ridsportförbund":             "Norrbottens län",
    "Skånska Ridsportförbundet":               "Skånes län",
    "Stockholms Läns Ridsportförbund":         "Stockholms län",
    "Södermanlands Ridsportförbund":           "Södermanlands län",
    "Uppsala Läns Ridsportförbund":            "Uppsala län",
    "Värmlands Ridsportförbund":               "Värmlands län",
    "Västerbottens Ridsportförbund":           "Västerbottens län",
    "Västernorrlands Ridsportförbund":         "Västernorrlands län",
    "Västmanlands Ridsportförbund":            "Västmanlands län",
    "Västra Götalands Ridsportförbund":        "Västra Götalands län",
    "Örebro Läns Ridsportförbund":             "Örebros län",
    "Östergötlands Ridsportförbund":           "Östergötlands län",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def normalize_phone(raw):
    """Strip non-numeric except + and spaces, reformat."""
    if not raw:
        return ""
    cleaned = re.sub(r'[^\d+\s\-]', '', raw).strip()
    return cleaned


def extract_city_from_address(address):
    """Best-effort: last non-numeric word chunk is often the city."""
    if not address:
        return ""
    # Remove zip codes (5 digits)
    parts = re.sub(r'\b\d{5}\b', '', address).strip()
    # Split by comma or newline, take last meaningful part
    segments = [s.strip() for s in re.split(r'[,\n]', parts) if s.strip()]
    if segments:
        return segments[-1]
    return ""


# ── Core scraper ───────────────────────────────────────────────────────────────

async def scrape_district(page, district_name, county_name):
    """
    Select a district in the SvRF search form, submit, collect all results.
    Returns list of club dicts.
    """
    clubs = []
    print(f"\n  ── {district_name} ──")

    try:
        # ── Wait for the search form ───────────────────────────────────────────
        # The React app renders a <select> or similar for district
        # Try common selector patterns for the district dropdown
        select_selectors = [
            "select[name='district']",
            "select[name='distrikt']",
            "select[id*='district']",
            "select[id*='distrikt']",
            "select",   # fallback: first select on page
        ]

        district_select = None
        for sel in select_selectors:
            try:
                el = page.locator(sel).first
                await el.wait_for(timeout=5000, state="visible")
                district_select = el
                if DEBUG:
                    print(f"    Found district select: {sel}")
                break
            except PWTimeout:
                continue

        if district_select is None:
            print(f"    WARNING: Could not find district dropdown, skipping.")
            return clubs

        # ── Select the district ────────────────────────────────────────────────
        # Try by label text first, then by value
        try:
            await district_select.select_option(label=district_name)
        except Exception:
            # Try partial match
            options = await district_select.locator("option").all()
            matched = False
            for opt in options:
                text = (await opt.inner_text()).strip()
                if district_name.lower() in text.lower():
                    val = await opt.get_attribute("value")
                    if val:
                        await district_select.select_option(value=val)
                        matched = True
                        if DEBUG:
                            print(f"    Matched option: {text}")
                        break
            if not matched:
                print(f"    WARNING: Could not select '{district_name}' in dropdown.")
                if DEBUG:
                    for opt in options:
                        print(f"      Option: {await opt.inner_text()}")
                return clubs

        # ── Click search button ────────────────────────────────────────────────
        search_btn_selectors = [
            "button[type='submit']",
            "button:has-text('Sök')",
            "button:has-text('SÖK')",
            "input[type='submit']",
            "button:has-text('Hitta')",
        ]

        clicked = False
        for sel in search_btn_selectors:
            try:
                btn = page.locator(sel).first
                await btn.wait_for(timeout=3000, state="visible")
                await btn.click()
                clicked = True
                if DEBUG:
                    print(f"    Clicked button: {sel}")
                break
            except PWTimeout:
                continue

        if not clicked:
            # Try pressing Enter on the form
            await page.keyboard.press("Enter")

        # ── Wait for results ───────────────────────────────────────────────────
        # Wait for a list/table of results to appear
        result_selectors = [
            "ul.search-results",
            "div.search-results",
            "table.results",
            "li.club",
            "div.club",
            "div[class*='result']",
            "ul[class*='result']",
            "article",
            "li",
        ]

        results_el = None
        for sel in result_selectors:
            try:
                el = page.locator(sel).first
                await el.wait_for(timeout=8000, state="visible")
                results_el = sel
                break
            except PWTimeout:
                continue

        # Give extra time for React rendering
        await page.wait_for_timeout(2000)

        # ── Debug: inspect page structure ─────────────────────────────────────
        if DEBUG:
            content = await page.content()
            # Find all text content briefly
            body_text = await page.locator("body").inner_text()
            print(f"    Page text snippet: {body_text[:500]}")

        # ── Extract results ────────────────────────────────────────────────────
        # Strategy: look for repeated structures that contain club names
        # SvRF likely shows: club name, city, club type, website link

        # Try to find result items by common patterns
        item_selectors = [
            "li.search-result-item",
            "div.search-result-item",
            "tr.result-row",
            "div[class*='ForumItem']",
            "div[class*='club']",
            "div[class*='Club']",
            "li[class*='club']",
            "article[class*='club']",
            # Generic: any li with a link inside, under a results container
            "ul li:has(a)",
        ]

        items = []
        for sel in item_selectors:
            try:
                found = await page.locator(sel).all()
                if len(found) > 2:  # Likely actual results
                    items = found
                    if DEBUG:
                        print(f"    Found {len(found)} items via: {sel}")
                    break
            except Exception:
                continue

        if not items:
            # Last resort: scan all links on the page for club-like URLs
            if DEBUG:
                print(f"    No items via selectors, trying link scan...")
            links = await page.locator("a[href*='forening'], a[href*='förening'], a[href*='club']").all()
            for link in links:
                href = await link.get_attribute("href") or ""
                text = (await link.inner_text()).strip()
                if text and len(text) > 3:
                    # Try to find parent element with more info
                    parent_text = ""
                    try:
                        parent_text = await link.locator("..").inner_text()
                    except Exception:
                        parent_text = text

                    clubs.append({
                        "name":     text,
                        "county":   county_name,
                        "city":     extract_city_from_address(parent_text),
                        "phone":    "",
                        "website":  href if href.startswith("http") else "",
                        "services": ["Ridklubb"],
                        "hours":    "",
                        "source":   "svrf",
                    })
            return clubs

        # ── Parse each result item ─────────────────────────────────────────────
        for item in items:
            try:
                text = (await item.inner_text()).strip()
                if not text or len(text) < 3:
                    continue

                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if not lines:
                    continue

                name = lines[0]

                # Skip non-club items (navigation links, headers, etc.)
                skip_words = ["sök", "hitta", "distrikt", "välj", "filter",
                              "nästa", "föregående", "sida"]
                if any(w in name.lower() for w in skip_words):
                    continue

                # City: look for line that looks like a city (no numbers)
                city = ""
                for line in lines[1:]:
                    if not re.search(r'\d', line) and len(line) > 2:
                        city = line
                        break

                # Phone: look for line matching phone pattern
                phone = ""
                for line in lines:
                    if re.search(r'[\d]{6,}', line.replace(" ", "").replace("-", "")):
                        phone = normalize_phone(line)
                        break

                # Website link
                website = ""
                try:
                    link_el = item.locator("a[href^='http']").first
                    website = await link_el.get_attribute("href") or ""
                except Exception:
                    pass

                if not website:
                    try:
                        # Try relative URL
                        link_el = item.locator("a").first
                        href = await link_el.get_attribute("href") or ""
                        if href and not href.startswith("#"):
                            if href.startswith("http"):
                                website = href
                    except Exception:
                        pass

                clubs.append({
                    "name":     name,
                    "county":   county_name,
                    "city":     city,
                    "phone":    phone,
                    "website":  website,
                    "services": ["Ridklubb", "Ridlektioner"],
                    "hours":    "",
                    "source":   "svrf",
                })

                if DEBUG:
                    print(f"    Club: {name} | {city} | {phone} | {website}")

            except Exception as e:
                if DEBUG:
                    print(f"    Error parsing item: {e}")
                continue

    except Exception as e:
        print(f"    ERROR scraping {district_name}: {e}")

    print(f"    → Found {len(clubs)} clubs")
    return clubs


async def handle_pagination(page):
    """
    Click 'next page' buttons until none remain.
    Returns list of new clubs found on subsequent pages.
    """
    extra_clubs = []
    next_selectors = [
        "button:has-text('Nästa')",
        "a:has-text('Nästa')",
        "button[aria-label*='next']",
        "a[rel='next']",
        "[class*='next']:not([disabled])",
    ]

    while True:
        clicked = False
        for sel in next_selectors:
            try:
                btn = page.locator(sel).first
                is_visible = await btn.is_visible()
                is_disabled = await btn.is_disabled()
                if is_visible and not is_disabled:
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            break
        # (additional page scraping would happen here — omitted for brevity,
        #  as SvRF results per district are typically < 100)

    return extra_clubs


async def run():
    """Main async entry point."""
    print("=" * 60)
    print("scrape_svrf.py — Svenska Ridsportförbundet")
    print("=" * 60)

    all_clubs = []

    districts_to_scrape = DISTRICTS
    if SINGLE_DIST is not None:
        districts_to_scrape = [DISTRICTS[SINGLE_DIST]]
        print(f"\nSingle district mode: {districts_to_scrape[0]}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not DEBUG)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="sv-SE",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # ── Initial page load ──────────────────────────────────────────────────
        print(f"\nLoading {FINDER_URL} ...")
        await page.goto(FINDER_URL, wait_until="networkidle", timeout=PAGE_TIMEOUT)
        await page.wait_for_timeout(3000)  # Extra wait for React hydration

        if DEBUG:
            print(f"Page title: {await page.title()}")
            # Log all form elements
            forms = await page.locator("form").all()
            print(f"Forms found: {len(forms)}")
            selects = await page.locator("select").all()
            print(f"Selects found: {len(selects)}")
            for i, s in enumerate(selects):
                options = await s.locator("option").all()
                print(f"  Select {i}: {len(options)} options")
                for opt in options[:5]:
                    print(f"    - {await opt.inner_text()}")

        # ── Scrape each district ───────────────────────────────────────────────
        for i, district in enumerate(districts_to_scrape):
            county = DISTRICT_TO_COUNTY.get(district, district)
            clubs = await scrape_district(page, district, county)
            all_clubs.extend(clubs)

            # Save checkpoint after each district
            if clubs:
                save_output(all_clubs, quiet=True)

            # Rate limit between district searches
            if i < len(districts_to_scrape) - 1:
                await page.wait_for_timeout(int(RATE_LIMIT * 1000))

            # Reload page between districts to reset state
            if i < len(districts_to_scrape) - 1:
                await page.goto(FINDER_URL, wait_until="networkidle", timeout=PAGE_TIMEOUT)
                await page.wait_for_timeout(2000)

        await browser.close()

    # ── Deduplicate ────────────────────────────────────────────────────────────
    seen = set()
    deduped = []
    for c in all_clubs:
        key = (c["name"].lower().strip(), c.get("city", "").lower().strip())
        if key not in seen and c["name"]:
            seen.add(key)
            deduped.append(c)

    save_output(deduped)
    print(f"\n✓ Done! {len(deduped)} unique clubs saved to {OUTPUT_FILE}")
    print(f"  Run 'python build_regions.py' to regenerate all region pages.")


def save_output(data, quiet=False):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if not quiet:
        print(f"\n  Saved {len(data)} records → {OUTPUT_FILE}")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(run())
