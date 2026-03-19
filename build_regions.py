#!/usr/bin/env python3
"""
build_regions.py — HästSverige
Generates all region pages, js/data.js, and sitemap.xml
Run: python build_regions.py
"""
import json
import os
import glob
import re
from datetime import datetime

SITE_URL = "https://ridskolor-i-sverige.se"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COUNTIES = [
    {"name": "Stockholms län", "slug": "stockholm"},
    {"name": "Uppsala län", "slug": "uppsala"},
    {"name": "Södermanlands län", "slug": "sodermanland"},
    {"name": "Östergötlands län", "slug": "ostergotland"},
    {"name": "Jönköpings län", "slug": "jonkoping"},
    {"name": "Kronobergs län", "slug": "kronoberg"},
    {"name": "Kalmars län", "slug": "kalmar"},
    {"name": "Gotlands län", "slug": "gotland"},
    {"name": "Blekinges län", "slug": "blekinge"},
    {"name": "Skånes län", "slug": "skane"},
    {"name": "Hallands län", "slug": "halland"},
    {"name": "Västra Götalands län", "slug": "vastra-gotaland"},
    {"name": "Värmlands län", "slug": "varmland"},
    {"name": "Örebros län", "slug": "orebro"},
    {"name": "Västmanlands län", "slug": "vastmanland"},
    {"name": "Dalarnas län", "slug": "dalarna"},
    {"name": "Gävleborgs län", "slug": "gavleborg"},
    {"name": "Västernorrlands län", "slug": "vasternorrland"},
    {"name": "Jämtlands län", "slug": "jamtland"},
    {"name": "Västerbottens län", "slug": "vasterbotten"},
    {"name": "Norrbottens län", "slug": "norrbotten"},
]

# Category mapping: file basename -> category slug and display name
CATEGORY_MAP = {
    "hitta_data.json":      {"slug": "ridskolor",     "name": "Ridskolor"},
    "ridskolor.json":       {"slug": "ridskolor",     "name": "Ridskolor"},
    "turridning.json":      {"slug": "turridning",    "name": "Turridning & Ridturer"},
    "hastkalas.json":       {"slug": "hastkalas",      "name": "Hästkalas & Ponnykalas"},
    "ridlager.json":        {"slug": "ridlager",       "name": "Ridläger & Sommarläger"},
    "hastpensionat.json":   {"slug": "hastpensionat",  "name": "Hästpensionat & Hästhotell"},
    "hovslagare.json":      {"slug": "hovslagare",     "name": "Hovslagare"},
}

CATEGORIES = [
    {"slug": "ridskolor",     "name": "Ridskolor",                    "icon": "🏇", "color": "#C4607A"},
    {"slug": "turridning",    "name": "Turridning & Ridturer",        "icon": "🌲", "color": "#4A7C59"},
    {"slug": "hastkalas",     "name": "Hästkalas & Ponnykalas",       "icon": "🎉", "color": "#9B59B6"},
    {"slug": "ridlager",      "name": "Ridläger & Sommarläger",       "icon": "⛺", "color": "#E67E22"},
    {"slug": "hastpensionat", "name": "Hästpensionat & Hästhotell",   "icon": "🏠", "color": "#3498DB"},
    {"slug": "hovslagare",    "name": "Hovslagare",                   "icon": "🔨", "color": "#C9963C"},
]


