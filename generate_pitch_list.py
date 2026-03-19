#!/usr/bin/env python3
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
generate_pitch_list.py
======================
Läser hitta_data.json och genererar en säljlista med ridskolor
som SAKNAR hemsida men HAR telefonnummer.

Output:
  pitch_list.csv   — för kallringning och e-post
  pitch_list.html  — snyggt formaterad HTML för manuellt bruk

Kör:
  python generate_pitch_list.py
"""

import json
import csv
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data():
    """Läs in alla JSON-datafiler och slå ihop."""
    entries = []
    import glob
    for path in glob.glob(os.path.join(BASE_DIR, "*.json")):
        basename = os.path.basename(path)
        if basename in ("ridskolor.json",):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)
        except Exception as e:
            print(f"  Kunde inte läsa {basename}: {e}")
    return entries


def generate_pitch_list():
    entries = load_data()

    # Filtrera: saknar hemsida men har telefon
    targets = [
        e for e in entries
        if not e.get("website") and e.get("phone")
    ]

    # Sortera på län > stad > namn
    targets.sort(key=lambda x: (
        x.get("county", ""),
        x.get("city", ""),
        x.get("name", "")
    ))

    print(f"\n{'='*60}")
    print(f"Ridskolor UTAN hemsida MEN med telefon: {len(targets)}")
    print(f"Totalt i databasen: {len(entries)}")
    print(f"{'='*60}\n")

    # Per-county breakdown
    county_counts = defaultdict(int)
    for e in targets:
        county_counts[e.get("county", "Okänt")] += 1
    for county, count in sorted(county_counts.items()):
        print(f"  {county:35s}  {count:>3} potentiella kunder")

    # Skriv CSV
    csv_path = os.path.join(BASE_DIR, "pitch_list.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name", "county", "city", "phone", "street", "email"
        ])
        writer.writeheader()
        for e in targets:
            writer.writerow({
                "name": e.get("name", ""),
                "county": e.get("county", ""),
                "city": e.get("city", ""),
                "phone": e.get("phone", ""),
                "street": e.get("street", ""),
                "email": e.get("email", ""),
            })
    print(f"\n  ✓ pitch_list.csv skriven ({len(targets)} rader)")

    # Skriv HTML
    html_path = os.path.join(BASE_DIR, "pitch_list.html")
    rows_html = ""
    for i, e in enumerate(targets, 1):
        rows_html += f"""
        <tr>
          <td class="num">{i}</td>
          <td><strong>{e.get('name','')}</strong></td>
          <td>{e.get('county','')}</td>
          <td>{e.get('city','')}</td>
          <td><a href="tel:{e.get('phone','')}">{e.get('phone','')}</a></td>
          <td>{e.get('email','')}</td>
          <td>
            <span class="status-badge status-new">Ej kontaktad</span>
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Säljlista — Ridskolor utan hemsida</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background:#F8F4F6; color:#2A1820; margin:0; padding:2rem; }}
    h1 {{ color:#8B3A52; margin-bottom:0.25rem; }}
    .meta {{ color:#9E8090; font-size:0.9rem; margin-bottom:2rem; }}
    .stats {{ display:flex; gap:2rem; margin-bottom:2rem; }}
    .stat {{ background:white; border-radius:12px; padding:1rem 1.5rem; box-shadow:0 2px 8px rgba(160,60,90,0.1); }}
    .stat strong {{ font-size:1.8rem; color:#C4607A; display:block; }}
    .stat span {{ font-size:0.82rem; color:#9E8090; }}
    table {{ width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(160,60,90,0.1); }}
    th {{ background:linear-gradient(135deg,#8B3A52,#C4607A); color:white; text-align:left; padding:0.75rem 1rem; font-size:0.85rem; }}
    td {{ padding:0.7rem 1rem; border-bottom:1px solid #EDD8E0; font-size:0.9rem; }}
    tr:last-child td {{ border-bottom:none; }}
    tr:hover td {{ background:#FDF0F3; }}
    .num {{ color:#9E8090; font-size:0.8rem; }}
    a {{ color:#C4607A; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .status-badge {{ display:inline-block; padding:0.2rem 0.65rem; border-radius:50px; font-size:0.75rem; font-weight:600; }}
    .status-new {{ background:#FDF0F3; color:#8B3A52; }}
    .status-contacted {{ background:#EBF5EE; color:#2E5240; }}
    .status-sold {{ background:#FFF8E7; color:#7A5C00; }}
    .filter-row {{ margin-bottom:1rem; display:flex; gap:1rem; align-items:center; flex-wrap:wrap; }}
    input[type=text] {{ padding:0.5rem 0.9rem; border:1.5px solid #EDD8E0; border-radius:8px; font-size:0.9rem; width:280px; }}
    input[type=text]:focus {{ outline:none; border-color:#C4607A; }}
    .pitch-box {{ background:white; border-radius:12px; padding:1.5rem 2rem; box-shadow:0 2px 8px rgba(160,60,90,0.1); margin-bottom:2rem; }}
    .pitch-box h2 {{ color:#8B3A52; font-size:1.1rem; margin-bottom:0.75rem; }}
    pre {{ background:#FDF0F3; border-radius:8px; padding:1rem; font-size:0.85rem; white-space:pre-wrap; line-height:1.6; color:#2A1820; }}
  </style>
</head>
<body>

<h1>Säljlista — Ridskolor utan hemsida</h1>
<p class="meta">Genererad: {__import__('datetime').date.today()} &bull; Ridskolor-i-Sverige.se</p>

<div class="stats">
  <div class="stat">
    <strong>{len(targets)}</strong>
    <span>Potentiella kunder (har telefon)</span>
  </div>
  <div class="stat">
    <strong>{len(entries)}</strong>
    <span>Totalt i katalogen</span>
  </div>
  <div class="stat">
    <strong>2 500 kr</strong>
    <span>Enkel hemsida (startpris)</span>
  </div>
</div>

<div class="pitch-box">
  <h2>📞 Telefon-pitch (ca 30 sek)</h2>
  <pre>"Hej, mitt namn är [NAMN] och jag ringer från Ridskolor-i-Sverige.se.
Vi har [RIDSKOLANS NAMN] listad i vår katalog — ni syns på Google
när folk söker ridskola i [STAD]. Jag ringde för att fråga om ni
är intresserade av en egen hemsida? Vi bygger enkla och snygga
ridskole-hemsidor för 2 500 kronor. Kan jag skicka er ett par exempel
och en offert?" </pre>
</div>

<div class="pitch-box">
  <h2>📧 E-post-mall</h2>
  <pre>Ämne: Er ridskola syns på Google — vill ni ha en hemsida?

Hej [NAMN],

Vi driver Ridskolor-i-Sverige.se — Sveriges mest kompletta katalog
med 480+ ridskolor. [RIDSKOLANS NAMN] finns redan listad hos oss
och visas när folk söker ridskola i [STAD/LÄN] på Google.

Vi märker att ni inte har en egen hemsida och erbjuder just nu
att bygga en snygg och mobilanpassad ridskole-hemsida för:

  🐴 Enkel landningssida: 2 500 kr (engång)
  🌐 Komplett 3-5 sidor: 5 000 kr (engång)
  📅 Löpande underhåll: 195 kr/mån

Hemsidan inkluderar: presentation, lektioner, priser,
kontaktformulär och karta. Vi kopplar den även till er kataloglista.

Svarar du på det här mejlet kan vi skicka ett par exempel och sätta
upp ett kostnadsfritt möte.

Med vänliga hälsningar,
[DITT NAMN]
Ridskolor-i-Sverige.se</pre>
</div>

<div class="filter-row">
  <input type="text" id="search-filter" placeholder="Filtrera på namn, stad, telefon...">
  <span id="visible-count" style="color:#9E8090;font-size:0.88rem;">{len(targets)} visas</span>
</div>

<table id="pitch-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Ridskola</th>
      <th>Län</th>
      <th>Stad</th>
      <th>Telefon</th>
      <th>E-post</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>

<script>
  var input = document.getElementById('search-filter');
  var counter = document.getElementById('visible-count');
  input.addEventListener('input', function() {{
    var q = this.value.toLowerCase();
    var rows = document.querySelectorAll('#pitch-table tbody tr');
    var visible = 0;
    rows.forEach(function(row) {{
      var text = row.textContent.toLowerCase();
      if (!q || text.includes(q)) {{
        row.style.display = '';
        visible++;
      }} else {{
        row.style.display = 'none';
      }}
    }});
    counter.textContent = visible + ' visas';
  }});
</script>

</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ pitch_list.html skriven")
    print(f"\n  Öppna pitch_list.html i webbläsaren för att börja ringa! 📞")
    print(f"  Eller importera pitch_list.csv i Excel/Google Sheets.\n")


if __name__ == "__main__":
    generate_pitch_list()
