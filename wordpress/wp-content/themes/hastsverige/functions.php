<?php
/**
 * HästSverige Theme Functions
 *
 * Sveriges kompletta hästportal — ridskolor, turridning, hästkalas,
 * ridläger, hästpensionat, hovslagare och community-forum.
 *
 * @package HastSverige
 */

defined('ABSPATH') || exit;

define('HASTSVERIGE_VERSION', '1.0.0');
define('HASTSVERIGE_DIR', get_template_directory());
define('HASTSVERIGE_URI', get_template_directory_uri());

/* ============================================================
   Theme Setup
   ============================================================ */
add_action('after_setup_theme', function () {
    // Translations
    load_theme_textdomain('hastsverige', HASTSVERIGE_DIR . '/languages');

    // Theme supports
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'comment-form', 'comment-list', 'gallery', 'caption']);
    add_theme_support('custom-logo', [
        'height'      => 80,
        'width'       => 300,
        'flex-width'  => true,
        'flex-height' => true,
    ]);

    // Image sizes
    add_image_size('listing-card', 400, 300, true);
    add_image_size('listing-hero', 1200, 500, true);
    add_image_size('ad-thumb', 600, 400, true);

    // Menus
    register_nav_menus([
        'primary'   => __('Huvudmeny', 'hastsverige'),
        'footer'    => __('Footermeny', 'hastsverige'),
        'categories'=> __('Kategorimeny', 'hastsverige'),
    ]);
});


/* ============================================================
   Enqueue Styles & Scripts
   ============================================================ */
add_action('wp_enqueue_scripts', function () {
    // Google Fonts
    wp_enqueue_style(
        'hastsverige-fonts',
        'https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400&family=Inter:wght@300;400;500;600;700&display=swap',
        [],
        null
    );

    // Leaflet CSS
    wp_enqueue_style(
        'leaflet',
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
        [],
        '1.9.4'
    );

    // Theme CSS
    wp_enqueue_style(
        'hastsverige-style',
        get_stylesheet_uri(),
        ['hastsverige-fonts', 'leaflet'],
        HASTSVERIGE_VERSION
    );

    // Leaflet JS
    wp_enqueue_script(
        'leaflet',
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
        [],
        '1.9.4',
        true
    );

    // Theme JS
    wp_enqueue_script(
        'hastsverige-main',
        HASTSVERIGE_URI . '/js/main.js',
        ['leaflet'],
        HASTSVERIGE_VERSION,
        true
    );

    // Pass data to JS
    wp_localize_script('hastsverige-main', 'hastsverigeData', [
        'ajaxUrl'  => admin_url('admin-ajax.php'),
        'nonce'    => wp_create_nonce('hastsverige_nonce'),
        'siteUrl'  => home_url('/'),
        'listings' => hastsverige_get_listings_for_map(),
    ]);
});


/* ============================================================
   Custom Post Type: Listing (Verksamhet)
   ============================================================ */
add_action('init', function () {
    register_post_type('listing', [
        'labels' => [
            'name'               => 'Verksamheter',
            'singular_name'      => 'Verksamhet',
            'add_new'            => 'Lägg till verksamhet',
            'add_new_item'       => 'Lägg till ny verksamhet',
            'edit_item'          => 'Redigera verksamhet',
            'new_item'           => 'Ny verksamhet',
            'view_item'          => 'Visa verksamhet',
            'search_items'       => 'Sök verksamheter',
            'not_found'          => 'Inga verksamheter hittades',
            'not_found_in_trash' => 'Inga verksamheter i papperskorgen',
        ],
        'public'             => true,
        'has_archive'        => true,
        'rewrite'            => ['slug' => 'verksamhet', 'with_front' => false],
        'menu_icon'          => 'dashicons-location',
        'supports'           => ['title', 'editor', 'thumbnail', 'excerpt'],
        'show_in_rest'       => true,
        'taxonomies'         => ['listing_category', 'county'],
    ]);
});


/* ============================================================
   Custom Taxonomy: Listing Category (Verksamhetskategori)
   ============================================================ */