def load_all_data():
    """Read all JSON files in BASE_DIR and data/ subdirectory, combine entries."""
    entries = []

    # Load from root directory
    for filepath in glob.glob(os.path.join(BASE_DIR, "*.json")):
        basename = os.path.basename(filepath)
        if basename == "wordpress_import.xml" or basename.startswith("package"):
            continue
        cat_info = CATEGORY_MAP.get(basename)
        with open(filepath, encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    if cat_info:
                        for e in data:
                            if not e.get("category"):
                                e["category"] = cat_info["slug"]
                    entries.extend(data)
                    print(f"  Loaded {len(data)} entries from {basename}")
            except json.JSONDecodeError as e:
                print(f"  Warning: Could not parse {filepath}: {e}")

    # Load from data/ subdirectory
    data_dir = os.path.join(BASE_DIR, "data")
    if os.path.isdir(data_dir):
        for filepath in glob.glob(os.path.join(data_dir, "*.json")):
            basename = os.path.basename(filepath)
            cat_info = CATEGORY_MAP.get(basename)
            with open(filepath, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        if cat_info:
                            for e in data:
                                if not e.get("category"):
                                    e["category"] = cat_info["slug"]
                        entries.extend(data)
                        print(f"  Loaded {len(data)} entries from data/{basename}")
                except json.JSONDecodeError as e:
                    print(f"  Warning: Could not parse {filepath}: {e}")

    # Deduplicate by (name.lower(), city.lower())
    seen = set()
    unique = []
    for e in entries:
        key = (e.get("name", "").lower().strip(), e.get("city", "").lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(e)

    print(f"  Total unique entries: {len(unique)}")

    # Print category breakdown
    from collections import Counter
    cat_counts = Counter(e.get("category", "unknown") for e in unique)
    for cat, count in cat_counts.most_common():
        print(f"    {cat}: {count}")

    return unique


def write_data_js(entries):
    """Write js/data.js with all entries as window.RIDSKOLOR_DATA."""
    js_dir = os.path.join(BASE_DIR, "js")
    os.makedirs(js_dir, exist_ok=True)
    filepath = os.path.join(js_dir, "data.js")

    json_str = json.dumps(entries, ensure_ascii=False, indent=2)
    content = f"// Auto-generated by build_regions.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"window.RIDSKOLOR_DATA = {json_str};\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Written: js/data.js ({len(entries)} entries)")


def get_county_entries(all_entries, county_name):
    """Filter entries by county name."""
    return [e for e in all_entries if e.get("county") == county_name]


def get_top_cities(entries, n=3):
    """Return top N cities by listing count."""
    from collections import Counter
    city_counts = Counter(e.get("city", "") for e in entries if e.get("city"))
    return [city for city, _ in city_counts.most_common(n)]


def escape_html(s):
    """Basic HTML escaping."""
    if not isinstance(s, str):
        return ""
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_schema_itemlist(entries, county_name, county_slug):
    """Build Schema.org ItemList JSON-LD for a county page."""
    items = []
    for i, e in enumerate(entries, 1):
        item = {
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "SportsActivityLocation",
                "name": e.get("name", ""),
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": e.get("city", ""),
                    "addressRegion": county_name,
                    "addressCountry": "SE"
                },
                "telephone": e.get("phone", ""),
                "url": e.get("website", "")
            }
        }
        items.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Hästverksamheter i {county_name}",
        "description": f"Komplett lista över hästverksamheter i {county_name}",
        "numberOfItems": len(entries),
        "itemListElement": items
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_breadcrumb_schema(county_name):
    """Build Schema.org BreadcrumbList."""
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Startsida",
                "item": SITE_URL + "/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": f"Hästverksamheter i {county_name}",
                "item": f"{SITE_URL}/regions/{next((c['slug'] for c in COUNTIES if c['name'] == county_name), '')}.html"
            }
        ]
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_county_cards_html(all_entries, prefix=""):
    """Generate county cards for the region index section."""
    cards = []
    icons = ["🐎", "🐴", "🏇", "🦄"]
    for i, county in enumerate(COUNTIES):
        count = len(get_county_entries(all_entries, county["name"]))
        icon = icons[i % len(icons)]
        cards.append(
            f'<a href="{prefix}regions/{county["slug"]}.html" class="county-card">'
            f'<div class="county-card-icon">{icon}</div>'
            f'<h3>{escape_html(county["name"])}</h3>'
            f'<p>{count} verksamheter</p>'
            f'<span class="county-card-arrow">→</span>'
            f'</a>'
        )
    return "\n        ".join(cards)


def build_region_page(county, all_entries, all_counties):
    """Generate a complete HTML page for a county/region."""
    county_name = county["name"]
    county_slug = county["slug"]

    entries = get_county_entries(all_entries, county_name)
    count = len(entries)
    top_cities = get_top_cities(entries, 3)
    top_cities_str = ", ".join(top_cities) if top_cities else county_name

    # Prev/next county
    idx = next((i for i, c in enumerate(all_counties) if c["slug"] == county_slug), 0)
    prev_county = all_counties[idx - 1] if idx > 0 else all_counties[-1]
    next_county = all_counties[idx + 1] if idx < len(all_counties) - 1 else all_counties[0]

    schema_itemlist = build_schema_itemlist(entries, county_name, county_slug)
    schema_breadcrumb = build_breadcrumb_schema(county_name)

    meta_desc = (
        f"Hitta hästverksamheter i {county_name}. "
        f"Vi listar {count} verksamheter — ridskolor, turridning, hästkalas, ridläger, hästpensionat och hovslagare. "
        f"Jämför och kontakta direkt."
    )

    county_cards_html = build_county_cards_html(all_entries, prefix="../")

    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hästverksamheter i {escape_html(county_name)} – HästSverige</title>
  <meta name="description" content="{escape_html(meta_desc)}">
  <link rel="canonical" href="{SITE_URL}/regions/{county_slug}.html">

  <!-- Open Graph -->
  <meta property="og:title" content="Hästverksamheter i {escape_html(county_name)} – HästSverige">
  <meta property="og:description" content="{escape_html(meta_desc)}">
  <meta property="og:url" content="{SITE_URL}/regions/{county_slug}.html">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{SITE_URL}/og-image.jpg">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Hästverksamheter i {escape_html(county_name)}">
  <meta name="twitter:description" content="{escape_html(meta_desc)}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

  <!-- Schema.org ItemList -->
  <script type="application/ld+json">
{schema_itemlist}
  </script>
  <!-- Schema.org BreadcrumbList -->
  <script type="application/ld+json">
{schema_breadcrumb}
  </script>

  <!-- GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  </script>
