<?php
/**
 * Front Page Template — HästSverige Startsida
 */
get_header();

// Count listings per category
$categories = get_terms([
    'taxonomy'   => 'listing_category',
    'hide_empty' => false,
]);
$total_listings = wp_count_posts('listing')->publish ?? 0;
$total_counties = 21;

// Category icons map
$cat_icons = [
    'ridskolor'     => '&#x1F3C7;',
    'turridning'    => '&#x1F40E;',
    'hastkalas'     => '&#x1F382;',
    'ridlager'      => '&#x26FA;',
    'hastpensionat' => '&#x1F3E0;',
    'hovslagare'    => '&#x1F528;',
];
?>

  <!-- Hero -->
  <section class="hero">
    <div class="hero-bg-pattern"></div>
    <div class="container">
      <p class="hero-eyebrow">Sveriges kompletta hästportal</p>
      <h1>Hitta Hästverksamheter<br><em>i hela Sverige</em></h1>
      <div class="hero-divider"></div>
      <p class="hero-sub">Ridskolor, turridning, hästkalas, ridläger, hästpensionat och hovslagare — allt samlat på ett ställe. Sök, jämför och kontakta direkt.</p>
      <div class="hero-stats">
        <div class="stat-card">
          <span class="stat-num"><?php echo esc_html(number_format_i18n($total_listings)); ?></span>
          <span class="stat-lbl">&#x1F3C7; Verksamheter</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">6</span>
          <span class="stat-lbl">&#x1F4C2; Kategorier</span>
        </div>
        <div class="stat-card">
          <span class="stat-num"><?php echo esc_html($total_counties); ?></span>
          <span class="stat-lbl">&#x1F4CD; Län</span>
        </div>
      </div>
      <div class="hero-buttons">
        <a href="#search" class="btn btn-primary-inv">&#x1F50D; Sök Verksamhet</a>
        <a href="#kategorier" class="btn btn-outline-inv">Visa Kategorier &#x2192;</a>
      </div>
    </div>
    <div class="hero-wave">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 70" preserveAspectRatio="none">
        <path d="M0,35 C240,70 480,0 720,35 C960,70 1200,0 1440,35 L1440,70 L0,70 Z" fill="#FDF7F2"/>
      </svg>
    </div>
  </section>

  <!-- Trust Section -->
  <section class="trust-section">
    <div class="container">
      <div class="trust-intro">
        <span class="trust-eyebrow">Samlingsplatsen för hästsverige</span>
        <h2>Allt om hästar — på ett ställe</h2>
        <p class="trust-lead">Vi har kartlagt ridskolor, turridning, hästkalas, ridläger, hästpensionat och hovslagare i hela Sverige. Oavsett vad du söker inom hästvärlden hittar du det här.</p>
      </div>

      <div class="trust-pillars">
        <div class="trust-pillar">
          <div class="trust-pillar-icon">&#x1F5C2;</div>
          <h3>Komplett katalog</h3>
          <p>Alla kända hästverksamheter samlade på en plats. Uppdaterad löpande med adresser, telefonnummer och webbplatser.</p>
        </div>
        <div class="trust-pillar">
          <div class="trust-pillar-icon">&#x1F4CD;</div>
          <h3>Hitta lokalt</h3>
          <p>Sök på stad, filtrera på län och kategori, eller använd kartan. Vi visar hästverksamheter nära dig.</p>
        </div>
        <div class="trust-pillar">
          <div class="trust-pillar-icon">&#x1F4E2;</div>
          <h3>Community</h3>
          <p>Sök medryttare, stallhjälp eller fodervärd via vår anslagstavla. Hästmänniskor hjälper hästmänniskor.</p>
        </div>
        <div class="trust-pillar">
          <div class="trust-pillar-icon">&#x1F3C6;</div>
          <h3>Från nybörjare till proffs</h3>
          <p>Alltifrån ponnyridning för de allra minsta till avancerade verksamheter för erfarna hästmänniskor.</p>
        </div>
      </div>

      <div class="trust-stats-bar">
        <div class="trust-stat-item">
          <strong>355 000</strong>
          <span>hästar i Sverige</span>
        </div>
        <div class="trust-stat-divider"></div>
        <div class="trust-stat-item">
          <strong><?php echo esc_html(number_format_i18n($total_listings)); ?>+</strong>
          <span>verksamheter kartlagda</span>
        </div>
        <div class="trust-stat-divider"></div>
        <div class="trust-stat-item">
          <strong>140 000</strong>
          <span>SvRF-medlemmar</span>
        </div>
        <div class="trust-stat-divider"></div>
        <div class="trust-stat-item">
          <strong>93%</strong>
          <span>av ryttarna är kvinnor</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Categories Section -->
  <section id="kategorier" class="categories-section">
    <div class="container">
      <div class="section-header centered">
        <h2>Utforska Kategorier</h2>
        <p>Välj en kategori för att hitta rätt hästverksamhet.</p>
      </div>
      <div class="category-cards">
        <?php
        if (!is_wp_error($categories)) :
            foreach ($categories as $cat) :
                $icon = $cat_icons[$cat->slug] ?? '&#x1F434;';
                $count = $cat->count;
        ?>
          <a href="<?php echo esc_url(get_term_link($cat)); ?>" class="category-card">
            <div class="category-card-icon"><?php echo $icon; ?></div>
            <h3><?php echo esc_html($cat->name); ?></h3>
            <span class="category-count"><?php echo esc_html($count); ?> verksamheter</span>
            <span class="category-arrow">&#x2192;</span>
          </a>
        <?php
            endforeach;
        endif;
        ?>
      </div>
    </div>
  </section>

  <!-- Full-width Leaflet Map -->
  <section class="fullmap-section">
    <div class="container">
      <div class="section-header centered">
        <h2>Hästverksamheter på Kartan</h2>
        <p>Klicka på en nål för att se verksamheten — zooma och panorera fritt.</p>
      </div>
    </div>
    <div class="fullmap-wrap" style="max-width:var(--container);margin:1.5rem auto 0;">
      <div id="leaflet-map"></div>
    </div>
    <div id="map-tooltip" role="tooltip"></div>
  </section>

  <!-- Search & Directory Table -->
  <div class="container">
    <section id="search" class="search-section">
      <div class="section-header centered">
        <h2>Sök bland alla verksamheter</h2>
        <p>Filtrera på kategori, län eller sök fritt.</p>
      </div>

      <!-- Category filter tabs -->
      <div class="category-filter-tabs">
        <button class="category-tab active" data-category="">Alla</button>
        <?php
        if (!is_wp_error($categories)) :
            foreach ($categories as $cat) : ?>
                <button class="category-tab" data-category="<?php echo esc_attr($cat->slug); ?>"><?php echo esc_html($cat->name); ?></button>
            <?php endforeach;
        endif;
        ?>
      </div>

      <div class="search-controls">
        <div class="search-input-wrap">
          <span class="search-icon">&#x1F50D;</span>
          <input type="text" id="search-input" placeholder="Sök namn, stad, tjänst..." aria-label="Sök verksamhet" autocomplete="off">
        </div>
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
      </div>

      <p id="result-count" class="result-count"></p>

      <div class="table-wrapper">
        <table class="directory-table" role="grid">
          <thead>
            <tr>
              <th>Namn</th>
              <th>Kategori</th>
              <th>Län</th>
              <th>Stad</th>
              <th>Telefon</th>
              <th>Webbplats</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <tr>
              <td colspan="6" style="text-align:center;padding:3rem;color:#9E8090;">Laddar verksamheter... &#x1F434;</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div id="pagination"></div>
    </section>
  </div>

  <!-- Forum Teaser -->
  <section class="forum-section" style="background:white;">
    <div class="container">
      <div class="forum-hero">
        <h2>Anslagstavla</h2>
        <p>Sök medryttare, stallhjälp, fodervärd eller hästdelning. Hästmänniskor hjälper hästmänniskor.</p>
        <div style="margin-top:1.5rem;">
          <a href="<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>" class="btn btn-primary-inv">Se alla annonser</a>
          <?php if (is_user_logged_in()) : ?>
            <a href="<?php echo esc_url(home_url('/ny-annons/')); ?>" class="btn btn-outline-inv">Lägg en annons</a>
          <?php else : ?>
            <a href="<?php echo esc_url(wp_login_url(home_url('/ny-annons/'))); ?>" class="btn btn-outline-inv">Logga in & annonsera</a>
          <?php endif; ?>
        </div>
      </div>

      <!-- Latest ads preview -->
      <?php
      $latest_ads = new WP_Query([
          'post_type'      => 'forum_ad',
          'posts_per_page' => 3,
          'post_status'    => 'publish',
          'orderby'        => 'date',
          'order'          => 'DESC',
      ]);

      if ($latest_ads->have_posts()) : ?>
        <div class="ad-grid" style="margin-top:2rem;">
          <?php while ($latest_ads->have_posts()) : $latest_ads->the_post();
            $ad_cats = wp_get_post_terms(get_the_ID(), 'ad_category', ['fields' => 'all']);
            $ad_cat_slug = $ad_cats[0]->slug ?? 'ovrigt';
            $ad_cat_name = $ad_cats[0]->name ?? 'Övrigt';
            $location = get_post_meta(get_the_ID(), '_ad_location', true);
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
          <?php endwhile; wp_reset_postdata(); ?>
        </div>
      <?php endif; ?>
    </div>
  </section>

  <!-- County Cards -->
  <section id="regioner" class="regions-section">
    <div class="container">
      <div class="section-header centered">
        <h2>Verksamheter per Län</h2>
        <p>Välj ditt län för en komplett lista med hästverksamheter, karta och kontaktinfo.</p>
      </div>
      <div class="county-cards">
        <?php
        $county_icons = ['&#x1F40E;', '&#x1F434;', '&#x1F3C7;', '&#x1F984;'];
        $counties_list = get_terms(['taxonomy' => 'county', 'hide_empty' => false, 'orderby' => 'name']);
        $i = 0;
        if (!is_wp_error($counties_list)) :
            foreach ($counties_list as $county) :
                $icon = $county_icons[$i % 4];
                $i++;
        ?>
          <a href="<?php echo esc_url(get_term_link($county)); ?>" class="county-card">
            <div class="county-card-icon"><?php echo $icon; ?></div>
            <h3><?php echo esc_html($county->name); ?></h3>
            <p><?php echo esc_html($county->count); ?> verksamheter</p>
            <span class="county-card-arrow">&#x2192;</span>
          </a>
        <?php
            endforeach;
        endif;
        ?>
      </div>
    </div>
  </section>

  <!-- Blog Teaser -->
  <section class="blog-teaser">
    <div class="container">
      <div class="section-header centered">
        <h2>Tips &amp; Råd om Hästar</h2>
        <p>Från nybörjare till erfaren ryttare — vi har guider för alla.</p>
      </div>
      <div class="blog-teaser-grid">
        <?php
        $blog_posts = new WP_Query([
            'post_type'      => 'post',
            'posts_per_page' => 4,
            'orderby'        => 'date',
            'order'          => 'DESC',
        ]);
        while ($blog_posts->have_posts()) : $blog_posts->the_post(); ?>
          <a href="<?php the_permalink(); ?>" class="blog-mini-card">
            <?php if (has_post_thumbnail()) : ?>
              <?php the_post_thumbnail('listing-card'); ?>
            <?php endif; ?>
            <h3><?php the_title(); ?></h3>
            <p><?php echo wp_trim_words(get_the_excerpt(), 15); ?></p>
          </a>
        <?php endwhile; wp_reset_postdata(); ?>
      </div>
      <div style="text-align:center;margin-top:2rem">
        <a href="<?php echo esc_url(home_url('/blogg/')); ?>" class="btn btn-outline-rose">Se alla artiklar &#x2192;</a>
      </div>
    </div>
  </section>

<?php get_footer(); ?>