add_action('init', function () {
    register_taxonomy('listing_category', 'listing', [
        'labels' => [
            'name'              => 'Kategorier',
            'singular_name'     => 'Kategori',
            'search_items'      => 'Sök kategorier',
            'all_items'         => 'Alla kategorier',
            'parent_item'       => 'Överordnad kategori',
            'parent_item_colon' => 'Överordnad kategori:',
            'edit_item'         => 'Redigera kategori',
            'update_item'       => 'Uppdatera kategori',
            'add_new_item'      => 'Lägg till ny kategori',
            'new_item_name'     => 'Nytt kategorinamn',
        ],
        'hierarchical' => true,
        'public'       => true,
        'rewrite'      => ['slug' => 'kategori', 'with_front' => false],
        'show_in_rest' => true,
    ]);
});


/* ============================================================
   Custom Taxonomy: County (Län)
   ============================================================ */
add_action('init', function () {
    register_taxonomy('county', 'listing', [
        'labels' => [
            'name'          => 'Län',
            'singular_name' => 'Län',
            'search_items'  => 'Sök län',
            'all_items'     => 'Alla län',
            'edit_item'     => 'Redigera län',
            'update_item'   => 'Uppdatera län',
            'add_new_item'  => 'Lägg till nytt län',
            'new_item_name' => 'Nytt länsnamn',
        ],
        'hierarchical' => true,
        'public'       => true,
        'rewrite'      => ['slug' => 'lan', 'with_front' => false],
        'show_in_rest' => true,
    ]);
});


/* ============================================================
   Custom Post Type: Forum Ad (Annons)
   ============================================================ */
add_action('init', function () {
    register_post_type('forum_ad', [
        'labels' => [
            'name'               => 'Annonser',
            'singular_name'      => 'Annons',
            'add_new'            => 'Lägg till annons',
            'add_new_item'       => 'Lägg till ny annons',
            'edit_item'          => 'Redigera annons',
            'new_item'           => 'Ny annons',
            'view_item'          => 'Visa annons',
            'search_items'       => 'Sök annonser',
            'not_found'          => 'Inga annonser hittades',
            'not_found_in_trash' => 'Inga annonser i papperskorgen',
        ],
        'public'             => true,
        'has_archive'        => true,
        'rewrite'            => ['slug' => 'anslagstavla', 'with_front' => false],
        'menu_icon'          => 'dashicons-megaphone',
        'supports'           => ['title', 'editor', 'thumbnail', 'author'],
        'show_in_rest'       => true,
        'taxonomies'         => ['ad_category', 'county'],
    ]);
});


/* ============================================================
   Custom Taxonomy: Ad Category (Annonskategori)
   ============================================================ */
add_action('init', function () {
    register_taxonomy('ad_category', 'forum_ad', [
        'labels' => [
            'name'          => 'Annonskategorier',
            'singular_name' => 'Annonskategori',
            'all_items'     => 'Alla annonskategorier',
            'add_new_item'  => 'Lägg till annonskategori',
        ],
        'hierarchical' => true,
        'public'       => true,
        'rewrite'      => ['slug' => 'annonstyp', 'with_front' => false],
        'show_in_rest' => true,
    ]);
});


/* ============================================================
   Listing Meta Boxes
   ============================================================ */
add_action('add_meta_boxes', function () {
    add_meta_box(
        'listing_details',
        'Verksamhetsdetaljer',
        'hastsverige_listing_meta_box',
        'listing',
        'normal',
        'high'
    );

    add_meta_box(
        'ad_details',
        'Annonsdetaljer',
        'hastsverige_ad_meta_box',
        'forum_ad',
        'normal',
        'high'
    );
});

