# Anslagstavla / Forum — Designdokument

## Forskning & Inspiration

### Svenska hästplattformar som undersökts:
- **Bukefalos.se** — Sveriges största hästforum (XenForo). Har Radannonser, marknad (hästar, sadlar, transport, stallplats), fodervärd/medryttare sök/erbjud. Diskussioner blandas med annonser — annonser "drunknar" i trådar. Styrka: stort förtroende, aktiv community.
- **Hästlycka.se** — Bäst i Sverige på medryttare/fodervärd-segmentet. ~170 medryttare-annonser, ~60 foderhäst-annonser. Har "Erbjuds/Sökes"-uppdelning + länsfilter med angränsande län.
- **Hästnet.se** — Nordens största hästmarknadsplats (2M+ besök/mån). 7500+ utrustningsannonser. Professionella annonser med standardiserade fält (ras, ålder, mankhöjd, pris). 149 kr per annons. Strukturerat men ingen community-känsla.
- **Hippson.se** — Nyhets-/kunskapssajt med köp/sälj. Inspirationskälla för innehållsstrategi.

### Internationella förebilder:
- **Chronicle of the Horse** (US) — Forum (Discourse) + klassificerade. Leasing/sharing mycket aktivt. Prenumeration krävs — bevisad synergieffekt med katalog/tidning.
- **Horse & Hound** (UK) — Separerad modell: forums.horseandhound.co.uk (diskussion) + classifieds.horseandhound.co.uk (strukturerade annonser). Postnummer/radie-sök, "Wanted"-notifikationer, upp till 5 foton + 3 video per annons.

### WordPress-plugins som utvärderats:

| Plugin | Typ | Pris | Bäst för |
|--------|-----|------|----------|
| **Classified Listing Pro** | Annonsplattform | $39/år | Strukturerade annonser, geo-sök, custom fields |
| **WPAdverts** | Enkel annonsplattform | Gratis + tillägg | Grundläggande köp/sälj |
| **HivePress** | Katalog + marknadsplats | Gratis + Pro $99 | Allround katalog |
| **wpForo** | Diskussionsforum | Gratis + tillägg | Community-diskussioner (fas 2) |
| **bbPress** | Lätt forum | Gratis | Enkel Q&A |
| **BuddyPress** | Socialt nätverk | Gratis | Användarprofiler (fas 3) |

### Beslut: Inbyggd lösning (fas 1) + eventuell plugin-uppgradering (fas 2)

**Fas 1 (nu):** Anslagstavlan är byggd **direkt i WordPress-temat** som en Custom Post Type (`forum_ad`). Detta ger:
- Noll plugin-kostnad i startfasen
- Designmatchning med resten av sajten
- Full kontroll över UX och data
- Enkel moderering via WordPress admin

**Fas 2 (vid ökad trafik):** Uppgradera till **Classified Listing Pro** ($39/år) för:
- Drag & drop custom fields per kategori
- AJAX radie-sök ("visa inom 30 km")
- Inbyggd chatt mellan annonsörer
- Betalda/featured annonser
- Mer avancerad filtrering

**Fas 3 (vid aktiv community):** Lägg till **wpForo** (gratis) för diskussionsforum + **BuddyPress** för användarprofiler.

---

## Annonskategorier

| Kategori | Slug | Beskrivning | Exempel |
|----------|------|-------------|---------|
| Söker medryttare | medryttare | Hästägare söker medryttare | "Söker medryttare till 14h welsh cob i Täby" |
| Stallhjälp | stallhjalp | Stall söker hjälp / person erbjuder hjälp | "Söker stallhjälp 2 ggr/vecka, Lomma" |
| Hästdelning | hastdelning | Dela häst med annan ryttare | "Erbjuder hästdelning på dressyrhäst, Linköping" |
| Fodervärd | fodervard | Fodervärd sökes/erbjuds | "Fodervärd sökes till islandshäst, Gävle" |
| Hästtransport | transport | Samåkning/transport erbjuds | "Kan ta med häst Stockholm→Malmö 15 april" |
| Utrustning (köp/sälj/byt) | utrustning | Begagnat köp/sälj | "Säljer Prestige sadel 17.5", bra skick" |
| Övrigt | ovrigt | Allt annat hästrelaterat | "Ridkompisar sökes, Örebro" |

---

## Fält per annons

| Fält | Obligatoriskt | Typ | Beskrivning |
|------|---------------|-----|-------------|
| Rubrik | Ja | Text (max 120 tecken) | Kort, tydlig rubrik |
| Kategori | Ja | Select | En av ovanstående |
| Beskrivning | Ja | Textarea | Detaljerad beskrivning |
| Län | Nej | Select (21 län) | Filtrering |
| Ort/Kommun | Nej | Text | Mer specifik plats |
| E-post | Nej | Email | Kontaktadress |
| Telefon | Nej | Tel | Kontaktnummer |
| Bild | Nej | File (max 5MB) | JPG/PNG/WebP |

---

## Regler & Moderering

1. **Inloggningskrav** — Användare måste vara registrerade och inloggade
2. **Moderering** — Alla nya annonser sätts som "Väntande" och granskas av admin
3. **Utgångsdatum** — Annonser utgår automatiskt efter 30 dagar
4. **Cron-jobb** — Daglig check som arkiverar utgångna annonser
5. **Spam-skydd** — WordPress nonce + Akismet (plugin)

---

## UX-mönster (baserat på forskning)

### Vad som fungerar bra (Bukefalos, Hästlycka):
- **Tydliga kategorier** med färgkodning
- **Platsfilter** — län + ort
- **Kort-layout** (card grid) för översikt
- **Tidsvisning** — "3 dagar sedan" ger känsla av aktivitet
- **Kontaktknapp** direkt synlig (ring / maila)

### Vad vi undviker:
- Komplexa registreringsflöden (WordPress standard-registrering räcker)
- Betalning för annonser (gratis = mer aktivitet = mer trafik)
- Omodererat innehåll (allt granskas först)
- Chattfunktion (för komplex, ring/maila räcker)

---

## Implementation (redan byggt)

### WordPress Custom Post Type: `forum_ad`
- Eget arkiv: `/anslagstavla/`
- Enskild annons: `/anslagstavla/rubrik-slug/`

### Taxonomi: `ad_category`
- Alla kategorier ovan förinstalleras vid tema-aktivering

### Templates:
- `archive-forum_ad.php` — Grid med filter (kategori, län, sökning)
- `single-forum_ad.php` — Annonsvy med kontaktkort + relaterade annonser
- `page-ny-annons.php` — Frontend-formulär (AJAX-submit)

### AJAX-endpoints:
- `filter_ads` — Filtrering utan sidladdning
- `submit_ad` — Skicka in ny annons

### Cron:
- `hastsverige_expire_ads` — Daglig check, arkiverar utgångna annonser
