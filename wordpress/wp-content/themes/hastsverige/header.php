<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

  <!-- Navigation -->
  <nav id="main-nav">
    <div class="nav-inner">
      <a href="<?php echo esc_url(home_url('/')); ?>" class="nav-logo">
        <?php if (has_custom_logo()) : ?>
          <?php the_custom_logo(); ?>
        <?php else : ?>
          <span class="logo-horse">&#x1F434;</span> <?php bloginfo('name'); ?>
        <?php endif; ?>
      </a>
      <ul class="nav-links">
        <li><a href="<?php echo esc_url(home_url('/')); ?>" class="<?php echo is_front_page() ? 'active' : ''; ?>">Startsida</a></li>
        <li class="nav-dropdown">
          <a href="#" class="nav-dropdown-toggle">Kategorier</a>
          <ul class="nav-dropdown-menu">
            <?php
            $categories = get_terms([
                'taxonomy'   => 'listing_category',
                'hide_empty' => false,
            ]);
            if (!is_wp_error($categories)) :
                foreach ($categories as $cat) : ?>
                    <li><a href="<?php echo esc_url(get_term_link($cat)); ?>"><?php echo esc_html($cat->name); ?></a></li>
                <?php endforeach;
            endif;
            ?>
          </ul>
        </li>
        <li><a href="<?php echo esc_url(home_url('/lan/')); ?>">Alla Län</a></li>
        <li><a href="<?php echo esc_url(get_post_type_archive_link('forum_ad')); ?>">Anslagstavla</a></li>
        <li><a href="<?php echo esc_url(home_url('/blogg/')); ?>">Blogg</a></li>
        <li><a href="<?php echo esc_url(home_url('/annonsera/')); ?>" class="nav-cta">Annonsera</a></li>
      </ul>
      <button class="nav-hamburger" aria-label="Öppna meny" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