function hastsverige_listing_meta_box($post) {
    wp_nonce_field('hastsverige_listing_meta', 'hastsverige_listing_nonce');

    $fields = [
        'phone'   => ['label' => 'Telefon',    'type' => 'text'],
        'email'   => ['label' => 'E-post',     'type' => 'email'],
        'website' => ['label' => 'Hemsida',    'type' => 'url'],
        'street'  => ['label' => 'Gatuadress', 'type' => 'text'],
        'city'    => ['label' => 'Stad',        'type' => 'text'],
        'lat'     => ['label' => 'Latitud',     'type' => 'text'],
        'lng'     => ['label' => 'Longitud',    'type' => 'text'],
        'hours'   => ['label' => 'Öppettider', 'type' => 'text'],
        'tier'    => ['label' => 'Nivå (premium/featured/free)', 'type' => 'select', 'options' => ['free', 'featured', 'premium']],
    ];

    echo '<table class="form-table">';
    foreach ($fields as $key => $field) {
        $value = get_post_meta($post->ID, '_listing_' . $key, true);
        echo '<tr>';
        echo '<th><label for="listing_' . $key . '">' . esc_html($field['label']) . '</label></th>';
        echo '<td>';
        if (($field['type'] ?? 'text') === 'select') {
            echo '<select name="listing_' . $key . '" id="listing_' . $key . '">';
            foreach ($field['options'] as $opt) {
                $sel = selected($value, $opt, false);
                echo '<option value="' . esc_attr($opt) . '"' . $sel . '>' . esc_html(ucfirst($opt)) . '</option>';
            }
            echo '</select>';
        } else {
            echo '<input type="' . esc_attr($field['type']) . '" name="listing_' . $key . '" id="listing_' . $key . '" value="' . esc_attr($value) . '" class="regular-text">';
        }
        echo '</td>';
        echo '</tr>';
    }
    echo '</table>';
}

function hastsverige_ad_meta_box($post) {
    wp_nonce_field('hastsverige_ad_meta', 'hastsverige_ad_nonce');

    $fields = [
        'contact_name'  => ['label' => 'Kontaktnamn',  'type' => 'text'],
        'contact_email' => ['label' => 'E-post',       'type' => 'email'],
        'contact_phone' => ['label' => 'Telefon',      'type' => 'text'],
        'location'      => ['label' => 'Ort/Kommun',   'type' => 'text'],
        'expires'       => ['label' => 'Utgår (datum)', 'type' => 'date'],
    ];

    echo '<table class="form-table">';
    foreach ($fields as $key => $field) {
        $value = get_post_meta($post->ID, '_ad_' . $key, true);
        echo '<tr>';
        echo '<th><label for="ad_' . $key . '">' . esc_html($field['label']) . '</label></th>';
        echo '<td><input type="' . esc_attr($field['type']) . '" name="ad_' . $key . '" id="ad_' . $key . '" value="' . esc_attr($value) . '" class="regular-text"></td>';
        echo '</tr>';
    }
    echo '</table>';
}


/* ============================================================
   Save Meta
   ============================================================ */
