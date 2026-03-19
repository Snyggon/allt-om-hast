/**
 * main.js — HästSverige
 * Handles table rendering, search, filter, sort, pagination,
 * SVG map interaction, and Leaflet map with category-colored markers.
 */

(function () {
  'use strict';

  /* ============================================================
     Constants & State
     ============================================================ */
  const ROWS_PER_PAGE = 30;

  // Category display names and colors
  const CATEGORY_INFO = {
    ridskolor:     { name: 'Ridskolor',                  color: '#C4607A', icon: '🏇' },
    turridning:    { name: 'Turridning & Ridturer',      color: '#4A7C59', icon: '🌲' },
    hastkalas:     { name: 'Hästkalas & Ponnykalas',      color: '#9B59B6', icon: '🎉' },
    ridlager:      { name: 'Ridläger & Sommarläger',      color: '#E67E22', icon: '⛺' },
    hastpensionat: { name: 'Hästpensionat & Hästhotell',  color: '#3498DB', icon: '🏠' },
    hovslagare:    { name: 'Hovslagare',                  color: '#C9963C', icon: '🔨' }
  };

  let allData = [];
  let filteredData = [];
  let currentPage = 1;
  let sortColumn = null;
  let sortDir = 'asc';
  let leafletMap = null;
  let leafletMarkers = [];

  /* ============================================================
     Boot
     ============================================================ */
  document.addEventListener('DOMContentLoaded', function () {
    if (typeof window.RIDSKOLOR_DATA !== 'undefined') {
      init(window.RIDSKOLOR_DATA);
    } else {
      setTimeout(function () {
        if (typeof window.RIDSKOLOR_DATA !== 'undefined') {
          init(window.RIDSKOLOR_DATA);
        } else {
          console.warn('RIDSKOLOR_DATA not found. Make sure js/data.js is loaded.');
        }
      }, 200);
    }
  });

  /* ============================================================
     Init
     ============================================================ */
  function init(data) {
    allData = Array.isArray(data) ? data : [];

    // Read URL params
    var params = new URLSearchParams(window.location.search);
    var countyParam = params.get('county') || '';
    var categoryParam = params.get('category') || '';

    // Region page: check body class and data attribute
    var body = document.body;
    if (body.classList.contains('region-page')) {
      var regionCounty = body.getAttribute('data-county') || '';
      if (regionCounty) {
        initWithFilters(regionCounty, categoryParam);
        return;
      }
    }

    initWithFilters(countyParam, categoryParam);
  }

  function initWithFilters(preselectedCounty, preselectedCategory) {
    buildCountyDropdown(preselectedCounty);
    buildCategoryDropdown(preselectedCategory);
    applyFilters();
    initTable();
    initSVGMap();
    initLeafletMap();
    bindEvents();

    // Apply preselected filters
    if (preselectedCounty || preselectedCategory) {
      var sel = document.getElementById('county-filter');
      if (sel && preselectedCounty) sel.value = preselectedCounty;
      var catSel = document.getElementById('category-filter');
      if (catSel && preselectedCategory) catSel.value = preselectedCategory;
      applyFilters();
      renderTable();
    }
  }

  /* ============================================================
     County Dropdown
     ============================================================ */
  function buildCountyDropdown(selected) {
    var sel = document.getElementById('county-filter');
    if (!sel) return;

    var counties = [];
    var seen = {};
    allData.forEach(function (d) {
      if (d.county && !seen[d.county]) {
        seen[d.county] = true;
        counties.push(d.county);
      }
    });
    counties.sort();

    sel.innerHTML = '<option value="">📍 Alla Län</option>';
    counties.forEach(function (county) {
      var opt = document.createElement('option');
      opt.value = county;
      opt.textContent = county;
      if (county === selected) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  /* ============================================================
     Category Dropdown
     ============================================================ */
  function buildCategoryDropdown(selected) {
    var sel = document.getElementById('category-filter');
    if (!sel) return;

    // Collect unique categories from data
    var cats = [];
    var seen = {};
    allData.forEach(function (d) {
      var cat = d.category || '';
      if (cat && !seen[cat]) {
        seen[cat] = true;
        cats.push(cat);
      }
    });

    // Sort by CATEGORY_INFO order
    var order = Object.keys(CATEGORY_INFO);
    cats.sort(function (a, b) {
      return (order.indexOf(a) === -1 ? 99 : order.indexOf(a)) -
             (order.indexOf(b) === -1 ? 99 : order.indexOf(b));
    });

    sel.innerHTML = '<option value="">🗂️ Alla Kategorier</option>';
    cats.forEach(function (cat) {
      var info = CATEGORY_INFO[cat];
      var opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = info ? info.icon + ' ' + info.name : cat;
      if (cat === selected) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  /* ============================================================
     Filters & Search
     ============================================================ */
  function applyFilters() {
    var searchInput = document.getElementById('search-input');
    var countyFilter = document.getElementById('county-filter');
    var categoryFilter = document.getElementById('category-filter');

    var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    var county = countyFilter ? countyFilter.value : '';
    var category = categoryFilter ? categoryFilter.value : '';

    filteredData = allData.filter(function (entry) {
      // County filter
      if (county && entry.county !== county) return false;

      // Category filter
      if (category && entry.category !== category) return false;

      // Text search across all relevant fields
      if (query) {
        var catInfo = CATEGORY_INFO[entry.category] || {};
        var haystack = [
          entry.name,
          entry.county,
          entry.city,
          entry.phone,
          entry.website,
          entry.hours,
          catInfo.name || entry.category || '',
          (entry.services || []).join(' ')
        ].join(' ').toLowerCase();
        if (!haystack.includes(query)) return false;
      }

      return true;
    });

    // Apply sort
    if (sortColumn !== null) {
      sortData();
    } else {
      // Default: featured/premium first, then alphabetical
      filteredData.sort(function (a, b) {
        var tierA = tierRank(a.tier);
        var tierB = tierRank(b.tier);
        if (tierA !== tierB) return tierB - tierA;
        return (a.name || '').localeCompare(b.name || '', 'sv');
      });
    }

    currentPage = 1;
  }

  function tierRank(tier) {
    if (tier === 'premium') return 2;
    if (tier === 'featured') return 1;
    return 0;
  }

  /* ============================================================
     Sort
     ============================================================ */
  var SORT_KEYS = ['name', 'category', 'county', 'city', 'phone', 'website'];

  function sortData() {
    var key = SORT_KEYS[sortColumn];
    if (!key) return;

    filteredData.sort(function (a, b) {
      var va = a[key] || '';
      var vb = b[key] || '';

      if (Array.isArray(va)) va = va.join(', ');
      if (Array.isArray(vb)) vb = vb.join(', ');

      // For category sort, use display name
      if (key === 'category') {
        var infoA = CATEGORY_INFO[va] || {};
        var infoB = CATEGORY_INFO[vb] || {};
        va = infoA.name || va;
        vb = infoB.name || vb;
      }

      va = va.toString().toLowerCase();
      vb = vb.toString().toLowerCase();

      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }

  /* ============================================================
     Table Rendering
     ============================================================ */
  function initTable() {
    var ths = document.querySelectorAll('.directory-table th[data-col]');
    ths.forEach(function (th, i) {
      th.addEventListener('click', function () {
        if (sortColumn === i) {
          sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          sortColumn = i;
          sortDir = 'asc';
        }
        sortData();
        renderTable();
        updateSortIcons();
      });
    });
    renderTable();
  }

  function renderTable() {
    var tbody = document.getElementById('table-body');
    if (!tbody) return;

    var total = filteredData.length;
    var start = (currentPage - 1) * ROWS_PER_PAGE;
    var end = Math.min(start + ROWS_PER_PAGE, total);
    var pageData = filteredData.slice(start, end);

    // Result count
    var countEl = document.getElementById('result-count');
    if (countEl) {
      if (total === 0) {
        countEl.textContent = '';
      } else {
        countEl.textContent = 'Visar ' + (start + 1) + '–' + end + ' av ' + total + ' verksamheter';
      }
    }

    // Empty state
    if (total === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="no-results"><span>🔍</span>Inga verksamheter hittades för din sökning.</td></tr>';
      renderPagination(0);
      return;
    }

    // Build rows
    var rows = pageData.map(function (entry) {
      var websiteHost = entry.website ? entry.website.replace(/^https?:\/\//, '').replace(/\/$/, '') : '';
      var websiteLink = entry.website
        ? '<a href="' + escapeHtml(entry.website) + '" target="_blank" rel="noopener">' + escapeHtml(websiteHost) + '</a>'
        : '–';

      // Category tag
      var catInfo = CATEGORY_INFO[entry.category] || {};
      var catColor = catInfo.color || '#888';
      var catName = catInfo.name || entry.category || '–';
      var catTag = '<span class="cat-tag" style="--cat-color:' + catColor + '">' + escapeHtml(catName) + '</span>';

      // Featured / Premium badge
      var rowClass = '';
      var badge = '';
      if (entry.tier === 'premium') {
        rowClass = ' class="row-premium"';
        badge = ' <span class="tier-badge tier-premium" title="Premium-listning">🏆</span>';
      } else if (entry.tier === 'featured') {
        rowClass = ' class="row-featured"';
        badge = ' <span class="tier-badge tier-featured" title="Framhävd listning">⭐</span>';
      }

      return '<tr' + rowClass + '>' +
        '<td><strong>' + escapeHtml(entry.name) + '</strong>' + badge + '</td>' +
        '<td>' + catTag + '</td>' +
        '<td>' + escapeHtml(entry.county || '–') + '</td>' +
        '<td>' + escapeHtml(entry.city || '–') + '</td>' +
        '<td>' + escapeHtml(entry.phone || '–') + '</td>' +
        '<td>' + websiteLink + '</td>' +
        '</tr>';
    });

    tbody.innerHTML = rows.join('');
    renderPagination(total);
  }

  /* ============================================================
     Pagination
     ============================================================ */
  function renderPagination(total) {
    var pag = document.getElementById('pagination');
    if (!pag) return;

    var totalPages = Math.ceil(total / ROWS_PER_PAGE);

    if (totalPages <= 1) {
      pag.innerHTML = '';
      return;
    }

    var maxVisible = 7;
    var startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    var endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    var buttons = [];

    if (currentPage > 1) {
      buttons.push('<button data-page="' + (currentPage - 1) + '">&#8249; Föregående</button>');
    }

    if (startPage > 1) {
      buttons.push('<button data-page="1">1</button>');
      if (startPage > 2) buttons.push('<button disabled>…</button>');
    }

    for (var p = startPage; p <= endPage; p++) {
      var cls = p === currentPage ? ' class="active"' : '';
      buttons.push('<button' + cls + ' data-page="' + p + '">' + p + '</button>');
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) buttons.push('<button disabled>…</button>');
      buttons.push('<button data-page="' + totalPages + '">' + totalPages + '</button>');
    }

    if (currentPage < totalPages) {
      buttons.push('<button data-page="' + (currentPage + 1) + '">Nästa &#8250;</button>');
    }

    pag.innerHTML = buttons.join('');

    pag.querySelectorAll('button[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        currentPage = parseInt(this.getAttribute('data-page'), 10);
        renderTable();
        var tableEl = document.querySelector('.directory-table');
        if (tableEl) tableEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  /* ============================================================
     Sort Icons
     ============================================================ */
  function updateSortIcons() {
    var ths = document.querySelectorAll('.directory-table th[data-col]');
    ths.forEach(function (th, i) {
      var icon = th.querySelector('.sort-icon');
      if (!icon) return;
      th.removeAttribute('aria-sort');
      if (i === sortColumn) {
        icon.textContent = sortDir === 'asc' ? ' ▲' : ' ▼';
        th.setAttribute('aria-sort', sortDir === 'asc' ? 'ascending' : 'descending');
      } else {
        icon.textContent = ' ⇅';
      }
    });
  }

  /* ============================================================
     Event Bindings
     ============================================================ */
  function bindEvents() {
    // Search input (debounced)
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
      var debounceTimer;
      searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
          applyFilters();
          renderTable();
          updateLeafletMarkers();
        }, 250);
      });
    }

    // County filter
    var countyFilter = document.getElementById('county-filter');
    if (countyFilter) {
      countyFilter.addEventListener('change', function () {
        applyFilters();
        renderTable();
        updateSVGMap();
        updateLeafletMarkers();
      });
    }

    // Category filter
    var categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
      categoryFilter.addEventListener('change', function () {
        applyFilters();
        renderTable();
        updateLeafletMarkers();
      });
    }

    // Hamburger menu
    var hamburger = document.querySelector('.nav-hamburger');
    var navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
      hamburger.addEventListener('click', function () {
        hamburger.classList.toggle('open');
        navLinks.classList.toggle('open');
      });
    }
  }

  /* ============================================================
     SVG Map
     ============================================================ */
  function initSVGMap() {
    var svgMap = document.getElementById('svg-map');
    if (!svgMap) return;

    var tooltip = document.getElementById('map-tooltip');
    var paths = svgMap.querySelectorAll('path[data-county]');

    paths.forEach(function (path) {
      var countyName = path.getAttribute('data-county');

      path.addEventListener('click', function () {
        var sel = document.getElementById('county-filter');
        if (sel) {
          if (sel.value === countyName) {
            sel.value = '';
          } else {
            sel.value = countyName;
          }
          applyFilters();
          renderTable();
          updateSVGMap();
          updateLeafletMarkers();
        }

        var searchSection = document.getElementById('search');
        if (searchSection) {
          searchSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });

      path.addEventListener('mouseenter', function () {
        if (tooltip) {
          var count = allData.filter(function (d) { return d.county === countyName; }).length;
          tooltip.textContent = countyName + (count > 0 ? ' (' + count + ' verksamheter)' : '');
          tooltip.style.opacity = '1';
        }
      });

      path.addEventListener('mousemove', function (e) {
        if (tooltip) {
          tooltip.style.left = (e.clientX + 14) + 'px';
          tooltip.style.top = (e.clientY - 30) + 'px';
        }
      });

      path.addEventListener('mouseleave', function () {
        if (tooltip) {
          tooltip.style.opacity = '0';
        }
      });
    });
  }

  function updateSVGMap() {
    var svgMap = document.getElementById('svg-map');
    if (!svgMap) return;

    var countyFilter = document.getElementById('county-filter');
    var selected = countyFilter ? countyFilter.value : '';

    svgMap.querySelectorAll('path[data-county]').forEach(function (path) {
      path.classList.remove('active');
      if (selected && path.getAttribute('data-county') === selected) {
        path.classList.add('active');
      }
    });
  }

  /* ============================================================
     Leaflet Map — Category-colored markers
     ============================================================ */
  function makeMarkerIcon(color) {
    return L.divIcon({
      className: '',
      html: '<div style="width:12px;height:12px;background:' + color + ';border:2px solid #fff;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>',
      iconSize: [12, 12],
      iconAnchor: [6, 6],
      popupAnchor: [0, -8]
    });
  }

  function initLeafletMap() {
    var mapEl = document.getElementById('leaflet-map');
    if (!mapEl || typeof L === 'undefined') return;

    leafletMap = L.map('leaflet-map').setView([62.0, 15.0], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18
    }).addTo(leafletMap);

    // Add markers for all entries
    allData.forEach(function (entry) {
      if (!entry.lat || !entry.lng) return;

      var catInfo = CATEGORY_INFO[entry.category] || {};
      var color = catInfo.color || '#3a5a4a';
      var catName = catInfo.name || '';

      var websiteLink = entry.website
        ? '<a href="' + entry.website + '" target="_blank" rel="noopener">' + entry.website.replace(/^https?:\/\//, '') + '</a>'
        : '';

      var popupContent =
        '<strong>' + escapeHtml(entry.name) + '</strong>' +
        (catName ? '<br><em style="color:' + color + '">' + escapeHtml(catName) + '</em>' : '') +
        '<br>' + escapeHtml(entry.city || '') + (entry.county ? ', ' + escapeHtml(entry.county) : '') +
        (entry.phone ? '<br>' + escapeHtml(entry.phone) : '') +
        (websiteLink ? '<br>' + websiteLink : '');

      var marker = L.marker([entry.lat, entry.lng], { icon: makeMarkerIcon(color) })
        .bindPopup(popupContent);

      marker.entry = entry;
      marker.addTo(leafletMap);
      leafletMarkers.push(marker);
    });
  }

  function updateLeafletMarkers() {
    if (!leafletMap) return;
    var countyFilter = document.getElementById('county-filter');
    var categoryFilter = document.getElementById('category-filter');
    var selectedCounty = countyFilter ? countyFilter.value : '';
    var selectedCategory = categoryFilter ? categoryFilter.value : '';

    leafletMarkers.forEach(function (marker) {
      var show = true;
      if (selectedCounty && marker.entry.county !== selectedCounty) show = false;
      if (selectedCategory && marker.entry.category !== selectedCategory) show = false;

      if (show) {
        if (!leafletMap.hasLayer(marker)) marker.addTo(leafletMap);
      } else {
        if (leafletMap.hasLayer(marker)) leafletMap.removeLayer(marker);
      }
    });

    // Fit bounds to visible markers
    if (selectedCounty || selectedCategory) {
      var visible = leafletMarkers.filter(function (m) {
        return leafletMap.hasLayer(m);
      });
      if (visible.length > 0) {
        var group = L.featureGroup(visible);
        leafletMap.fitBounds(group.getBounds().pad(0.3));
      }
    } else {
      leafletMap.setView([62.0, 15.0], 5);
    }
  }

  /* ============================================================
     Utility
     ============================================================ */
  function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

})();
