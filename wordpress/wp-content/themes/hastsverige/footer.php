  <!-- Footer -->
  <footer>
    <div class="footer-inner">
      <div class="footer-col">
        <div class="footer-logo">&#x1F434; <?php bloginfo('name'); ?></div>
        <p class="footer-tagline"><?php bloginfo('description'); ?></p>
      </div>
      <div class="footer-col">
        <h4>Snabblänkar</h4>
        <ul>
          <li><a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a></li>
          <li><a href="<?php echo esc_url(get_post_type_archive_link('listing')); ?>">Alla verksamheter</a></li>
          <li><a href="<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>">Anslagstavla</a></li>
          <li><a href="<?php echo esc_url(home_url('/blogg/')); ?>">Blogg</a></li>
          <li><a href="<?php echo esc_url(home_url('/annonsera/')); ?>">Annonsera</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Kategorier</h4>
        <ul>
          <?php
          $cats = get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false, 'number' => 6]);
          if (!is_wp_error($cats)) :
              foreach ($cats as $cat) : ?>
                  <li><a href="<?php echo esc_url(get_term_link($cat)); ?>"><?php echo esc_html($cat->name); ?></a></li>
              <?php endforeach;
          endif;
          ?>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Populära Län</h4>
        <ul>
          <?php
          $popular_counties = ['stockholms-lan', 'vastra-gotalands-lan', 'skanes-lan', 'dalarnas-lan'];
          foreach ($popular_counties as $slug) :
              $term = get_term_by('slug', $slug, 'county');
              if ($term) : ?>
                  <li><a href="<?php echo esc_url(get_term_link($term)); ?>"><?php echo esc_html($term->name); ?></a></li>
              <?php endif;
          endforeach;
          ?>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?> &mdash; Sveriges kompletta hästportal.</p>
    </div>
  </footer>

  <?php wp_footer(); ?>
</body>
</html>