add_action('save_post_listing', function ($post_id) {
    if (!isset($_POST['hastsverige_listing_nonce']) || !wp_verify_nonce($_POST['hastsverige_listing_nonce'], 'hastsverige_listing_meta')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;

    $fields = ['phone', 'email', 'website', 'street', 'city', 'lat', 'lng', 'hours', 'tier'];
    foreach ($fields as $key) {
        if (isset($_POST['listing_' . $key])) {
            update_post_meta($post_id, '_listing_' . $key, sanitize_text_field($_POST['listing_' . $key]));
        }
    }
});

add_action('save_post_forum_ad', function ($post_id) {
    if (!isset($_POST['hastsverige_ad_nonce']) || !wp_verify_nonce($_POST['hastsverige_ad_nonce'], 'hastsverige_ad_meta')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;

    $fields = ['contact_name', 'contact_email', 'contact_phone', 'location', 'expires'];
    foreach ($fields as $key) {
        if (isset($_POST['ad_' . $key])) {
            update_post_meta($post_id, '_ad_' . $key, sanitize_text_field($_POST['ad_' . $key]));
        }
    }
});


/* ============================================================
   Map Data Helper
   ============================================================ */
function hastsverige_get_listings_for_map($args = []) {
    $defaults = [
        'post_type'      => 'listing',
        'posts_per_page' => -1,
        'post_status'    => 'publish',
    ];
    $query = new WP_Query(array_merge($defaults, $args));
    $listings = [];

    while ($query->have_posts()) {
        $query->the_post();
        $id = get_the_ID();
        $lat = get_post_meta($id, '_listing_lat', true);
        $lng = get_post_meta($id, '_listing_lng', true);

        if (!$lat || !$lng) continue;

        $categories = wp_get_post_terms($id, 'listing_category', ['fields' => 'names']);
        $counties   = wp_get_post_terms($id, 'county', ['fields' => 'names']);

        $listings[] = [
            'id'       => $id,
            'name'     => get_the_title(),
            'lat'      => (float) $lat,
            'lng'      => (float) $lng,
            'city'     => get_post_meta($id, '_listing_city', true),
            'county'   => $counties[0] ?? '',
            'phone'    => get_post_meta($id, '_listing_phone', true),
            'website'  => get_post_meta($id, '_listing_website', true),
            'category' => $categories[0] ?? '',
            'tier'     => get_post_meta($id, '_listing_tier', true) ?: 'free',
            'url'      => get_permalink($id),
        ];
    }
    wp_reset_postdata();

    return $listings;
}


/* ============================================================
   AJAX: Filter listings
   ============================================================ */
add_action('wp_ajax_filter_listings', 'hastsverige_filter_listings');
add_action('wp_ajax_nopriv_filter_listings', 'hastsverige_filter_listings');

function hastsverige_filter_listings() {
    check_ajax_referer('hastsverige_nonce', 'nonce');

    $category = sanitize_text_field($_POST['category'] ?? '');
    $county   = sanitize_text_field($_POST['county'] ?? '');
    $search   = sanitize_text_field($_POST['search'] ?? '');
    $page     = max(1, intval($_POST['page'] ?? 1));
    $per_page = 30;

    $args = [
        'post_type'      => 'listing',
        'posts_per_page' => $per_page,
        'paged'          => $page,
        'post_status'    => 'publish',
        's'              => $search,
        'meta_key'       => '_listing_tier',
        'orderby'        => [
            'meta_value' => 'DESC',
            'title'      => 'ASC',
        ],
    ];

    $tax_query = [];
    if ($category) {
        $tax_query[] = [
            'taxonomy' => 'listing_category',
            'field'    => 'slug',
            'terms'    => $category,
        ];
    }
    if ($county) {
        $tax_query[] = [
            'taxonomy' => 'county',
            'field'    => 'slug',
            'terms'    => $county,
        ];
    }
    if ($tax_query) {
        $args['tax_query'] = $tax_query;
    }

    $query = new WP_Query($args);
    $results = [];

    while ($query->have_posts()) {
        $query->the_post();
        $id = get_the_ID();
        $results[] = [
            'id'       => $id,
            'name'     => get_the_title(),
            'city'     => get_post_meta($id, '_listing_city', true),
            'county'   => implode(', ', wp_get_post_terms($id, 'county', ['fields' => 'names'])),
            'phone'    => get_post_meta($id, '_listing_phone', true),
            'website'  => get_post_meta($id, '_listing_website', true),
            'category' => implode(', ', wp_get_post_terms($id, 'listing_category', ['fields' => 'names'])),
            'tier'     => get_post_meta($id, '_listing_tier', true) ?: 'free',
            'url'      => get_permalink($id),
            'lat'      => (float) get_post_meta($id, '_listing_lat', true),
            'lng'      => (float) get_post_meta($id, '_listing_lng', true),
        ];
    }
    wp_reset_postdata();

    wp_send_json_success([
        'listings'   => $results,
        'total'      => $query->found_posts,
        'pages'      => $query->max_num_pages,
        'current'    => $page,
    ]);
}


/* ============================================================
   AJAX: Filter forum ads
   ============================================================ */
add_action('wp_ajax_filter_ads', 'hastsverige_filter_ads');
add_action('wp_ajax_nopriv_filter_ads', 'hastsverige_filter_ads');

function hastsverige_filter_ads() {
    check_ajax_referer('hastsverige_nonce', 'nonce');

    $category = sanitize_text_field($_POST['category'] ?? '');
    $county   = sanitize_text_field($_POST['county'] ?? '');
    $search   = sanitize_text_field($_POST['search'] ?? '');
    $page     = max(1, intval($_POST['page'] ?? 1));

    $args = [
        'post_type'      => 'forum_ad',
        'posts_per_page' => 20,
        'paged'          => $page,
        'post_status'    => 'publish',
        's'              => $search,
        'orderby'        => 'date',
        'order'          => 'DESC',
    ];

    $tax_query = [];
    if ($category) {
        $tax_query[] = [
            'taxonomy' => 'ad_category',
            'field'    => 'slug',
            'terms'    => $category,
        ];
    }
    if ($county) {
        $tax_query[] = [
            'taxonomy' => 'county',
            'field'    => 'slug',
            'terms'    => $county,
        ];
    }
    if ($tax_query) {
        $args['tax_query'] = $tax_query;
    }

    // Exclude expired ads
    $args['meta_query'] = [
        'relation' => 'OR',
        [
            'key'     => '_ad_expires',
            'value'   => current_time('Y-m-d'),
            'compare' => '>=',
            'type'    => 'DATE',
        ],
        [
            'key'     => '_ad_expires',
            'compare' => 'NOT EXISTS',
        ],
    ];

    $query = new WP_Query($args);
    $results = [];

    while ($query->have_posts()) {
        $query->the_post();
        $id = get_the_ID();
        $results[] = [
            'id'        => $id,
            'title'     => get_the_title(),
            'excerpt'   => wp_trim_words(get_the_content(), 30),
            'category'  => implode(', ', wp_get_post_terms($id, 'ad_category', ['fields' => 'names'])),
            'county'    => implode(', ', wp_get_post_terms($id, 'county', ['fields' => 'names'])),
            'location'  => get_post_meta($id, '_ad_location', true),
            'date'      => get_the_date('Y-m-d'),
            'author'    => get_the_author(),
            'url'       => get_permalink($id),
            'thumbnail' => get_the_post_thumbnail_url($id, 'ad-thumb') ?: '',
        ];
    }
    wp_reset_postdata();

    wp_send_json_success([
        'ads'     => $results,
        'total'   => $query->found_posts,
        'pages'   => $query->max_num_pages,
        'current' => $page,
    ]);
}


/* ============================================================
   Frontend Ad Submission
   ============================================================ */
add_action('wp_ajax_submit_ad', 'hastsverige_submit_ad');

function hastsverige_submit_ad() {
    check_ajax_referer('hastsverige_nonce', 'nonce');

    if (!is_user_logged_in()) {
        wp_send_json_error(['message' => 'Du måste vara inloggad för att lägga en annons.']);
    }

    $title       = sanitize_text_field($_POST['title'] ?? '');
    $content     = wp_kses_post($_POST['content'] ?? '');
    $category    = sanitize_text_field($_POST['ad_category'] ?? '');
    $county      = sanitize_text_field($_POST['county'] ?? '');
    $location    = sanitize_text_field($_POST['location'] ?? '');
    $phone       = sanitize_text_field($_POST['phone'] ?? '');
    $email       = sanitize_email($_POST['email'] ?? '');

    if (!$title || !$content || !$category) {
        wp_send_json_error(['message' => 'Fyll i alla obligatoriska fält (titel, innehåll, kategori).']);
    }

    $post_id = wp_insert_post([
        'post_title'   => $title,
        'post_content' => $content,
        'post_type'    => 'forum_ad',
        'post_status'  => 'pending', // Modereras innan publicering
        'post_author'  => get_current_user_id(),
    ]);

    if (is_wp_error($post_id)) {
        wp_send_json_error(['message' => 'Kunde inte skapa annonsen. Försök igen.']);
    }

    // Set taxonomy terms
    if ($category) {
        wp_set_object_terms($post_id, $category, 'ad_category');
    }
    if ($county) {
        wp_set_object_terms($post_id, $county, 'county');
    }

    // Save meta
    update_post_meta($post_id, '_ad_contact_name', sanitize_text_field(wp_get_current_user()->display_name));
    update_post_meta($post_id, '_ad_contact_email', $email ?: wp_get_current_user()->user_email);
    update_post_meta($post_id, '_ad_contact_phone', $phone);
    update_post_meta($post_id, '_ad_location', $location);
    update_post_meta($post_id, '_ad_expires', date('Y-m-d', strtotime('+30 days')));

    // Handle image upload
    if (!empty($_FILES['ad_image'])) {
        require_once ABSPATH . 'wp-admin/includes/image.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/media.php';
        $attachment_id = media_handle_upload('ad_image', $post_id);
        if (!is_wp_error($attachment_id)) {
            set_post_thumbnail($post_id, $attachment_id);
        }
    }

    wp_send_json_success([
        'message' => 'Din annons har skickats in och väntar på godkännande!',
        'post_id' => $post_id,
    ]);
}


/* ============================================================
   Auto-expire Forum Ads (cron)
   ============================================================ */
add_action('init', function () {
    if (!wp_next_scheduled('hastsverige_expire_ads')) {
        wp_schedule_event(time(), 'daily', 'hastsverige_expire_ads');
    }
});

add_action('hastsverige_expire_ads', function () {
    $expired = new WP_Query([
        'post_type'      => 'forum_ad',
        'posts_per_page' => -1,
        'post_status'    => 'publish',
        'meta_query'     => [
            [
                'key'     => '_ad_expires',
                'value'   => current_time('Y-m-d'),
                'compare' => '<',
                'type'    => 'DATE',
            ],
        ],
    ]);

    while ($expired->have_posts()) {
        $expired->the_post();
        wp_update_post([
            'ID'          => get_the_ID(),
            'post_status' => 'draft',
        ]);
    }
    wp_reset_postdata();
});


/* ============================================================
   Seed Default Taxonomies on Activation
   ============================================================ */
add_action('after_switch_theme', function () {
    // Flush rewrite rules
    flush_rewrite_rules();

    // Listing categories
    $categories = [
        'ridskolor'      => 'Ridskolor',
        'turridning'     => 'Turridning & Ridturer',
        'hastkalas'      => 'Hästkalas & Ponnykalas',
        'ridlager'       => 'Ridläger & Sommarläger',
        'hastpensionat'  => 'Hästpensionat & Hästhotell',
        'hovslagare'     => 'Hovslagare',
    ];
    foreach ($categories as $slug => $name) {
        if (!term_exists($slug, 'listing_category')) {
            wp_insert_term($name, 'listing_category', ['slug' => $slug]);
        }
    }

    // Ad categories
    $ad_cats = [
        'medryttare'    => 'Söker medryttare',
        'stallhjalp'    => 'Stallhjälp',
        'hastdelning'   => 'Hästdelning',
        'fodervard'     => 'Fodervärd',
        'transport'     => 'Hästtransport',
        'utrustning'    => 'Utrustning (köp/sälj/byt)',
        'ovrigt'        => 'Övrigt',
    ];
    foreach ($ad_cats as $slug => $name) {
        if (!term_exists($slug, 'ad_category')) {
            wp_insert_term($name, 'ad_category', ['slug' => $slug]);
        }
    }

    // Counties (21 Swedish counties)
    $counties = [
        'stockholms-lan'      => 'Stockholms län',
        'uppsala-lan'         => 'Uppsala län',
        'sodermanlands-lan'   => 'Södermanlands län',
        'ostergotlands-lan'   => 'Östergötlands län',
        'jonkopings-lan'      => 'Jönköpings län',
        'kronobergs-lan'      => 'Kronobergs län',
        'kalmars-lan'         => 'Kalmars län',
        'gotlands-lan'        => 'Gotlands län',
        'blekinges-lan'       => 'Blekinges län',
        'skanes-lan'          => 'Skånes län',
        'hallands-lan'        => 'Hallands län',
        'vastra-gotalands-lan'=> 'Västra Götalands län',
        'varmlands-lan'       => 'Värmlands län',
        'orebros-lan'         => 'Örebros län',
        'vastmanlands-lan'    => 'Västmanlands län',
        'dalarnas-lan'        => 'Dalarnas län',
        'gavleborgs-lan'      => 'Gävleborgs län',
        'vasternorrlands-lan' => 'Västernorrlands län',
        'jamtlands-lan'       => 'Jämtlands län',
        'vasterbottens-lan'   => 'Västerbottens län',
        'norrbottens-lan'     => 'Norrbottens län',
    ];
    foreach ($counties as $slug => $name) {
        if (!term_exists($slug, 'county')) {
            wp_insert_term($name, 'county', ['slug' => $slug]);
        }
    }
});


/* ============================================================
   Widgets
   ============================================================ */
add_action('widgets_init', function () {
    register_sidebar([
        'name'          => 'Sidebar',
        'id'            => 'sidebar-1',
        'before_widget' => '<div class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ]);
});


/* ============================================================
   Include files
   ============================================================ */
require_once HASTSVERIGE_DIR . '/inc/import-json.php';
