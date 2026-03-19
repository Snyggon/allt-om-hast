/**
 * HästSverige — Main JavaScript
 * Handles Leaflet map, AJAX search/filter, table rendering, pagination,
 * mobile navigation, and category tabs.
 */

(function () {
  'use strict';

  /* ============================================================
     State
     ============================================================ */
  var allListings = [];
  var filteredListings = [];
  var leafletMap = null;
  var markerLayer = null;
  var currentPage = 1;
  var currentCategory = '';
  var currentCounty = '';
  var searchQuery = '';
  var ROWS_PER_PAGE = 30;

  /* ============================================================
     Boot
     ============================================================ */
  document.addEventListener('DOMContentLoaded', function () {
    // Load listings from localized data
    if (typeof hastsverigeData !== 'undefined' && hastsverigeData.listings) {
      allListings = hastsverigeData.listings;
      filteredListings = allListings.slice();
    }

    initLeafletMap();
    initSearch();
    initCategoryTabs();
    initMobileNav();
    initDropdowns();
    renderTable();
    updateMarkers();
  });

  /* ============================================================
     Leaflet Map
     ============================================================ */
  function initLeafletMap() {
    var mapEl = document.getElementById('leaflet-map');
    if (!mapEl || typeof L === 'undefined') return;

    // Check for pre-set filters (archive pages)
    var filterCat = mapEl.dataset.filterCategory || '';
    var filterCounty = mapEl.dataset.filterCounty || '';

    if (filterCat) currentCategory = filterCat;
    if (filterCounty) currentCounty = filterCounty;

    leafletMap = L.map('leaflet-map', {
      scrollWheelZoom: false
    }).setView([62.5, 16.5], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
      maxZoom: 18
    }).addTo(leafletMap);

    markerLayer = L.layerGroup().addTo(leafletMap);
    updateMarkers();
  }

  function updateMarkers() {
    if (!markerLayer) return;
    markerLayer.clearLayers();

    var bounds = [];
    var listings = getFilteredListings();

    // Category colors
    var catColors = {
      'ridskolor': '#C4607A',
      'turridning': '#4A7C59',
      'hastkalas': '#C9963C',
      'ridlager': '#6B4A58',
      'hastpensionat': '#2E5240',
      'hovslagare': '#856404'
    };

    listings.forEach(function (item) {
      if (!item.lat || !item.lng) return;

      var catSlug = (item.category || '').toLowerCase()
        .replace(/[åä]/g, 'a').replace(/ö/g, 'o')
        .replace(/[^a-z]/g, '');
      var color = catColors[catSlug] || '#C4607A';

      var icon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="width:12px;height:12px;border-radius:50%;background:' + color + ';border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3);"></div>',
        iconSize: [12, 12],
        iconAnchor: [6, 6]
      });

      var marker = L.marker([item.lat, item.lng], { icon: icon });

      var popup = '<div style="font-size:0.9rem;min-width:180px;">';
      popup += '<strong>' + escapeHtml(item.name) + '</strong>';
      if (item.category) popup += '<br><span style="color:#6B4A58;font-size:0.8rem;">' + escapeHtml(item.category) + '</span>';
      if (item.city) popup += '<br>' + escapeHtml(item.city);
      if (item.phone) popup += '<br><a href="tel:' + escapeHtml(item.phone) + '">' + escapeHtml(item.phone) + '</a>';
      if (item.url) popup += '<br><a href="' + escapeHtml(item.url) + '">Visa detaljer &rarr;</a>';
      popup += '</div>';

      marker.bindPopup(popup);
      markerLayer.addLayer(marker);
      bounds.push([item.lat, item.lng]);
    });

    if (bounds.length > 0 && leafletMap) {
      leafletMap.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 });
    }
  }

  /* ============================================================
     Filtering
     ============================================================ */
  function getFilteredListings() {
    return allListings.filter(function (item) {
      // Category filter
      if (currentCategory) {
        var catSlug = slugify(item.category || '');
        if (catSlug !== currentCategory && item.category !== currentCategory) return false;
      }

      // County filter
      if (currentCounty) {
        var countySlug = slugify(item.county || '');
        if (countySlug !== currentCounty && item.county !== currentCounty) return false;
      }

      // Text search
      if (searchQuery) {
        var q = searchQuery.toLowerCase();
        var haystack = [item.name, item.city, item.county, item.category, item.phone]
          .join(' ').toLowerCase();
        if (haystack.indexOf(q) === -1) return false;
      }

      return true;
    });
  }

  function applyFilters() {
    filteredListings = getFilteredListings();

    // Sort: premium first, then featured, then alphabetical
    var tierOrder = { 'premium': 0, 'featured': 1, 'free': 2 };
    filteredListings.sort(function (a, b) {
      var ta = tierOrder[a.tier] !== undefined ? tierOrder[a.tier] : 2;
      var tb = tierOrder[b.tier] !== undefined ? tierOrder[b.tier] : 2;
      if (ta !== tb) return ta - tb;
      return (a.name || '').localeCompare(b.name || '', 'sv');
    });

    currentPage = 1;
    renderTable();
    updateMarkers();
    updateResultCount();
  }

  /* ============================================================
     Search & Filters
     ============================================================ */
  function initSearch() {
    var searchInput = document.getElementById('search-input');
    var countyFilter = document.getElementById('county-filter');

    if (searchInput) {
      var timeout;
      searchInput.addEventListener('input', function () {
        clearTimeout(timeout);
        timeout = setTimeout(function () {
          searchQuery = searchInput.value.trim();
          applyFilters();
        }, 300);
      });
    }

    if (countyFilter) {
      countyFilter.addEventListener('change', function () {
        currentCounty = countyFilter.value;
        applyFilters();
      });
    }
  }

  function initCategoryTabs() {
    var tabs = document.querySelectorAll('.category-tab[data-category]');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function (e) {
        e.preventDefault();
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        currentCategory = tab.dataset.category;
        applyFilters();
      });
    });
  }

  /* ============================================================
     Table Rendering
     ============================================================ */
  function renderTable() {
    var tbody = document.getElementById('table-body');
    if (!tbody) return;

    var start = (currentPage - 1) * ROWS_PER_PAGE;
    var page = filteredListings.slice(start, start + ROWS_PER_PAGE);

    if (page.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:2rem;color:#9E8090;">Inga verksamheter matchade din sökning.</td></tr>';
      renderPagination(0);
      return;
    }

    var html = '';
    page.forEach(function (item) {
      var tierClass = item.tier && item.tier !== 'free' ? ' class="tier-' + escapeHtml(item.tier) + '"' : '';
      var badge = '';
      if (item.tier === 'premium') badge = '&#x1F3C6; ';
      if (item.tier === 'featured') badge = '&#x2B50; ';

      html += '<tr' + tierClass + '>';
      html += '<td><a href="' + escapeHtml(item.url || '#') + '" style="font-weight:600;">' + badge + escapeHtml(item.name) + '</a></td>';
      html += '<td>' + escapeHtml(item.category || '') + '</td>';
      html += '<td>' + escapeHtml(item.county || '') + '</td>';
      html += '<td>' + escapeHtml(item.city || '') + '</td>';
      html += '<td>' + (item.phone ? '<a href="tel:' + escapeHtml(item.phone) + '">' + escapeHtml(item.phone) + '</a>' : '—') + '</td>';
      html += '<td>' + (item.website ? '<a href="' + escapeHtml(item.website) + '" target="_blank" rel="noopener">Besök &#x2197;</a>' : '—') + '</td>';
      html += '</tr>';
    });

    tbody.innerHTML = html;
    renderPagination(filteredListings.length);
  }

  function renderPagination(total) {
    var pagDiv = document.getElementById('pagination');
    if (!pagDiv) return;

    var pages = Math.ceil(total / ROWS_PER_PAGE);
    if (pages <= 1) {
      pagDiv.innerHTML = '';
      return;
    }

    var html = '';
    for (var i = 1; i <= pages; i++) {
      html += '<button class="' + (i === currentPage ? 'active' : '') + '" data-page="' + i + '">' + i + '</button>';
    }
    pagDiv.innerHTML = html;

    pagDiv.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        currentPage = parseInt(btn.dataset.page);
        renderTable();
        // Scroll to table
        var searchSection = document.getElementById('search');
        if (searchSection) searchSection.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  function updateResultCount() {
    var countEl = document.getElementById('result-count');
    if (countEl) {
      countEl.textContent = filteredListings.length + ' verksamheter';
    }
  }

  /* ============================================================
     Mobile Navigation
     ============================================================ */
  function initMobileNav() {
    var hamburger = document.querySelector('.nav-hamburger');
    var navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
      hamburger.addEventListener('click', function () {
        var expanded = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', !expanded);
        navLinks.classList.toggle('open');
      });
    }
  }

  function initDropdowns() {
    // Touch-friendly dropdowns
    var dropdowns = document.querySelectorAll('.nav-dropdown');
    dropdowns.forEach(function (dd) {
      var toggle = dd.querySelector('.nav-dropdown-toggle');
      if (toggle) {
        toggle.addEventListener('click', function (e) {
          e.preventDefault();
          dd.classList.toggle('open');
        });
      }
    });
  }

  /* ============================================================
     Utilities
     ============================================================ */
  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function slugify(str) {
    return str.toLowerCase()
      .replace(/[åä]/g, 'a')
      .replace(/ö/g, 'o')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  }

})();
