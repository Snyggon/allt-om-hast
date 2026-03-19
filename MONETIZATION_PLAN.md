# Monetization Plan — Ridskolor-i-Sverige.se
Skapad: mars 2026 | Uppdaterad: mars 2026

## Automatiseringsranking (viktigast insikt)
Användaren vill ha **maximal automatisering**. Rangordning:

| # | Intäkt | Automatisering | Prioritet |
|---|--------|----------------|-----------|
| 1 | Affiliate — hästförsäkring | ✅✅✅ passiv | 🔥 Bygg nu |
| 2 | Google AdSense | ✅✅✅ passiv | Efter trafik |
| 3 | Affiliate — utrustning (Amazon/Adtraction) | ✅✅✅ passiv | Registrera nu |
| 4 | Betalda listningar | ✅✅ semi | Klar i koden |
| 5 | Nyhetsbrev-sponsring | ✅✅ semi | Kräver e-postlista |
| 6 | Jobbannons-tavla | ✅✅ semi | Enkel att bygga |
| 7 | Sommarläger-listningar | ✅✅ säsongsvis | April–juni |
| 8 | Hemsidor åt ridskolor | ❌ aktivt arbete | Säljlista klar |

**Bästa enskilda idén:** En dedikerad `blogg/hastforsakring.html` med affiliatelänkar till Agria, Länsförsäkringar och If. Rankar på Google, hög provision (300–800 kr/pol), helt passiv.

---

## Intäktsström 1: Google AdSense

### Setup (ca 30 min)
1. Gå till google.com/adsense och skapa ett konto med sajtens URL
2. Klistra in AdSense-koden i `<head>` på index.html, region-sidor och blogg-artiklar
3. Vänta 24–48h på godkännande

### Placeringar som ger mest
| Plats | Format | Förväntat |
|-------|--------|-----------|
| Under sökfältet (före tabellen) | Leaderboard 728×90 | Hög CTR |
| Mellan rad 10 och 11 i tabellresultaten | In-feed native | Bäst för mobil |
| Sidebar på artikel-sidor | Rectangle 300×250 | Steady intäkter |
| Under artiklar i bloggen | Leaderboard | Bra intent |

### Förväntade intäkter
- Sverige är premium-marknad (CPM ~$2–4 för hobby/sport-nisch)
- 10 000 sidvisningar/mån → ~$150–400/mån
- 50 000 sidvisningar/mån → ~$750–2 000/mån
- **Börja lågt, stiger med trafik och Core Web Vitals**

### Viktigt
- Aktivera Auto Ads för de bästa placeringarna automatiskt
- Sätt frequency cap för att inte störa UX
- AdSense och affiliate kan kombineras utan problem

---

## Intäktsström 2: Affiliate Marketing

### Program att gå med i NU (prioritetsordning)

#### Prioritet 1: Amazon.se Associates
- **URL:** affiliate-program.amazon.se
- **Provision:** 3–8% beroende på kategori (sports = 4%)
- **Varför:** Enklast att komma igång, produkter finns för allt
- **Sätt upp på 15 min** — bra för utrustningsartikeln direkt
- Produkter att länka: hjälmar, ridbyxor, stövlar, handskar, skyddsvästar

#### Prioritet 2: Adtraction.com
- **URL:** adtraction.com → Registrera som publisher
- **Varför:** Störst nordiskt nätverk, Horze och troligen PS of Sweden finns här
- Sök på "equestrian", "ridning", "häst" i deras marknadsplace
- Förhandla om du kan — direktavtal ger bättre provision

#### Prioritet 3: Horze.se
- **Provision:** 5–10%
- **Kontakt:** Via Adtraction ELLER direkt: affiliate@horze.com
- En av Sveriges/Nordens största hästutrustningsbutiker

#### Prioritet 4: Agria Djurförsäkring
- Hästförsäkring är relevant för alla ridskoleföräldrar
- Kontakta Agria direkt för partnerskap: agria.se/om-agria/kontakt
- Provision per tecknad försäkring (CPA-modell)

#### Prioritet 5: PS of Sweden
- Premium svensk utrustning, via Adrecord.com
- **URL:** adrecord.com/en/join/ps-of-sweden
- Commision ej offentlig, men premiumprodukt = premiumprovisioner

### Affiliate-innehåll (redan implementerat i koden)
- `blogg/vad-ska-du-ha-pa-dig.html` — utrustningsguide med produktblock
- `blogg/rekommenderad-utrustning.html` — dedikerad utrustningssida (planerad)
- Lägg till produktrekommendationer i sidebar på region-sidor

