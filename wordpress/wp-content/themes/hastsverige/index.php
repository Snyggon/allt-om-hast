<?php
/**
 * Default template — fallback for all views.
 */
get_header();
?>

<div class="container" style="padding: 4rem 1.5rem;">
  <?php if (have_posts()) : ?>
    <div class="section-header">
      <h1><?php
        if (is_search()) {
            printf('Sökresultat för: "%s"', get_search_query());
        } elseif (is_archive()) {
            the_archive_title();
        } else {
            echo 'Senaste inläggen';
        }
      ?></h1>
    </div>

    <div class="blog-teaser-grid">
      <?php while (have_posts()) : the_post(); ?>
        <article class="blog-mini-card">
          <?php if (has_post_thumbnail()) : ?>
            <a href="<?php the_permalink(); ?>">
              <?php the_post_thumbnail('listing-card'); ?>
            </a>
          <?php endif; ?>
          <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
          <p><?php echo wp_trim_words(get_the_excerpt(), 20); ?></p>
        </article>
      <?php endwhile; ?>
    </div>

    <div id="pagination" style="margin-top:2rem;">
      <?php the_posts_pagination(['mid_size' => 2]); ?>
    </div>

  <?php else : ?>
    <p>Inget innehåll hittades.</p>
  <?php endif; ?>
</div>

<?php get_footer(); ?>
