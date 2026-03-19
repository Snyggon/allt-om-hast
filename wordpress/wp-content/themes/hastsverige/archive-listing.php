<?php
/**
 * Archive Listing Template — Alla verksamheter / Kategorivy / Länsvy
 */
get_header();

$current_term = get_queried_object();
$is_category = is_tax('listing_category');
$is_county   = is_tax('county');
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;">

  <!-- Breadcrumbs -->
  <nav class="breadcrumbs" style="margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
    <a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a> &rsaquo;
    <?php if ($is_category || $is_county) : ?>
      <span><?php echo esc_html($current_term->name); ?></span>
    <?php else : ?>
      <span>Alla verksamheter</span>
    <?php endif; ?>
  </nav>

  <div class="section-header">
    <h1><?php
      if ($is_category) {
          echo esc_html($current_term->name);
      } elseif ($is_county) {
          echo 'Hästverksamheter i ' . esc_html($current_term->name);
      } else {
          echo 'Alla hästverksamheter i Sverige';
      }
    ?></h1>
    <?php if ($current_term && $current_term->description) : ?>
      <p><?php echo esc_html($current_term->description); ?></p>
    <?php endif; ?>
  </div>

  <!-- Category filter tabs -->
  <?php if (!$is_category) : ?>
    <div class="category-filter-tabs" style="margin-bottom:1.5rem;">
      <a href="<?php echo esc_url(get_post_type_archive_link('listing')); ?>" class="category-tab <?php echo !$is_category ? 'active' : ''; ?>">Alla</a>
      <?php
      $cats = get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]);
      if (!is_wp_error($cats)) :
          foreach ($cats as $cat) : ?>
              <a href="<?php echo esc_url(get_term_link($cat)); ?>" class="category-tab <?php echo ($is_category && $current_term->term_id === $cat->term_id) ? 'active' : ''; ?>"><?php echo esc_html($cat->name); ?></a>
          <?php endforeach;
      endif;
      ?>
    </div>
  <?php endif; ?>

  <!-- Map for this view -->
  <div class="fullmap-wrap" style="margin-bottom:2rem;border-radius:16px;overflow:hidden;border:1px solid var(--border);">
    <div id="leaflet-map" style="height:400px;"
         data-filter-category="<?php echo $is_category ? esc_attr($current_term->slug) : ''; ?>"
         data-filter-county="<?php echo $is_county ? esc_attr($current_term->slug) : ''; ?>">
    </div>
  </div>

  <!-- Search -->
  <div class="search-controls" style="margin-bottom:1.5rem;">
    <div class="search-input-wrap">
      <span class="search-icon">&#x1F50D;</span>
      <input type="text" id="search-input" placeholder="Sök namn, stad..." aria-label="Sök" autocomplete="off">
    </div>
    <?php if (!$is_county) : ?>
      <select id="county-filter" aria-label="Filtrera på län">
        <option value="">&#x1F4CD; Alla Län</option>
        <?php
        $counties = get_terms(['taxonomy' => 'county', 'hide_empty' => false, 'orderby' => 'name']);
        if (!is_wp_error($counties)) :
            foreach ($counties as $county) : ?>
                <option value="<?php echo esc_attr($county->slug); ?>"><?php echo esc_html($county->name); ?></option>
            <?php endforeach;
        endif;
        ?>
      </select>
    <?php endif; ?>
  </div>

  <p id="result-count" class="result-count"><?php echo esc_html($wp_query->found_posts); ?> verksamheter</p>

  <!-- Listings table -->
  <div class="table-wrapper">
    <table class="directory-table" role="grid">
      <thead>
        <tr>
          <th>Namn</th>
          <?php if (!$is_category) : ?><th>Kategori</th><?php endif; ?>
          <?php if (!$is_county) : ?><th>Län</th><?php endif; ?>
          <th>Stad</th>
          <th>Telefon</th>
          <th>Webbplats</th>
        </tr>
      </thead>
      <tbody>
        <?php if (have_posts()) : ?>
          <?php while (have_posts()) : the_post();
            $lid = get_the_ID();
            $tier = get_post_meta($lid, '_listing_tier', true) ?: 'free';
            $phone = get_post_meta($lid, '_listing_phone', true);
            $website = get_post_meta($lid, '_listing_website', true);
            $city = get_post_meta($lid, '_listing_city', true);
            $l_cats = wp_get_post_terms($lid, 'listing_category', ['fields' => 'names']);
            $l_counties = wp_get_post_terms($lid, 'county', ['fields' => 'names']);
          ?>
            <tr class="<?php echo $tier !== 'free' ? 'tier-' . esc_attr($tier) : ''; ?>">
              <td>
                <a href="<?php the_permalink(); ?>" style="font-weight:600;">
                  <?php if ($tier === 'premium') echo '&#x1F3C6; '; ?>
                  <?php if ($tier === 'featured') echo '&#x2B50; '; ?>
                  <?php the_title(); ?>
                </a>
              </td>
              <?php if (!$is_category) : ?><td><?php echo esc_html(implode(', ', $l_cats)); ?></td><?php endif; ?>
              <?php if (!$is_county) : ?><td><?php echo esc_html(implode(', ', $l_counties)); ?></td><?php endif; ?>
              <td><?php echo esc_html($city); ?></td>
              <td><?php echo $phone ? '<a href="tel:' . esc_attr($phone) . '">' . esc_html($phone) . '</a>' : '—'; ?></td>
              <td><?php echo $website ? '<a href="' . esc_url($website) . '" target="_blank" rel="noopener">Besök &#x2197;</a>' : '—'; ?></td>
            </tr>
          <?php endwhile; ?>
        <?php else : ?>
          <tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-light);">Inga verksamheter hittades.</td></tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>

  <div style="margin-top:1.5rem;">
    <?php the_posts_pagination(['mid_size' => 2]); ?>
  </div>

</div>

<?php get_footer(); ?>