### Hur mycket kan affiliate ge?
- 1 000 besökare/mån på utrustningsartikeln × 2% konversion × 600 kr AOV × 5% = **600 kr/mån**
- Skalar linjärt med trafik. Med SEO-tillväxt: 5 000 bes/mån = **3 000 kr/mån**

---

## Intäktsström 3: Betalda Listningar / Featured Listings

### Produktstruktur

| Paket | Pris | Vad ingår |
|-------|------|-----------|
| **Gratis** | 0 kr | Standard-listning, visas i normal ordning |
| **Framhävd** ⭐ | 199 kr/mån | Gul highlight-rad, "Rekommenderad" badge, visas före gratislistningar |
| **Premium** 🏆 | 399 kr/mån | Guld-badge, överst i listan för sitt län, logo, utökad beskrivning (150 tecken), prioritet på karta |
| **Annons-topp** | 999 kr/mån | Banner-plats överst på läns-sidan (exklusiv per län) |

### Implementering (KLART i koden)
- `is_featured: true` / `tier: "premium"` i data.js
- Guldram och badge i tabellen
- Sorterings-logik: premium → featured → gratis
- 155 ridskolor med telefon men utan hemsida = säljprioritet 1

### Säljprocess
1. Hämta kontaktlista från `contacts.csv` (scrape_emails.py)
2. Ring/maila de 155 med telefon (skript nedan)
3. Erbjud: "Vi visar dig högt upp på söktrafiken för ditt län"
4. Betallösning: Stripe eller Swish Business till att börja

### Säljmanus (email)
```
Hej [NAMN PÅ RIDSKOLA],

Vi driver Ridskolor-i-Sverige.se — katalogen med 480+ ridskolor
som syns på Google för "ridskola [stad/län]".

[RIDSKOLAN] finns redan med i katalogen.
Vill ni synas ÖVERST i er länskategori? Vi erbjuder just nu
en lanseringsrabatt: 199 kr/mån under de 3 första månaderna.

Svarar du på det här mejlet så sätter vi upp det direkt.

Med vänliga hälsningar,
Ridskolor-i-Sverige.se
```

### Intäktspotential
- 10 betalande ridskolor à 199 kr = **1 990 kr/mån**
- 5 premium à 399 kr + 10 framhävda à 199 kr = **3 985 kr/mån**
- 3 annons-toppar à 999 kr = **2 997 kr/mån**
- **Realistiskt år 1: 3 000–8 000 kr/mån**

---

## Intäktsström 4: Hemsidor åt ridskolor

### Affärsmöjligheten
- **262 ridskolor saknar hemsida** (data från vår scraper)
- **155 av dem har telefonnummer** = direkt säljbar lista
- Vi har redan mallen — en ridskolehemsida kan byggas på 2h

### Prissättning

| Produkt | Pris | Marginal |
|---------|------|---------|
| Enkel landningssida (1 sida) | 2 500 kr engång | ~2 000 kr |
| Komplett webbplats (3–5 sidor) | 5 000 kr engång | ~4 000 kr |
| Hosting + underhåll | 195 kr/mån | ~150 kr/mån |
| Hosting + SEO-uppdateringar | 395 kr/mån | ~300 kr/mån |

### Vad ingår i en ridskole-hemsida
- Startsida med presentation + hero-bild
- Lektioner och prislista
- Kontakt + karta
- Mobilanpassad
- Google Analytics
- Automatisk länk till deras listning i vår katalog

### Säljprocess
1. Kör: `python scrape_emails.py` → `contacts.csv`
2. Filtrera: ridskolor med telefon MEN utan hemsida
3. Ring varmt: "Hej, vi visar redan upp er på ridskolor-i-sverige.se..."
4. Erbjud paketet
5. Leverera: Använd vår befintliga region-mall, anpassa med deras info

### Exempel-pitch (telefon)
```
"Hej, jag ringer från Ridskolor-i-Sverige.se. Vi har [RIDSKOLAN]
listad hos oss och ni dyker upp på Google när folk söker ridskola
i [STAD]. Jag ringde för att fråga om ni är intresserade av att
ha en egen hemsida — vi bygger enkla och snygga ridskole-hemsidor
för 2 500 kronor. Kan jag skicka ett par exempel?"
```