</head>
<body class="region-page" data-county="{escape_html(county_name)}">

  <!-- Navigation -->
  <nav id="main-nav">
    <div class="nav-inner">
      <a href="../index.html" class="nav-logo">
        <span class="logo-horse">&#x1F434;</span> HästSverige
      </a>
      <ul class="nav-links">
        <li><a href="../index.html">Startsida</a></li>
        <li><a href="../index.html#kategorier">Kategorier</a></li>
        <li><a href="../index.html#regioner">Alla Län</a></li>
        <li><a href="../index.html#search">Sök</a></li>
        <li><a href="../blogg/index.html">Blogg</a></li>
        <li><a href="../annonsera.html" class="nav-cta">Annonsera</a></li>
      </ul>
      <button class="nav-hamburger" aria-label="Meny" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>

  <!-- County Hero -->
  <div class="county-hero">
    <div class="hero-bg-pattern"></div>
    <div class="container">
      <div class="breadcrumb" style="color:rgba(255,255,255,0.7); padding-bottom:1rem;">
        <a href="../index.html" style="color:rgba(255,255,255,0.85);">Startsida</a>
        <span>&#x203A;</span>
        <span>Hästverksamheter i {escape_html(county_name)}</span>
      </div>
      <p class="hero-eyebrow">&#x1F434; {count} verksamheter listade</p>
      <h1>Hästverksamheter i {escape_html(county_name)}</h1>
      <div class="hero-divider"></div>
      <p>Inkl. {escape_html(top_cities_str)}. Ridskolor, turridning, hästkalas, ridläger, hästpensionat och hovslagare.</p>
    </div>
    <div class="hero-wave">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 70" preserveAspectRatio="none">
        <path d="M0,35 C240,70 480,0 720,35 C960,70 1200,0 1440,35 L1440,70 L0,70 Z" fill="#FDF7F2"/>
      </svg>
    </div>
  </div>

  <div class="container">

    <!-- Prev/Next Navigation -->
    <nav class="nav-counties" aria-label="Länsnavigation">
      <a href="{prev_county['slug']}.html">&#8592; {escape_html(prev_county['name'])}</a>
      <a href="../index.html#regioner">Alla Län</a>
      <a href="{next_county['slug']}.html">{escape_html(next_county['name'])} &#8594;</a>
    </nav>

    <!-- Search & Table Section -->
    <section id="search" class="search-section">
      <div class="section-header">
        <h2>Sök bland verksamheter i {escape_html(county_name)}</h2>
      </div>
      <div class="search-controls">
        <div class="search-input-wrap">
          <span class="search-icon">&#x1F50D;</span>
          <input type="text" id="search-input" placeholder="Sök namn, stad, kategori..." aria-label="Sök verksamhet">
        </div>
        <select id="county-filter" aria-label="Filtrera på län">
          <option value="">Alla Län</option>
        </select>
        <select id="category-filter" aria-label="Filtrera på kategori">
          <option value="">Alla Kategorier</option>
        </select>
      </div>
      <p id="result-count" class="result-count"></p>
      <div class="table-wrapper">
        <table class="directory-table" role="grid">
          <thead>
            <tr>
              <th data-col="0">Namn <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
              <th data-col="1">Kategori <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
              <th data-col="2">Län <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
              <th data-col="3">Stad <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
              <th data-col="4">Telefon <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
              <th data-col="5">Webbplats <span class="sort-icon" aria-hidden="true">&#x21C5;</span></th>
            </tr>
          </thead>
          <tbody id="table-body">
            <tr><td colspan="6" style="text-align:center;padding:2rem;color:#666;">Laddar verksamheter...</td></tr>
          </tbody>
        </table>
      </div>
      <div id="pagination"></div>
    </section>

    <!-- Leaflet Map for this county -->
    <section class="fullmap-section" style="background:transparent;">
      <div class="section-header">
        <h2>Karta — {escape_html(county_name)}</h2>
      </div>
      <div class="fullmap-wrap">
        <div id="leaflet-map"></div>
      </div>
    </section>

    <!-- All Regions -->
    <section id="regioner" class="regions-section" style="background:transparent;">
      <div class="section-header centered">
        <h2>Andra Län</h2>
        <p>Bläddra bland hästverksamheter i hela Sverige.</p>
      </div>
      <div class="county-cards">
        {county_cards_html}
      </div>
    </section>

  </div>

  <!-- Map Tooltip -->
  <div id="map-tooltip" role="tooltip"></div>

  <!-- Footer -->
  <footer>
    <div class="footer-inner">
      <div class="footer-col">
        <div class="footer-logo">&#x1F434; HästSverige</div>
        <p class="footer-tagline">Sveriges kompletta hästportal.<br>Ridskolor, turridning, hästkalas och mer.</p>
      </div>
      <div class="footer-col">
        <h4>Snabblänkar</h4>
        <ul>
          <li><a href="../index.html">Startsida</a></li>
          <li><a href="../index.html#search">Sök</a></li>
          <li><a href="../blogg/index.html">Blogg</a></li>
          <li><a href="../index.html#regioner">Alla Län</a></li>
          <li><a href="../annonsera.html">Annonsera</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Populära Län</h4>
        <ul>
          <li><a href="../regions/stockholm.html">Stockholm</a></li>
          <li><a href="../regions/vastra-gotaland.html">Västra Götaland</a></li>
          <li><a href="../regions/skane.html">Skåne</a></li>
          <li><a href="../regions/dalarna.html">Dalarna</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; {datetime.now().year} HästSverige &mdash; Sveriges kompletta hästportal.</p>
    </div>
  </footer>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="../js/data.js"></script>
  <script src="../js/main.js"></script>

