<?php
/**
 * Template Name: Ny Annons
 *
 * Frontend form for submitting forum ads.
 * Create a WordPress page with slug "ny-annons" and assign this template.
 */
get_header();

// Redirect if not logged in
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

$ad_categories = get_terms(['taxonomy' => 'ad_category', 'hide_empty' => false]);
$counties = get_terms(['taxonomy' => 'county', 'hide_empty' => false, 'orderby' => 'name']);
$user = wp_get_current_user();
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;">

  <!-- Breadcrumbs -->
  <nav class="breadcrumbs" style="margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
    <a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a> &rsaquo;
    <a href="<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>">Anslagstavla</a> &rsaquo;
    <span>Ny annons</span>
  </nav>

  <div class="section-header centered">
    <h1>Lägg en annons</h1>
    <p>Sök medryttare, stallhjälp, fodervärd eller erbjud dina tjänster. Annonsen granskas innan publicering och är giltig i 30 dagar.</p>
  </div>

  <form class="ad-form" id="new-ad-form" enctype="multipart/form-data">
    <?php wp_nonce_field('hastsverige_nonce', 'nonce'); ?>

    <div class="form-group">
      <label for="ad-title">Rubrik *</label>
      <input type="text" id="ad-title" name="title" required placeholder="T.ex. &quot;Söker medryttare till sportponny i Uppsala&quot;" maxlength="120">
    </div>

    <div class="form-group">
      <label for="ad-category">Kategori *</label>
      <select id="ad-category" name="ad_category" required>
        <option value="">Välj kategori...</option>
        <?php if (!is_wp_error($ad_categories)) :
            foreach ($ad_categories as $cat) : ?>
                <option value="<?php echo esc_attr($cat->slug); ?>"><?php echo esc_html($cat->name); ?></option>
            <?php endforeach;
        endif; ?>
      </select>
    </div>

    <div class="form-group">
      <label for="ad-content">Beskrivning *</label>
      <textarea id="ad-content" name="content" required placeholder="Beskriv vad du söker eller erbjuder. Ju mer detaljer desto bättre!" rows="6"></textarea>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div class="form-group">
        <label for="ad-county">Län</label>
        <select id="ad-county" name="county">
          <option value="">Välj län...</option>
          <?php if (!is_wp_error($counties)) :
              foreach ($counties as $county) : ?>
                  <option value="<?php echo esc_attr($county->slug); ?>"><?php echo esc_html($county->name); ?></option>
              <?php endforeach;
          endif; ?>
        </select>
      </div>
      <div class="form-group">
        <label for="ad-location">Ort / Kommun</label>
        <input type="text" id="ad-location" name="location" placeholder="T.ex. Uppsala, Sigtuna">
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div class="form-group">
        <label for="ad-email">E-post (kontakt)</label>
        <input type="email" id="ad-email" name="email" value="<?php echo esc_attr($user->user_email); ?>" placeholder="din@email.se">
      </div>
      <div class="form-group">
        <label for="ad-phone">Telefon (valfritt)</label>
        <input type="tel" id="ad-phone" name="phone" placeholder="070-XXX XX XX">
      </div>
    </div>

    <div class="form-group">
      <label for="ad-image">Bild (valfritt)</label>
      <input type="file" id="ad-image" name="ad_image" accept="image/*" style="padding:0.5rem;">
      <p style="font-size:0.8rem;color:var(--text-light);margin-top:0.3rem;">Max 5 MB. JPG, PNG eller WebP.</p>
    </div>

    <div id="ad-form-message" style="display:none;padding:1rem;border-radius:10px;margin-bottom:1rem;"></div>

    <button type="submit" class="btn btn-green" style="width:100%;justify-content:center;font-size:1.05rem;padding:1rem;" id="submit-ad-btn">
      &#x1F4E8; Skicka annons
    </button>

    <p style="text-align:center;margin-top:1rem;font-size:0.85rem;color:var(--text-light);">
      Annonsen granskas av oss innan publicering. Du får e-post när den är godkänd.
    </p>
  </form>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  var form = document.getElementById('new-ad-form');
  var btn = document.getElementById('submit-ad-btn');
  var msg = document.getElementById('ad-form-message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    btn.disabled = true;
    btn.textContent = 'Skickar...';

    var formData = new FormData(form);
    formData.append('action', 'submit_ad');

    fetch(hastsverigeData.ajaxUrl, {
      method: 'POST',
      body: formData,
      credentials: 'same-origin'
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      if (data.success) {
        msg.style.display = 'block';
        msg.style.background = 'var(--green-light)';
        msg.style.color = 'var(--green-dark)';
        msg.textContent = data.data.message;
        form.reset();
      } else {
        msg.style.display = 'block';
        msg.style.background = 'var(--rose-pale)';
        msg.style.color = 'var(--rose-dark)';
        msg.textContent = data.data.message || 'Något gick fel. Försök igen.';
      }
    })
    .catch(function() {
      msg.style.display = 'block';
      msg.style.background = 'var(--rose-pale)';
      msg.style.color = 'var(--rose-dark)';
      msg.textContent = 'Nätverksfel. Kontrollera din anslutning.';
    })
    .finally(function() {
      btn.disabled = false;
      btn.innerHTML = '&#x1F4E8; Skicka annons';
    });
  });
});
</script>

<?php get_footer(); ?>
