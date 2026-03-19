<?php
/**
 * Template Name: Annonsera
 *
 * Landing page for paid business listings.
 * Create a WordPress page with slug "annonsera" and assign this template.
 */
get_header();
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;">

  <!-- Hero -->
  <div style="text-align:center;max-width:700px;margin:0 auto 3rem;">
    <h1 style="font-size:clamp(1.8rem, 4vw, 2.8rem);">Syns mer — nå fler kunder</h1>
    <p style="color:var(--text-mid);font-size:1.1rem;margin-top:0.75rem;">
      Hundratals hästmänniskor söker efter verksamheter som din på HästSverige varje dag.
      Framhäv din listning och stå ut i mängden.
    </p>
  </div>

  <!-- Pricing Cards -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1.5rem;max-width:1000px;margin:0 auto 4rem;">

    <!-- Free -->
    <div style="background:white;border:1px solid var(--border);border-radius:16px;padding:2rem;text-align:center;">
      <h3 style="font-size:1.2rem;margin-bottom:0.5rem;">Gratis</h3>
      <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:700;color:var(--text);margin-bottom:1rem;">0 kr</div>
      <ul style="text-align:left;margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2714; Grundlistning i katalogen</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2714; Namn, adress, telefon</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2714; Visas på kartan</li>
        <li style="padding:0.4rem 0;">&#x2714; Länk till hemsida</li>
      </ul>
      <span class="btn btn-outline-rose" style="width:100%;justify-content:center;opacity:0.6;cursor:default;">Redan inkluderad</span>
    </div>

    <!-- Featured -->
    <div style="background:white;border:2px solid var(--gold);border-radius:16px;padding:2rem;text-align:center;position:relative;">
      <span style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gold);color:white;padding:0.3rem 1rem;border-radius:20px;font-size:0.8rem;font-weight:600;">POPULÄRAST</span>
      <h3 style="font-size:1.2rem;margin-bottom:0.5rem;">&#x2B50; Framhävd</h3>
      <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:700;color:var(--gold);margin-bottom:0.25rem;">199 kr</div>
      <p style="font-size:0.85rem;color:var(--text-mid);margin-bottom:1rem;">/månad</p>
      <ul style="text-align:left;margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2714; Allt i Gratis</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2B50; Gul markering i listan</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2B50; Sorteras före gratislistningar</li>
        <li style="padding:0.4rem 0;">&#x2B50; Framhävd på läns-sidan</li>
      </ul>
      <a href="#kontakt" class="btn btn-primary" style="width:100%;justify-content:center;">Välj Framhävd</a>
    </div>

    <!-- Premium -->
    <div style="background:linear-gradient(135deg, rgba(201,150,60,0.05), rgba(201,150,60,0.1));border:2px solid var(--gold);border-radius:16px;padding:2rem;text-align:center;">
      <h3 style="font-size:1.2rem;margin-bottom:0.5rem;">&#x1F3C6; Premium</h3>
      <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:700;color:var(--rose);margin-bottom:0.25rem;">399 kr</div>
      <p style="font-size:0.85rem;color:var(--text-mid);margin-bottom:1rem;">/månad</p>
      <ul style="text-align:left;margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x2714; Allt i Framhävd</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x1F3C6; Guldram & premium-badge</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x1F3C6; Överst i hela länet</li>
        <li style="padding:0.4rem 0;border-bottom:1px solid var(--border);">&#x1F3C6; Utökad beskrivning & bilder</li>
        <li style="padding:0.4rem 0;">&#x1F3C6; Prioriterad support</li>
      </ul>
      <a href="#kontakt" class="btn btn-green" style="width:100%;justify-content:center;">Välj Premium</a>
    </div>

  </div>

  <!-- Contact Form -->
  <div id="kontakt" style="max-width:600px;margin:0 auto;">
    <div class="section-header centered">
      <h2>Kontakta oss</h2>
      <p>Fyll i formuläret så återkommer vi inom 24 timmar.</p>
    </div>

    <form class="ad-form" action="https://formspree.io/f/DITT-FORMSPREE-ID" method="POST">
      <div class="form-group">
        <label for="company-name">Företagsnamn *</label>
        <input type="text" id="company-name" name="company" required>
      </div>
      <div class="form-group">
        <label for="contact-name">Kontaktperson *</label>
        <input type="text" id="contact-name" name="name" required>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
        <div class="form-group">
          <label for="contact-email">E-post *</label>
          <input type="email" id="contact-email" name="email" required>
        </div>
        <div class="form-group">
          <label for="contact-phone">Telefon</label>
          <input type="tel" id="contact-phone" name="phone">
        </div>
      </div>
      <div class="form-group">
        <label for="package">Önskat paket</label>
        <select id="package" name="package">
          <option value="featured">&#x2B50; Framhävd (199 kr/mån)</option>
          <option value="premium">&#x1F3C6; Premium (399 kr/mån)</option>
          <option value="banner">&#x1F4F0; Läns-banner (999 kr/mån)</option>
        </select>
      </div>
      <div class="form-group">
        <label for="message">Meddelande</label>
        <textarea id="message" name="message" rows="4" placeholder="Berätta gärna om din verksamhet..."></textarea>
      </div>
      <input type="hidden" name="_subject" value="Ny annonsförfrågan — HästSverige">
      <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;">Skicka förfrågan</button>
    </form>
  </div>

</div>

<?php get_footer(); ?>
