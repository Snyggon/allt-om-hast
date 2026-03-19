# HästSverige — WordPress Uppsättningsguide

## 1. Skaffa WordPress-hosting

Rekommenderade svenska hostingleverantörer:

| Leverantör | Pris/mån | Fördelar |
|-----------|----------|----------|
| **Loopia** | ~79 kr | Svensk support, .se-domän ingår |
| **one.com** | ~49 kr | Billigast, enkel setup |
| **SiteGround** | ~99 kr | Bäst prestanda, bra support |

### Steg:
1. Registrera konto hos valfri leverantör
2. Registrera domännamn (t.ex. hastsverige.se)
3. Installera WordPress (de flesta har 1-klick-installation)

---

## 2. Installera temat

1. Ladda upp mappen `wordpress/wp-content/themes/hastsverige/` till din WordPress-installation
2. Gå till **Utseende > Teman** i WordPress admin
3. Aktivera "HästSverige"
4. Temat skapar automatiskt alla kategorier, län och annonskategorier

---

## 3. Importera data

### Alternativ A: WordPress Import (enklast)

1. Kör `python import_to_wordpress.py` lokalt — skapar `wordpress_import.xml`
2. Gå till **Verktyg > Importera > WordPress** i WP admin
3. Ladda upp `wordpress_import.xml`
4. All data importeras som "Verksamhet"-inlägg med rätt kategorier och län

### Alternativ B: Admin-import

1. Gå till **Inställningar > HästSverige Import** i WP admin
2. Välj JSON-fil och kategori
3. Klicka "Importera"

---

## 4. Skapa nödvändiga sidor

Skapa dessa WordPress-sidor (Sidor > Lägg till ny):

| Sidnamn | Slug | Mall |
|---------|------|------|
| Startsida | (sätts som framsida) | — (använder front-page.php automatiskt) |
| Ny Annons | ny-annons | "Ny Annons" |
| Annonsera | annonsera | "Annonsera" |
| Blogg | blogg | Standard |

### Ställ in startsida:
1. Gå till **Inställningar > Läsning**
2. Välj "En statisk sida"
3. Startsida: (din startsida)
4. Inläggssida: Blogg

---

## 5. Konfigurera Formspree (kontaktformulär)

1. Registrera på [formspree.io](https://formspree.io)
2. Skapa ett formulär
3. Ersätt `DITT-FORMSPREE-ID` i `page-annonsera.php` med ditt riktiga ID

---

## 6. SEO & Analytics

### Yoast SEO:
1. Installera plugin **Yoast SEO** (gratis)
2. Kör setup-guiden
3. Sätt site title till "HästSverige — Sveriges Kompletta Hästportal"

### Google Analytics:
1. Installera plugin **GA Google Analytics**
2. Klistra in ditt GA4 Measurement ID (G-XXXXXXXXXX)

### Google Search Console:
1. Verifiera sajten på [search.google.com/search-console](https://search.google.com/search-console)
2. Skicka in sitemap: `https://hastsverige.se/sitemap.xml` (genereras av Yoast)

---

## 7. Permalänk-inställningar

1. Gå till **Inställningar > Permalänkar**
2. Välj "Inläggsnamn" (`/%postname%/`)
3. Spara — detta aktiverar alla custom URL:er

---

## 8. Rekommenderade plugins

| Plugin | Syfte | Pris |
|--------|-------|------|
| **Yoast SEO** | SEO-optimering | Gratis |
| **WP Super Cache** | Snabbare sidor | Gratis |
| **Wordfence** | Säkerhet | Gratis |
| **Akismet** | Spamskydd (forum) | Gratis |
| **WPForms Lite** | Kontaktformulär | Gratis |
| **Redirection** | Omdirigeringar | Gratis |

---

## 9. Anslagstavlan (Forum)

Anslagstavlan är inbyggd i temat:
- Användare registrerar sig (WordPress standard)
- Inloggade kan posta annonser via `/ny-annons/`
- Annonser modereras innan publicering (status: "Väntande")
- Annonser utgår automatiskt efter 30 dagar

### Annonskategorier (förinstallerade):
- Söker medryttare
- Stallhjälp
- Hästdelning
- Fodervärd
- Hästtransport
- Utrustning (köp/sälj/byt)
- Övrigt

---

## 10. Betalda listningar

Systemet stödjer tre tier-nivåer:
- **free** — Standard (visas normalt)
- **featured** — Gul markering, sorteras före gratis
- **premium** — Guldram, överst i länet

Ändra en verksamhets tier:
1. Gå till **Verksamheter** i admin
2. Redigera verksamheten
3. Ändra "Nivå" i rutan "Verksamhetsdetaljer"

---

## Filstruktur

```
wordpress/wp-content/themes/hastsverige/
├── style.css              # Tema-CSS (design tokens, layout, komponenter)
├── functions.php          # Custom post types, taxonomier, AJAX, cron
├── header.php             # Sidhuvud med navigation
├── footer.php             # Sidfot
├── front-page.php         # Startsida (hero, kategorier, karta, sök, forum-teaser)
├── index.php              # Fallback-template
├── single.php             # Blogg-inlägg
├── single-listing.php     # Enskild verksamhet (kontaktkort, karta)
├── single-forum_ad.php    # Enskild annons
├── archive-listing.php    # Alla verksamheter / kategorivy / länsvy
├── archive-forum_ad.php   # Anslagstavla (alla annonser)
├── taxonomy-listing_category.php  # Kategori-arkiv
├── taxonomy-county.php    # Läns-arkiv
├── page.php               # Standard-sida
├── page-ny-annons.php     # Formulär: lägg annons
├── page-annonsera.php     # Betalda listningar (prissida)
├── 404.php                # 404-sida
├── inc/
│   └── import-json.php    # JSON-import via admin
└── js/
    └── main.js            # Karta, sök, filter, pagination
```