</body>
</html>"""

    return html


def write_region_pages(all_entries):
    """Generate and write all region HTML pages."""
    regions_dir = os.path.join(BASE_DIR, "regions")
    os.makedirs(regions_dir, exist_ok=True)

    for county in COUNTIES:
        html = build_region_page(county, all_entries, COUNTIES)
        filepath = os.path.join(regions_dir, f"{county['slug']}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        count = len(get_county_entries(all_entries, county["name"]))
        print(f"  Written: regions/{county['slug']}.html ({count} entries)")


def write_sitemap(all_entries):
    """Generate sitemap.xml."""
    today = datetime.now().strftime("%Y-%m-%d")

    urls = []

    def add_url(loc, priority="0.8", changefreq="weekly"):
        urls.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    # Main pages
    add_url(f"{SITE_URL}/", priority="1.0", changefreq="daily")
    add_url(f"{SITE_URL}/annonsera.html", priority="0.7", changefreq="monthly")
    add_url(f"{SITE_URL}/blogg/", priority="0.8", changefreq="weekly")

    # Blog articles
    blog_slugs = [
        "hitta-ridskola",
        "ridlektioner-barn",
        "klassisk-vs-western",
        "kosta-ridning",
        "fordeler-ridning-barn",
        "vad-ska-du-ha-pa-dig",
        "hast-evenemang-2026",
        "ryttarmarken",
    ]
    for slug in blog_slugs:
        add_url(f"{SITE_URL}/blogg/{slug}.html", priority="0.7", changefreq="monthly")

    # Region pages
    for county in COUNTIES:
        add_url(f"{SITE_URL}/regions/{county['slug']}.html", priority="0.9", changefreq="weekly")

    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join(urls) + """
</urlset>
"""

    filepath = os.path.join(BASE_DIR, "sitemap.xml")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"  Written: sitemap.xml ({len(urls)} URLs)")


def main():
    print("=" * 60)
    print("HästSverige — Build Script")
    print("=" * 60)

    print("\n[1/4] Loading data from JSON files...")
    all_entries = load_all_data()

    print("\n[2/4] Writing js/data.js...")
    write_data_js(all_entries)

    print("\n[3/4] Generating region pages...")
    write_region_pages(all_entries)

    print("\n[4/4] Generating sitemap.xml...")
    write_sitemap(all_entries)

    print("\n" + "=" * 60)
    print(f"Build complete! Generated:")
    print(f"  - js/data.js ({len(all_entries)} verksamheter)")
    print(f"  - {len(COUNTIES)} region pages in regions/")
    print(f"  - sitemap.xml")
    print("=" * 60)


if __name__ == "__main__":
    main()
