<?php
/**
 * Single Listing Template — Verksamhetssida
 */
get_header();

$id       = get_the_ID();
$phone    = get_post_meta($id, '_listing_phone', true);
$email    = get_post_meta($id, '_listing_email', true);
$website  = get_post_meta($id, '_listing_website', true);
$street   = get_post_meta($id, '_listing_street', true);
$city     = get_post_meta($id, '_listing_city', true);
$hours    = get_post_meta($id, '_listing_hours', true);
$lat      = get_post_meta($id, '_listing_lat', true);
$lng      = get_post_meta($id, '_listing_lng', true);
$tier     = get_post_meta($id, '_listing_tier', true) ?: 'free';

$categories = wp_get_post_terms($id, 'listing_category', ['fields' => 'all']);
$counties   = wp_get_post_terms($id, 'county', ['fields' => 'all']);
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;">

  <!-- Breadcrumbs -->
  <nav class="breadcrumbs" style="margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
    <a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a> &rsaquo;
    <?php if ($categories) : ?>
      <a href="<?php echo esc_url(get_term_link($categories[0])); ?>"><?php echo esc_html($categories[0]->name); ?></a> &rsaquo;
    <?php endif; ?>
    <span><?php the_title(); ?></span>
  </nav>

  <div style="display:grid;grid-template-columns:2fr 1fr;gap:2rem;align-items:start;">

    <!-- Main content -->
    <div>
      <?php if ($tier === 'premium') : ?>
        <span style="display:inline-block;background:var(--gold);color:white;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin-bottom:1rem;">&#x1F3C6; Premium</span>
      <?php elseif ($tier === 'featured') : ?>
        <span style="display:inline-block;background:var(--gold-light);color:var(--text);padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin-bottom:1rem;">&#x2B50; Framhävd</span>
      <?php endif; ?>

      <h1 style="font-size:2rem;margin-bottom:0.5rem;"><?php the_title(); ?></h1>

      <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <?php foreach ($categories as $cat) : ?>
          <a href="<?php echo esc_url(get_term_link($cat)); ?>" class="category-tab active" style="cursor:pointer;"><?php echo esc_html($cat->name); ?></a>
        <?php endforeach; ?>
        <?php foreach ($counties as $county) : ?>
          <a href="<?php echo esc_url(get_term_link($county)); ?>" class="category-tab"><?php echo esc_html($county->name); ?></a>
        <?php endforeach; ?>
      </div>

      <?php if (has_post_thumbnail()) : ?>
        <div style="border-radius:16px;overflow:hidden;margin-bottom:2rem;">
          <?php the_post_thumbnail('listing-hero', ['style' => 'width:100%;height:auto;']); ?>
        </div>
      <?php endif; ?>

      <div class="entry-content" style="font-size:1rem;line-height:1.8;">
        <?php the_content(); ?>
      </div>
    </div>

    <!-- Sidebar / Contact card -->
    <aside>
      <div style="background:white;border:1px solid var(--border);border-radius:16px;padding:1.5rem;position:sticky;top:calc(var(--nav-height) + 1rem);">
        <h3 style="font-size:1.1rem;margin-bottom:1rem;">Kontaktinformation</h3>

        <?php if ($street || $city) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F4CD; Adress</strong>
            <span><?php echo esc_html(trim("$street, $city", ', ')); ?></span>
            <?php if ($counties) : ?>
              <br><span style="color:var(--text-mid);font-size:0.9rem;"><?php echo esc_html($counties[0]->name); ?></span>
            <?php endif; ?>
          </div>
        <?php endif; ?>

        <?php if ($phone) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F4DE; Telefon</strong>
            <a href="tel:<?php echo esc_attr($phone); ?>"><?php echo esc_html($phone); ?></a>
          </div>
        <?php endif; ?>

        <?php if ($email) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x2709; E-post</strong>
            <a href="mailto:<?php echo esc_attr($email); ?>"><?php echo esc_html($email); ?></a>
          </div>
        <?php endif; ?>

        <?php if ($website) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F310; Hemsida</strong>
            <a href="<?php echo esc_url($website); ?>" target="_blank" rel="noopener"><?php echo esc_html(preg_replace('#^https?://(www\.)?#', '', $website)); ?></a>
          </div>
        <?php endif; ?>

        <?php if ($hours) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F552; Öppettider</strong>
            <span><?php echo esc_html($hours); ?></span>
          </div>
        <?php endif; ?>

        <?php if ($phone) : ?>
          <a href="tel:<?php echo esc_attr($phone); ?>" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:0.5rem;">&#x1F4DE; Ring nu</a>
        <?php endif; ?>

        <?php if ($website) : ?>
          <a href="<?php echo esc_url($website); ?>" target="_blank" rel="noopener" class="btn btn-outline-rose" style="width:100%;justify-content:center;margin-top:0.5rem;">&#x1F310; Besök hemsida</a>
        <?php endif; ?>
      </div>

      <?php if ($lat && $lng) : ?>
        <div style="margin-top:1.5rem;border-radius:16px;overflow:hidden;border:1px solid var(--border);">
          <div id="single-map" style="height:250px;" data-lat="<?php echo esc_attr($lat); ?>" data-lng="<?php echo esc_attr($lng); ?>" data-name="<?php echo esc_attr(get_the_title()); ?>"></div>
        </div>
      <?php endif; ?>
    </aside>

  </div>
</div>

<style>
@media (max-width: 768px) {
  .container > div[style*="grid-template-columns"] {
    grid-template-columns: 1fr !important;
  }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
  var mapEl = document.getElementById('single-map');
  if (mapEl && typeof L !== 'undefined') {
    var lat = parseFloat(mapEl.dataset.lat);
    var lng = parseFloat(mapEl.dataset.lng);
    var name = mapEl.dataset.name;
    if (lat && lng) {
      var map = L.map('single-map').setView([lat, lng], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
      }).addTo(map);
      L.marker([lat, lng]).addTo(map).bindPopup('<strong>' + name + '</strong>').openPopup();
    }
  }
});
</script>

<?php get_footer(); ?>
