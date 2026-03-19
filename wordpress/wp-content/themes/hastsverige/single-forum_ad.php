<?php
/**
 * Single Forum Ad Template — Enskild annons
 */
get_header();

$id = get_the_ID();
$contact_name  = get_post_meta($id, '_ad_contact_name', true);
$contact_email = get_post_meta($id, '_ad_contact_email', true);
$contact_phone = get_post_meta($id, '_ad_contact_phone', true);
$location      = get_post_meta($id, '_ad_location', true);
$expires       = get_post_meta($id, '_ad_expires', true);

$ad_cats = wp_get_post_terms($id, 'ad_category', ['fields' => 'all']);
$ad_counties = wp_get_post_terms($id, 'county', ['fields' => 'all']);
$ad_cat_slug = $ad_cats[0]->slug ?? 'ovrigt';
$ad_cat_name = $ad_cats[0]->name ?? 'Övrigt';
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;">

  <!-- Breadcrumbs -->
  <nav class="breadcrumbs" style="margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
    <a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a> &rsaquo;
    <a href="<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>">Anslagstavla</a> &rsaquo;
    <span><?php the_title(); ?></span>
  </nav>

  <div style="display:grid;grid-template-columns:2fr 1fr;gap:2rem;align-items:start;">

    <!-- Main content -->
    <div>
      <span class="ad-card-category ad-cat-<?php echo esc_attr($ad_cat_slug); ?>" style="margin-bottom:1rem;"><?php echo esc_html($ad_cat_name); ?></span>

      <h1 style="font-size:2rem;margin:0.5rem 0;"><?php the_title(); ?></h1>

      <div style="display:flex;gap:1rem;color:var(--text-mid);font-size:0.9rem;margin-bottom:1.5rem;flex-wrap:wrap;">
        <span>&#x1F4C5; <?php echo get_the_date(); ?></span>
        <?php if ($location) : ?>
          <span>&#x1F4CD; <?php echo esc_html($location); ?></span>
        <?php endif; ?>
        <?php if ($ad_counties) : ?>
          <span><?php echo esc_html($ad_counties[0]->name); ?></span>
        <?php endif; ?>
        <span>av <?php the_author(); ?></span>
      </div>

      <?php if (has_post_thumbnail()) : ?>
        <div style="border-radius:16px;overflow:hidden;margin-bottom:2rem;">
          <?php the_post_thumbnail('large', ['style' => 'width:100%;height:auto;']); ?>
        </div>
      <?php endif; ?>

      <div class="entry-content" style="font-size:1rem;line-height:1.8;">
        <?php the_content(); ?>
      </div>

      <?php if ($expires) : ?>
        <p style="margin-top:2rem;padding:0.75rem 1rem;background:var(--rose-pale);border-radius:10px;font-size:0.9rem;color:var(--rose-dark);">
          &#x23F3; Denna annons är giltig till <?php echo esc_html(date_i18n('j F Y', strtotime($expires))); ?>
        </p>
      <?php endif; ?>
    </div>

    <!-- Contact sidebar -->
    <aside>
      <div style="background:white;border:1px solid var(--border);border-radius:16px;padding:1.5rem;position:sticky;top:calc(var(--nav-height) + 1rem);">
        <h3 style="font-size:1.1rem;margin-bottom:1rem;">Kontakta annonsören</h3>

        <?php if ($contact_name) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F464; Namn</strong>
            <span><?php echo esc_html($contact_name); ?></span>
          </div>
        <?php endif; ?>

        <?php if ($location) : ?>
          <div style="margin-bottom:1rem;">
            <strong style="font-size:0.85rem;color:var(--text-mid);display:block;">&#x1F4CD; Plats</strong>
            <span><?php echo esc_html($location); ?></span>
            <?php if ($ad_counties) : ?>
              <br><span style="color:var(--text-mid);font-size:0.9rem;"><?php echo esc_html($ad_counties[0]->name); ?></span>
            <?php endif; ?>
          </div>
        <?php endif; ?>

        <?php if ($contact_phone) : ?>
          <a href="tel:<?php echo esc_attr($contact_phone); ?>" class="btn btn-primary" style="width:100%;justify-content:center;margin-bottom:0.5rem;">&#x1F4DE; <?php echo esc_html($contact_phone); ?></a>
        <?php endif; ?>

        <?php if ($contact_email) : ?>
          <a href="mailto:<?php echo esc_attr($contact_email); ?>" class="btn btn-outline-rose" style="width:100%;justify-content:center;">&#x2709; Skicka e-post</a>
        <?php endif; ?>

        <p style="margin-top:1rem;font-size:0.8rem;color:var(--text-light);text-align:center;">Nämn gärna att du hittade annonsen på HästSverige!</p>
      </div>

      <!-- Related ads -->
      <?php
      $related = new WP_Query([
          'post_type'      => 'forum_ad',
          'posts_per_page' => 3,
          'post__not_in'   => [$id],
          'post_status'    => 'publish',
          'tax_query'      => $ad_cats ? [[
              'taxonomy' => 'ad_category',
              'field'    => 'term_id',
              'terms'    => $ad_cats[0]->term_id,
          ]] : [],
      ]);

      if ($related->have_posts()) : ?>
        <div style="margin-top:1.5rem;">
          <h3 style="font-size:1rem;margin-bottom:0.75rem;">Liknande annonser</h3>
          <?php while ($related->have_posts()) : $related->the_post(); ?>
            <a href="<?php the_permalink(); ?>" style="display:block;padding:0.75rem;background:white;border:1px solid var(--border);border-radius:10px;margin-bottom:0.5rem;color:var(--text);text-decoration:none;transition:border-color 0.2s;">
              <strong style="font-size:0.9rem;"><?php the_title(); ?></strong>
              <span style="display:block;font-size:0.8rem;color:var(--text-mid);"><?php echo wp_trim_words(get_the_content(), 10); ?></span>
            </a>
          <?php endwhile; wp_reset_postdata(); ?>
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

<?php get_footer(); ?>
