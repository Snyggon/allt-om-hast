<?php
/**
 * Default Page Template
 */
get_header();
?>

<div class="container" style="padding: 2rem 1.5rem 4rem;max-width:900px;">
  <?php while (have_posts()) : the_post(); ?>
    <h1 style="margin-bottom:1.5rem;"><?php the_title(); ?></h1>
    <div class="entry-content" style="font-size:1rem;line-height:1.8;">
      <?php the_content(); ?>
    </div>
  <?php endwhile; ?>
</div>

<?php get_footer(); ?>
