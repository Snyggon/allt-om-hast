<?php
/**
 * Single Post Template (Blog posts)
 */
get_header();
?>

<article class="container" style="padding: 2rem 1.5rem 4rem;max-width:800px;">

  <nav class="breadcrumbs" style="margin-bottom:1.5rem;font-size:0.9rem;color:var(--text-mid);">
    <a href="<?php echo esc_url(home_url('/')); ?>">Startsida</a> &rsaquo;
    <a href="<?php echo esc_url(home_url('/blogg/')); ?>">Blogg</a> &rsaquo;
    <span><?php the_title(); ?></span>
  </nav>

  <?php while (have_posts()) : the_post(); ?>

    <header style="margin-bottom:2rem;">
      <h1 style="font-size:clamp(1.8rem, 4vw, 2.6rem);"><?php the_title(); ?></h1>
      <div style="color:var(--text-mid);font-size:0.9rem;margin-top:0.5rem;">
        <span><?php echo get_the_date(); ?></span>
        &middot;
        <span><?php echo get_the_author(); ?></span>
        <?php
        $cats = get_the_category();
        if ($cats) :
            echo ' &middot; ';
            foreach ($cats as $cat) :
                echo '<a href="' . esc_url(get_category_link($cat->term_id)) . '">' . esc_html($cat->name) . '</a> ';
            endforeach;
        endif;
        ?>
      </div>
    </header>

    <?php if (has_post_thumbnail()) : ?>
      <div style="border-radius:16px;overflow:hidden;margin-bottom:2rem;">
        <?php the_post_thumbnail('large', ['style' => 'width:100%;height:auto;']); ?>
      </div>
    <?php endif; ?>

    <div class="entry-content" style="font-size:1.05rem;line-height:1.85;">
      <?php the_content(); ?>
    </div>

    <div style="margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border);">
      <?php
      $prev = get_previous_post();
      $next = get_next_post();
      ?>
      <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
        <?php if ($prev) : ?>
          <a href="<?php echo get_permalink($prev); ?>" style="color:var(--text-mid);">&larr; <?php echo esc_html($prev->post_title); ?></a>
        <?php endif; ?>
        <?php if ($next) : ?>
          <a href="<?php echo get_permalink($next); ?>" style="color:var(--text-mid);text-align:right;"><?php echo esc_html($next->post_title); ?> &rarr;</a>
        <?php endif; ?>
      </div>
    </div>

  <?php endwhile; ?>

</article>

<?php get_footer(); ?>
