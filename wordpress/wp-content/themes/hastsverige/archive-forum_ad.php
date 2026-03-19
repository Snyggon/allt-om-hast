<?php
/**
 * Archive Forum Ad Template — Anslagstavla
 */
get_header();

$ad_categories = get_terms(['taxonomy' => 'ad_category', 'hide_empty' => false]);
$counties = get_terms(['taxonomy' => 'county', 'hide_empty' => false, 'orderby' => 'name']);
$current_cat = get_query_var('ad_category') ?: '';
$current_county = get_query_var('county') ?: '';
?>

<div class="container" style="padding: 0 1.5rem;">

  <!-- Forum Hero -->
  <div class="forum-hero" style="margin-top:2rem;">
    <h1>Anslagstavla</h1>
    <p>Sök medryttare, stallhjälp, fodervärd eller hästdelning. Hästmänniskor hjälper hästmänniskor.</p>
    <div style="margin-top:1.5rem;">
      <?php if (is_user_logged_in()) : ?>
        <a href="<?php echo esc_url(home_url('/ny-annons/')); ?>" class="btn btn-primary-inv">&#x2795; Lägg en annons</a>
      <?php else : ?>
        <a href="<?php echo esc_url(wp_login_url(home_url('/ny-annons/'))); ?>" class="btn btn-primary-inv">&#x1F512; Logga in & annonsera</a>
      <?php endif; ?>
    </div>
  </div>

  <!-- Filters -->
  <div class="forum-filters" style="margin-top:2rem;">
    <select id="ad-category-filter">
      <option value="">Alla kategorier</option>
      <?php if (!is_wp_error($ad_categories)) :
          foreach ($ad_categories as $cat) : ?>
              <option value="<?php echo esc_attr($cat->slug); ?>" <?php selected($current_cat, $cat->slug); ?>><?php echo esc_html($cat->name); ?></option>
          <?php endforeach;
      endif; ?>
    </select>
    <select id="ad-county-filter">
      <option value="">Alla län</option>
      <?php if (!is_wp_error($counties)) :
          foreach ($counties as $county) : ?>
              <option value="<?php echo esc_attr($county->slug); ?>" <?php selected($current_county, $county->slug); ?>><?php echo esc_html($county->name); ?></option>
          <?php endforeach;
      endif; ?>
    </select>
    <input type="text" id="ad-search" placeholder="&#x1F50D; Sök bland annonser...">
  </div>

  <!-- Ad Count -->
  <p class="result-count" style="margin:1rem 0;" id="ad-count"><?php echo esc_html($wp_query->found_posts); ?> annonser</p>

  <!-- Ad Grid -->
  <div class="ad-grid" id="ad-grid">
    <?php if (have_posts()) : ?>
      <?php while (have_posts()) : the_post();
        $ad_cats = wp_get_post_terms(get_the_ID(), 'ad_category', ['fields' => 'all']);
        $ad_cat_slug = $ad_cats[0]->slug ?? 'ovrigt';
        $ad_cat_name = $ad_cats[0]->name ?? 'Övrigt';
        $location = get_post_meta(get_the_ID(), '_ad_location', true);
        $expires = get_post_meta(get_the_ID(), '_ad_expires', true);
      ?>
        <div class="ad-card">
          <div class="ad-card-image">
            <?php if (has_post_thumbnail()) :
                the_post_thumbnail('ad-thumb');
            else :
                echo '&#x1F434;';
            endif; ?>
          </div>
          <div class="ad-card-body">
            <span class="ad-card-category ad-cat-<?php echo esc_attr($ad_cat_slug); ?>"><?php echo esc_html($ad_cat_name); ?></span>
            <h3 class="ad-card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
            <p class="ad-card-excerpt"><?php echo wp_trim_words(get_the_content(), 25); ?></p>
            <div class="ad-card-meta">
              <span class="ad-card-location">&#x1F4CD; <?php echo esc_html($location ?: 'Ej angivet'); ?></span>
              <span><?php echo human_time_diff(get_the_time('U'), current_time('timestamp')) . ' sedan'; ?></span>
            </div>
          </div>
        </div>
      <?php endwhile; ?>
    <?php else : ?>
      <div style="grid-column:1/-1;text-align:center;padding:3rem;color:var(--text-light);">
        <p style="font-size:2rem;margin-bottom:1rem;">&#x1F434;</p>
        <p>Inga annonser just nu. Bli först att lägga en!</p>
        <?php if (is_user_logged_in()) : ?>
          <a href="<?php echo esc_url(home_url('/ny-annons/')); ?>" class="btn btn-primary" style="margin-top:1rem;">Lägg en annons</a>
        <?php endif; ?>
      </div>
    <?php endif; ?>
  </div>

  <!-- Pagination -->
  <div style="margin:2rem 0 4rem;">
    <?php the_posts_pagination(['mid_size' => 2]); ?>
  </div>

</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  var catFilter = document.getElementById('ad-category-filter');
  var countyFilter = document.getElementById('ad-county-filter');
  var searchInput = document.getElementById('ad-search');

  function filterAds() {
    var params = new URLSearchParams();
    if (catFilter.value) params.set('ad_category', catFilter.value);
    if (countyFilter.value) params.set('county', countyFilter.value);
    if (searchInput.value) params.set('s', searchInput.value);
    params.set('post_type', 'forum_ad');
    window.location.href = '<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>?' + params.toString();
  }

  catFilter.addEventListener('change', filterAds);
  countyFilter.addEventListener('change', filterAds);

  var searchTimeout;
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(filterAds, 500);
  });
});
</script>

<?php get_footer(); ?>
