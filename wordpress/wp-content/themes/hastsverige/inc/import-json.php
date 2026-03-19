<?php
/**
 * JSON Import Tool for HästSverige
 *
 * Imports scraped JSON data files (ridskolor, turridning, etc.)
 * into WordPress as Listing custom posts.
 *
 * Usage (WP-CLI):
 *   wp eval-file wp-content/themes/hastsverige/inc/import-json.php -- --file=data/turridning.json --category=turridning
 *   wp eval-file wp-content/themes/hastsverige/inc/import-json.php -- --file=hitta_data.json --category=ridskolor
 *   wp eval-file wp-content/themes/hastsverige/inc/import-json.php -- --all
 *
 * Or via admin: Settings > HästSverige Import
 */

defined('ABSPATH') || exit;

/* ============================================================
   Admin Page for Import
   ============================================================ */
add_action('admin_menu', function () {
    add_options_page(
        'HästSverige Import',
        'HästSverige Import',
        'manage_options',
        'hastsverige-import',
        'hastsverige_import_page'
    );
});

function hastsverige_import_page() {
    if (!current_user_can('manage_options')) return;

    $message = '';

    // Handle form submission
    if (isset($_POST['hastsverige_import_submit']) && check_admin_referer('hastsverige_import')) {
        $file = sanitize_text_field($_POST['import_file'] ?? '');
        $category = sanitize_text_field($_POST['import_category'] ?? '');

        if ($file && $category) {
            $result = hastsverige_import_json($file, $category);
            $message = $result;
        }
    }

    // Scan for available JSON files
    $json_files = [];
    $data_dir = get_template_directory() . '/../../../../../../data/';
    $root_dir = get_template_directory() . '/../../../../../../';

    // Check data/ directory
    if (is_dir($data_dir)) {
        foreach (glob($data_dir . '*.json') as $f) {
            $json_files[] = 'data/' . basename($f);
        }
    }

    // Check root for hitta_data.json
    if (file_exists($root_dir . 'hitta_data.json')) {
        $json_files[] = 'hitta_data.json';
    }

    $categories = get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]);

    ?>
    <div class="wrap">
        <h1>HästSverige — Importera JSON-data</h1>

        <?php if ($message) : ?>
            <div class="notice notice-success"><p><?php echo esc_html($message); ?></p></div>
        <?php endif; ?>

        <form method="post">
            <?php wp_nonce_field('hastsverige_import'); ?>

            <table class="form-table">
                <tr>
                    <th><label for="import_file">JSON-fil</label></th>
                    <td>
                        <select name="import_file" id="import_file">
                            <option value="">Välj fil...</option>
                            <?php foreach ($json_files as $f) : ?>
                                <option value="<?php echo esc_attr($f); ?>"><?php echo esc_html($f); ?></option>
                            <?php endforeach; ?>
                        </select>
                        <p class="description">Eller ange sökväg manuellt:</p>
                        <input type="text" name="import_file_manual" class="regular-text" placeholder="data/turridning.json">
                    </td>
                </tr>
                <tr>
                    <th><label for="import_category">Kategori</label></th>
                    <td>
                        <select name="import_category" id="import_category">
                            <?php if (!is_wp_error($categories)) :
                                foreach ($categories as $cat) : ?>
                                    <option value="<?php echo esc_attr($cat->slug); ?>"><?php echo esc_html($cat->name); ?></option>
                                <?php endforeach;
                            endif; ?>
                        </select>
                    </td>
                </tr>
            </table>

            <?php submit_button('Importera', 'primary', 'hastsverige_import_submit'); ?>
        </form>

        <hr>
        <h2>Statistik</h2>
        <table class="widefat striped">
            <thead>
                <tr><th>Kategori</th><th>Antal</th></tr>
            </thead>
            <tbody>
                <?php if (!is_wp_error($categories)) :
                    foreach ($categories as $cat) : ?>
                        <tr>
                            <td><?php echo esc_html($cat->name); ?></td>
                            <td><?php echo esc_html($cat->count); ?></td>
                        </tr>
                    <?php endforeach;
                endif; ?>
                <tr style="font-weight:bold;">
                    <td>Totalt</td>
                    <td><?php echo esc_html(wp_count_posts('listing')->publish); ?></td>
                </tr>
            </tbody>
        </table>
    </div>
    <?php
}


/* ============================================================
   Import Function
   ============================================================ */
function hastsverige_import_json($file_path, $category_slug, $dry_run = false) {
    // Resolve path relative to project root
    $base = dirname(get_template_directory(), 5);
    $full_path = $base . '/' . ltrim($file_path, '/');

    if (!file_exists($full_path)) {
        return "Filen hittades inte: $full_path";
    }

    $json = file_get_contents($full_path);
    $data = json_decode($json, true);

    if (!$data || !is_array($data)) {
        return "Kunde inte parsa JSON från: $file_path";
    }

    // Ensure category exists
    $term = term_exists($category_slug, 'listing_category');
    if (!$term) {
        return "Kategorin '$category_slug' finns inte. Skapa den först.";
    }

    // County slug mapping
    $county_slugs = [];
    $all_counties = get_terms(['taxonomy' => 'county', 'hide_empty' => false]);
    if (!is_wp_error($all_counties)) {
        foreach ($all_counties as $c) {
            $county_slugs[mb_strtolower($c->name)] = $c->slug;
        }
    }

    $imported = 0;
    $skipped = 0;
    $errors = 0;

    foreach ($data as $entry) {
        $name = trim($entry['name'] ?? '');
        if (!$name) {
            $skipped++;
            continue;
        }

        // Check for duplicate (same name + city)
        $city = trim($entry['city'] ?? '');
        $existing = new WP_Query([
            'post_type'      => 'listing',
            'title'          => $name,
            'posts_per_page' => 1,
            'meta_query'     => $city ? [[
                'key'   => '_listing_city',
                'value' => $city,
            ]] : [],
        ]);

        if ($existing->have_posts()) {
            $skipped++;
            wp_reset_postdata();
            continue;
        }
        wp_reset_postdata();

        if ($dry_run) {
            $imported++;
            continue;
        }

        $post_id = wp_insert_post([
            'post_title'   => $name,
            'post_content' => '',
            'post_type'    => 'listing',
            'post_status'  => 'publish',
        ]);

        if (is_wp_error($post_id)) {
            $errors++;
            continue;
        }

        // Set category
        wp_set_object_terms($post_id, $category_slug, 'listing_category');

        // Set county
        $county_raw = mb_strtolower(trim($entry['county'] ?? ''));
        if ($county_raw && isset($county_slugs[$county_raw])) {
            wp_set_object_terms($post_id, $county_slugs[$county_raw], 'county');
        }

        // Set meta fields
        $meta_map = [
            'phone'   => '_listing_phone',
            'email'   => '_listing_email',
            'website' => '_listing_website',
            'street'  => '_listing_street',
            'city'    => '_listing_city',
            'lat'     => '_listing_lat',
            'lng'     => '_listing_lng',
            'hours'   => '_listing_hours',
        ];

        foreach ($meta_map as $json_key => $meta_key) {
            $val = trim($entry[$json_key] ?? '');
            if ($val) {
                update_post_meta($post_id, $meta_key, $val);
            }
        }

        // Default tier
        update_post_meta($post_id, '_listing_tier', 'free');

        $imported++;
    }

    return sprintf(
        'Import klar! %d importerade, %d överhoppade (dubbletter/tomma), %d fel. Totalt %d poster i filen.',
        $imported, $skipped, $errors, count($data)
    );
}
