/* ===== PlantGuide Web UI — App Logic ===== */
(function() {
  'use strict';

  const { species, tag_categories, all_tags } = PLANTGUIDE_DATA;
  let activeTags = new Set();
  let searchQuery = '';
  let selectedSpecies = null;

  // ===== DOM Refs =====
  const $ = id => document.getElementById(id);
  const speciesGrid = $('species-grid');
  const tagSections = $('tag-sections');
  const activeFilters = $('active-filters');
  const filterChips = $('filter-chips');
  const searchInput = $('search-input');
  const emptyState = $('empty-state');
  const visibleCount = $('visible-count');
  const clearTags = $('clear-tags');
  const clearAllFilters = $('clear-all-filters');
  const careModal = $('care-modal');
  const modalBody = $('modal-body');
  const modalClose = $('modal-close');

  // ===== Render Tag Sections =====
  function renderTagSections() {
    let html = '';
    for (const [category, categoryTags] of Object.entries(tag_categories)) {
      const available = categoryTags.filter(t => all_tags.includes(t));
      if (available.length === 0) continue;
      html += `<div class="tag-section">
        <div class="tag-section-title">${category}</div>
        <div class="tag-section-tags">`;
      for (const tag of available) {
        const count = species.filter(s => s.tags.some(t => t.toLowerCase() === tag)).length;
        const active = activeTags.has(tag) ? 'active' : '';
        html += `<button class="tag-chip ${active}" data-tag="${tag}">
          ${tag} <span class="tag-count">${count}</span>
        </button>`;
      }
      html += `</div></div>`;
    }
    tagSections.innerHTML = html;

    // Tag click handlers
    tagSections.querySelectorAll('.tag-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const tag = btn.dataset.tag;
        if (activeTags.has(tag)) {
          activeTags.delete(tag);
        } else {
          activeTags.add(tag);
        }
        render();
      });
    });
  }

  // ===== Render Species Grid =====
  function renderSpecies() {
    const filtered = species.filter(s => {
      // Search filter
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const nameMatch = s.common_name.toLowerCase().includes(q);
        const sciMatch = s.scientific_name.toLowerCase().includes(q);
        const idMatch = s.id.toLowerCase().includes(q);
        const tagMatch = s.tags.some(t => t.toLowerCase().includes(q));
        if (!nameMatch && !sciMatch && !idMatch && !tagMatch) return false;
      }
      // Tag filter
      if (activeTags.size > 0) {
        const speciesTags = s.tags.map(t => t.toLowerCase());
        for (const tag of activeTags) {
          if (!speciesTags.includes(tag)) return false;
        }
      }
      return true;
    });

    visibleCount.textContent = filtered.length;
    emptyState.style.display = filtered.length === 0 ? 'block' : 'none';

    if (filtered.length === 0) {
      speciesGrid.innerHTML = '';
      return;
    }

    let html = '';
    for (const s of filtered) {
      const displayTags = s.tags.slice(0, 4);
      const extra = s.tags.length > 4 ? `+${s.tags.length - 4}` : null;
      html += `<div class="species-card" data-id="${s.id}">
        <div class="species-name">${s.common_name}</div>
        <div class="species-sci">${s.scientific_name}</div>
        <div class="species-tags">
          ${displayTags.map(t => `<span class="tag-chip" style="font-size:.625rem;padding:1px 6px;pointer-events:none">${t}</span>`).join('')}
          ${extra ? `<span class="tag-chip" style="font-size:.625rem;padding:1px 6px;pointer-events:none;background:var(--slate-100);border-color:var(--slate-200)">${extra}</span>` : ''}
        </div>
        <div class="species-meta">
          <span class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            ${s.care.light}
          </span>
          <span class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
            ${s.care.water}
          </span>
        </div>
      </div>`;
    }
    speciesGrid.innerHTML = html;

    // Card click handlers
    speciesGrid.querySelectorAll('.species-card').forEach(card => {
      card.addEventListener('click', () => {
        const id = card.dataset.id;
        const plant = species.find(s => s.id === id);
        if (plant) showCareModal(plant);
      });
    });
  }

  // ===== Render Active Filters =====
  function renderActiveFilters() {
    if (activeTags.size === 0) {
      activeFilters.style.display = 'none';
      return;
    }
    activeFilters.style.display = 'flex';
    let html = '';
    for (const tag of activeTags) {
      html += `<span class="filter-chip" data-tag="${tag}">
        ${tag}
        <span class="chip-remove">×</span>
      </span>`;
    }
    filterChips.innerHTML = html;

    filterChips.querySelectorAll('.filter-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const tag = chip.dataset.tag;
        activeTags.delete(tag);
        render();
      });
    });
  }

  // ===== Render =====
  function render() {
    renderActiveFilters();
    renderSpecies();
    // Update tag chip active states
    tagSections.querySelectorAll('.tag-chip').forEach(btn => {
      btn.classList.toggle('active', activeTags.has(btn.dataset.tag));
    });
  }

  // ===== Care Card Modal =====
  function showCareModal(plant) {
    const c = plant.care;
    const issues = c.common_issues || [];
    const tips = c.tips || [];

    modalBody.innerHTML = `
      <div class="care-card-header">
        <h2>${plant.common_name}</h2>
        <div class="sci-name">${plant.scientific_name}</div>
      </div>
      ${c.summary ? `<div class="care-card-summary">${c.summary}</div>` : ''}
      <div class="care-grid">
        <div class="care-item">
          <div class="care-item-label">💡 Light</div>
          <div class="care-item-value">${c.light}</div>
        </div>
        <div class="care-item">
          <div class="care-item-label">💧 Water</div>
          <div class="care-item-value">${c.water}</div>
        </div>
        <div class="care-item">
          <div class="care-item-label">🌱 Soil</div>
          <div class="care-item-value">${c.soil}</div>
        </div>
        <div class="care-item">
          <div class="care-item-label">💨 Humidity</div>
          <div class="care-item-value">${c.humidity}</div>
        </div>
        <div class="care-item">
          <div class="care-item-label">🌡️ Temperature</div>
          <div class="care-item-value">${c.temperature_c}°C</div>
        </div>
        <div class="care-item">
          <div class="care-item-label">🧪 Fertilizer</div>
          <div class="care-item-value">${c.fertilizer}</div>
        </div>
      </div>
      ${c.toxicity ? `<div class="care-section"><div class="care-section-title">⚠️ Toxicity</div><div class="care-item-value">${c.toxicity}</div></div>` : ''}
      ${issues.length > 0 ? `<div class="care-section"><div class="care-section-title">Common Issues</div><ul class="care-issues">${issues.map(i => `<li>${i}</li>`).join('')}</ul></div>` : ''}
      ${tips.length > 0 ? `<div class="care-section"><div class="care-section-title">💡 Tips</div><ul class="care-tips">${tips.map(t => `<li>${t}</li>`).join('')}</ul></div>` : ''}
    `;
    careModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  function hideCareModal() {
    careModal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Modal close handlers
  modalClose.addEventListener('click', hideCareModal);
  careModal.addEventListener('click', (e) => {
    if (e.target === careModal) hideCareModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && careModal.style.display !== 'none') hideCareModal();
  });

  // ===== Clear Handlers =====
  clearTags.addEventListener('click', () => {
    activeTags.clear();
    render();
  });

  clearAllFilters.addEventListener('click', () => {
    activeTags.clear();
    searchQuery = '';
    searchInput.value = '';
    render();
  });

  // ===== Search =====
  searchInput.addEventListener('input', () => {
    searchQuery = searchInput.value;
    render();
  });

  // ===== Mobile sidebar toggle =====
  const sidebarHeader = document.querySelector('.sidebar-header');
  if (window.innerWidth <= 768) {
    sidebarHeader.addEventListener('click', () => {
      tagSections.classList.toggle('open');
    });
  }

  // ===== Init =====
  renderTagSections();
  render();
  console.log(`🌿 PlantGuide Web UI loaded — ${species.length} species, ${all_tags.length} tags`);
})();