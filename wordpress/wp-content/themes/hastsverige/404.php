<?php
/**
 * 404 Not Found Template
 */
get_header();
?>

<div class="container" style="text-align:center;padding:6rem 1.5rem;">
  <div style="font-size:4rem;margin-bottom:1rem;">&#x1F434;</div>
  <h1>Sidan hittades inte</h1>
  <p style="color:var(--text-mid);margin:1rem 0 2rem;font-size:1.1rem;">Det verkar som att hästen har sprungit iväg med sidan du letade efter.</p>
  <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">&#x1F3E0; Tillbaka till startsidan</a>
</div>

<?php get_footer(); ?>