### Intäktspotential
- **Pessimistiskt:** 5% konversion av 155 = 8 hemsidor × 2 500 = **20 000 kr**
- **Realistiskt:** 10% = 15 hemsidor × 3 500 snitt = **52 500 kr**
- **Recurring:** 15 kunder × 195 kr/mån = **2 925 kr/mån passivt**

---

---

## Intäktsström 5: Hästförsäkring-jämförelse (NYY — HÖGST PRIORITET)

**Status:** Ej byggd — `blogg/hastforsakring.html` planerad
**Automatisering:** ✅✅✅ Helt passiv
**Varför detta är den bästa idén:**
- Hög provision per konversion: 300–800 kr/tecknad försäkring
- Rankar bra på Google: "hästförsäkring jämförelse", "bästa hästförsäkringen 2026"
- Återkommande: försäkring förnyas varje år (möjlig provision vid förnyelse)
- Naturlig publik: alla ridskoleföräldrar behöver hästförsäkring
- Noll löpande arbete efter publicering

**Bolag att kontakta:**
- Agria Djurförsäkring — agria.se/om-agria/kontakt (störst marknadsandel)
- Länsförsäkringar — kontakta via länsförsäkringar.se
- If Skadeförsäkring — if.se/foretag/kontakta-oss

---

## Intäktsström 6: Nyhetsbrev + sponsorskap

**Status:** Ej byggt
**Automatisering:** ✅✅ Semi-passiv
**Setup:** Lägg in e-post-formulär på startsidan ("Bevaka ridskolor i ditt län"). Mailchimp gratis upp till 500 prenumeranter.
**Intäkt:** Sälj 1–2 sponsorplatser per utskick till utrustningsbolag. 2 000 prenumeranter → 2 000–5 000 kr/utskick.

---

## Intäktsström 7: Jobbannons-tavla för ridlärare

**Status:** Ej byggt — enkel `jobb.html` räcker
**Automatisering:** ✅✅ Semi-passiv (annonser läggs upp av ridskolor)
**Prissättning:** 299–499 kr per annons i 30 dagar
**Varför:** Ingen annan nischad svensk sajt för detta. Ridskolor söker ständigt ridlärare och stallpersonal.

---

## Intäktsström 8: Sommarläger-listningar

**Status:** Ej byggt
**Automatisering:** ✅✅ Säsongsvis passiv
**Timing:** Sälj april–juni (föräldrar söker sommarridläger åt barn)
**Prissättning:** 499 kr per lägerannons under säsongen

---

## Sammanfattning — Realistisk prognos år 1 (uppdaterad)

| Intäktsström | Automatisering | Lågt | Högt |
|-------------|----------------|------|------|
| AdSense | ✅✅✅ | 6 000 kr | 24 000 kr |
| Affiliate (utrustning) | ✅✅✅ | 12 000 kr | 36 000 kr |
| Affiliate (försäkring) | ✅✅✅ | 15 000 kr | 60 000 kr |
| Betalda listningar | ✅✅ | 24 000 kr | 72 000 kr |
| Nyhetsbrev-sponsring | ✅✅ | 0 kr | 30 000 kr |
| Jobbannons-tavla | ✅✅ | 5 000 kr | 20 000 kr |
| Hemsidebygge | ❌ | 20 000 kr | 60 000 kr |
| **TOTALT** | | **~82 000 kr** | **~302 000 kr** |

---

## Prioriteringsordning (uppdaterad för maximal automation)

### Gör nu (passivt, en gång):
1. 🔥 **Bygg `blogg/hastforsakring.html`** — hästförsäkring-jämförelse med CTA till Agria m.fl.
2. 📝 **Registrera Amazon Associates** → byt `DITT-AFFILIATE-ID` i `vad-ska-du-ha-pa-dig.html`
3. 📝 **Registrera Adtraction.com** → ansök om Horze och PS of Sweden
4. 📞 **Kontakta Agria** för CPA-avtal (agria.se/om-agria/kontakt)
5. 🔗 **Koppla Formspree** till annonsera.html (gratis, ersätt `DITT-FORMSPREE-ID`)

### Gör när sajten har trafik:
6. 📊 **Ansök om AdSense** (google.com/adsense)
7. 📧 **Lägg till nyhetsbrev-formulär** (Mailchimp, gratis)

### Gör om du vill aktivt:
8. 💳 **Sätt upp Stripe/Swish Business** för betalda listningar
9. 📞 **Använd pitch_list.html** för att kontakta 155 ridskolor utan hemsida

---
*Uppdaterad mars 2026. Uppdatera igen när intäkter och konverteringsdata finns.*
