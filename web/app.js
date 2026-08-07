/* PlantGuide — Tag Picker + Care Card UI */

(async function () {
  // --- State ---
  let species = [];
  let allTags = [];
  let selectedTags = new Set();

  // --- DOM refs ---
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  const tagCloud = $('#tag-cloud');
  const tagSearch = $('#tag-search');
  const tagCount = $('#tag-count');
  const matchInfo = $('#match-info');
  const speciesList = $('#species-list');
  const resultCount = $('#result-count');
  const speciesTotal = $('#species-total');
  const clearBtn = $('#clear-tags');
  const showAllBtn = $('#show-all-btn');
  const careModal = $('#care-modal');
  const careContent = $('#care-card-content');
  const closeModal = $('#close-modal');
  const modalBackdrop = $('.modal-backdrop');

  // --- Load data ---
  async function loadData() {
    try {
      const resp = await fetch('data/species.min.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json = await resp.json();
      species = json.species || [];
      allTags = json.tags || [];
    } catch {
      // Fallback to non-minified
      const resp = await fetch('data/species.json');
      const json = await resp.json();
      species = json.species || [];
      allTags = json.tags || [];
    }
    speciesTotal.textContent = species.length;
  }

  // --- Render tag cloud ---
  function renderTags() {
    const query = tagSearch.value.toLowerCase().trim();
    tagCloud.innerHTML = '';

    for (const tag of allTags) {
      const chip = document.createElement('span');
      chip.className = 'tag-chip';
      if (selectedTags.has(tag)) chip.classList.add('selected');
      chip.textContent = tag;
      chip.title = tag;

      if (query && !tag.includes(query)) chip.classList.add('hidden');

      chip.addEventListener('click', () => toggleTag(tag));
      tagCloud.appendChild(chip);
    }

    tagCount.textContent = `${selectedTags.size} selected`;
  }

  function toggleTag(tag) {
    if (selectedTags.has(tag)) selectedTags.delete(tag);
    else selectedTags.add(tag);
    renderTags();
    renderResults();
  }

  // --- Match + render species ---
  function matchScore(sp) {
    if (selectedTags.size === 0) return 0;
    const plantTags = new Set(sp.tags.map(t => t.toLowerCase().trim()));
    let hits = 0;
    for (const t of selectedTags) if (plantTags.has(t)) hits++;
    return hits;
  }

  function renderResults() {
    const scored = species.map(sp => ({ ...sp, score: matchScore(sp) }));

    let filtered;
    if (selectedTags.size === 0) {
      filtered = scored; // show all when no tags selected
    } else {
      filtered = scored.filter(s => s.score > 0).sort((a, b) => b.score - a.score);
    }

    resultCount.textContent = filtered.length;
    matchInfo.textContent = selectedTags.size === 0
      ? 'Select tags above to filter species'
      : `${filtered.length} species match your tags`;

    if (filtered.length === 0) {
      speciesList.innerHTML = `
        <div class="empty-state">
          <div class="icon">🔎</div>
          <p>No species match the selected tags.</p>
          <p style="font-size:.85rem">Try different tags or clear your selection.</p>
        </div>`;
      return;
    }

    speciesList.innerHTML = filtered.map(sp => {
      const tagsHtml = sp.tags.slice(0, 6).map(t =>
        `<span>${escHtml(t)}</span>`
      ).join('');

      const scoreHtml = sp.score > 0
        ? `<div class="match-score">${sp.score}/${selectedTags.size} tags match</div>`
        : '';

      return `
        <div class="species-card" data-id="${escHtml(sp.id)}" onclick="window._openCareCard('${escHtml(sp.id)}')">
          ${scoreHtml}
          <h3>${escHtml(sp.common_name)}</h3>
          <div class="sci-name">${escHtml(sp.scientific_name)}</div>
          <div class="card-summary">${escHtml(sp.care.summary || '')}</div>
          <div class="card-tags">${tagsHtml}</div>
        </div>`;
    }).join('');
  }

  // --- Care card modal ---
  function openCareCard(id) {
    const sp = species.find(s => s.id === id);
    if (!sp) return;

    const c = sp.care;
    const tagsHtml = sp.tags.map(t => `<span>${escHtml(t)}</span>`).join('');
    const issuesHtml = (c.common_issues || []).map(i => `<li>${escHtml(i)}</li>`).join('');
    const tipsHtml = (c.tips || []).map(t => `<li>${escHtml(t)}</li>`).join('');

    careContent.innerHTML = `
      <div class="care-card">
        <h2>${escHtml(sp.common_name)}</h2>
        <div class="sci">${escHtml(sp.scientific_name)}</div>
        <div class="summary">${escHtml(c.summary || '')}</div>
        <div class="care-grid">
          <div class="care-item"><label>☀️ Light</label><span>${escHtml(c.light || '—')}</span></div>
          <div class="care-item"><label>💧 Water</label><span>${escHtml(c.water || '—')}</span></div>
          <div class="care-item"><label>🌱 Soil</label><span>${escHtml(c.soil || '—')}</span></div>
          <div class="care-item"><label>💨 Humidity</label><span>${escHtml(c.humidity || '—')}</span></div>
          <div class="care-item"><label>🌡️ Temp</label><span>${escHtml(c.temperature_c || '—')}°C</span></div>
          <div class="care-item"><label>🧪 Fertilizer</label><span>${escHtml(c.fertilizer || '—')}</span></div>
          <div class="care-item full"><label>⚠️ Toxicity</label><span>${escHtml(c.toxicity || '—')}</span></div>
        </div>
        <div class="care-tags">${tagsHtml}</div>
        ${issuesHtml ? `<div class="care-section"><h3>⚠️ Common Issues</h3><ul>${issuesHtml}</ul></div>` : ''}
        ${tipsHtml ? `<div class="care-section"><h3>💡 Tips</h3><ul>${tipsHtml}</ul></div>` : ''}
      </div>`;

    careModal.classList.remove('hidden');
  }

  function closeCareCard() {
    careModal.classList.add('hidden');
  }

  // Expose for onclick in injected HTML
  window._openCareCard = openCareCard;

  // --- Helpers ---
  function escHtml(s) {
    if (!s) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // --- Event listeners ---
  tagSearch.addEventListener('input', renderTags);
  clearBtn.addEventListener('click', () => {
    selectedTags.clear();
    tagSearch.value = '';
    renderTags();
    renderResults();
  });
  showAllBtn.addEventListener('click', () => {
    selectedTags.clear();
    tagSearch.value = '';
    renderTags();
    renderResults();
    document.querySelector('#results-section')?.scrollIntoView({ behavior: 'smooth' });
  });
  closeModal.addEventListener('click', closeCareCard);
  modalBackdrop.addEventListener('click', closeCareCard);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeCareCard();
  });

  // --- Init ---
  await loadData();
  renderTags();
  renderResults();
})();
