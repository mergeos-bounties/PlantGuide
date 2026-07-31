/* ============================================
   PlantGuide — Symptom Checker Logic
   ============================================ */

// --- Care Card Database ---
// Each entry maps a plant disease/condition to symptoms (tags),
// severity, treatment, and prevention advice.
const plantConditions = [
  {
    id: "powdery-mildew",
    name: "Powdery Mildew",
    icon: "🌫️",
    severity: "medium",
    symptoms: ["white powder", "powdery mildew", "leaf distortion"],
    treatment:
      "Apply a fungicide containing potassium bicarbonate or sulfur. For mild cases, mix 1 tsp baking soda + 1/2 tsp liquid soap in 1L water and spray on affected leaves every 3–5 days. Remove severely infected leaves.",
    prevention:
      "Ensure good air circulation around plants. Avoid overhead watering. Plant resistant varieties. Thin out dense foliage to reduce humidity around leaves."
  },
  {
    id: "yellowing-leaves",
    name: "Chlorosis (Yellowing Leaves)",
    icon: "🍂",
    severity: "medium",
    symptoms: ["yellowing", "yellowing leaves", "pale leaves"],
    treatment:
      "Test soil pH — iron becomes unavailable above pH 7.0. Apply chelated iron foliar spray for quick correction. For nitrogen deficiency, apply a balanced 10-10-10 fertilizer. Water consistently; overwatering also causes yellowing.",
    prevention:
      "Maintain soil pH between 6.0–6.5 for most plants. Use slow-release balanced fertilizer. Water only when top 2–3 cm of soil is dry. Mulch to retain moisture."
  },
  {
    id: "brown-spots",
    name: "Leaf Spot Disease",
    icon: "🟤",
    severity: "medium",
    symptoms: ["brown spots", "spots", "leaf spots"],
    treatment:
      "Remove and destroy affected leaves immediately. Apply copper-based fungicide or neem oil spray every 7–10 days. Avoid wetting foliage when watering. Improve air circulation.",
    prevention:
      "Water at the base of plants, not on leaves. Space plants adequately. Clean up fallen leaves and debris. Rotate susceptible crops annually."
  },
  {
    id: "wilting",
    name: "Wilting / Vascular Wilt",
    icon: "🥀",
    severity: "high",
    symptoms: ["wilting", "drooping", "limp leaves"],
    treatment:
      "Check soil moisture: if dry, deep-water immediately. If wet and wilting, root rot may be present — stop watering and improve drainage. For bacterial wilt, remove and destroy infected plants; there is no chemical cure.",
    prevention:
      "Use well-draining soil. Water consistently, not sporadically. Avoid compacted soil. Choose disease-resistant varieties. Sterilize tools between plants."
  },
  {
    id: "root-rot",
    name: "Root Rot",
    icon: "🪴",
    severity: "high",
    symptoms: ["wilting", "root rot", "yellowing", "mushy stems"],
    treatment:
      "Remove plant from pot, trim away all dark, mushy roots with sterilized scissors. Repot in fresh, well-draining soil. Apply a fungicide drench (thiophanate-methyl). Reduce watering frequency significantly.",
    prevention:
      "Use pots with drainage holes. Never let plants sit in standing water. Use well-aerated potting mix with perlite. Allow soil to dry between waterings."
  },
  {
    id: "pest-damage",
    name: "Pest Infestation",
    icon: "🐛",
    severity: "medium",
    symptoms: ["pest damage", "holes in leaves", "sticky residue", "visible insects"],
    treatment:
      "Identify the pest (aphids, spider mites, mealybugs, etc.). Spray with insecticidal soap or neem oil solution every 5–7 days. For heavy infestations, use horticultural oil or pyrethrin-based insecticide. Wipe leaves with damp cloth.",
    prevention:
      "Inspect new plants before introducing them. Encourage beneficial insects (ladybugs, lacewings). Keep plants healthy — stressed plants attract pests. Use sticky traps for monitoring."
  },
  {
    id: "stunted-growth",
    name: "Stunted Growth",
    icon: "🌱",
    severity: "medium",
    symptoms: ["stunted growth", "small leaves", "slow growth"],
    treatment:
      "Test for nutrient deficiencies — phosphorus deficiency is a common cause. Apply a complete fertilizer with micronutrients. Check for root-bound conditions — repot if roots circle the container. Ensure adequate light (12–16 hours for most plants).",
    prevention:
      "Fertilize regularly during growing season. Repot every 1–2 years. Provide appropriate light levels for the species. Maintain consistent temperatures."
  },
  {
    id: "sunscald",
    name: "Sunscald / Leaf Burn",
    icon: "☀️",
    severity: "low",
    symptoms: ["brown spots", "scorched leaves", "bleached leaves", "crispy edges"],
    treatment:
      "Move plant to a location with indirect light. Trim severely damaged leaves. Water adequately to help recovery — burned leaves lose more water. Apply a dilute seaweed extract to support new growth.",
    prevention:
      "Gradually acclimate plants to direct sunlight over 7–10 days. Use shade cloth for sensitive plants during peak sun hours. Water early morning to reduce leaf burn risk."
  },
  {
    id: "nutrient-burn",
    name: "Nutrient Burn / Over-fertilization",
    icon: "⚡",
    severity: "medium",
    symptoms: ["brown spots", "yellowing", "crispy edges", "white crust on soil"],
    treatment:
      "Flush the soil thoroughly with clean water — run water through the pot for 2–3 minutes, allowing it to drain completely. Stop fertilizing for 4–6 weeks. Trim damaged leaves.",
    prevention:
      "Follow label instructions for fertilizer — more is not better. Use half-strength for sensitive plants. Flush soil every 2–3 months to prevent salt buildup."
  },
  {
    id: "overwatering",
    name: "Overwatering / Edema",
    icon: "💧",
    severity: "medium",
    symptoms: ["yellowing", "wilting", "mushy stems", "mold on soil"],
    treatment:
      "Stop watering immediately. If soil is soggy, repot into dry, fresh mix. Remove affected leaves. Increase light and airflow to speed drying. Resume watering only when top 3–5 cm of soil is bone dry.",
    prevention:
      "Use the finger test before watering. Ensure pots have drainage holes. Choose pots appropriate for plant size — oversized pots retain excess moisture. Water less in winter/dormant periods."
  }
];

// --- Symptom Tags (visible to the user) ---
const symptomTags = [
  { id: "yellowing", label: "Yellowing Leaves", icon: "🍂" },
  { id: "brown-spots", label: "Brown Spots", icon: "🟤" },
  { id: "wilting", label: "Wilting / Drooping", icon: "🥀" },
  { id: "root-rot", label: "Root Rot", icon: "🪴" },
  { id: "powdery-mildew", label: "Powdery Mildew", icon: "🌫️" },
  { id: "pest-damage", label: "Pest Damage", icon: "🐛" },
  { id: "stunted-growth", label: "Stunted Growth", icon: "🌱" },
  { id: "crispy-edges", label: "Crispy Edges", icon: "🔥" },
  { id: "mushy-stems", label: "Mushy Stems", icon: "🧽" },
  { id: "mold-on-soil", label: "Mold on Soil", icon: "🦠" },
  { id: "holes-in-leaves", label: "Holes in Leaves", icon: "🕳️" },
  { id: "white-powder", label: "White Powder", icon: "❄️" },
];

// --- State ---
let selectedTags = new Set();

// --- DOM References ---
const tagContainer = document.getElementById("tag-container");
const clearBtn = document.getElementById("clear-btn");
const diagnoseBtn = document.getElementById("diagnose-btn");
const resultsSection = document.getElementById("results-section");
const careCardsContainer = document.getElementById("care-cards-container");
const noResults = document.getElementById("no-results");

// --- Render Tags ---
function renderTags() {
  tagContainer.innerHTML = "";

  symptomTags.forEach((tag) => {
    const el = document.createElement("span");
    el.className = "tag" + (selectedTags.has(tag.id) ? " selected" : "");
    el.dataset.tagId = tag.id;
    el.innerHTML = `<span class="tag-icon">${tag.icon}</span>${tag.label}`;
    el.addEventListener("click", () => toggleTag(tag.id));
    tagContainer.appendChild(el);
  });

  updateButtonStates();
}

// --- Toggle Tag ---
function toggleTag(tagId) {
  if (selectedTags.has(tagId)) {
    selectedTags.delete(tagId);
  } else {
    selectedTags.add(tagId);
  }
  renderTags();
}

// --- Update Button States ---
function updateButtonStates() {
  diagnoseBtn.disabled = selectedTags.size === 0;
}

// --- Clear All ---
function clearAll() {
  selectedTags.clear();
  renderTags();
  resultsSection.style.display = "none";
}

// --- Diagnose: Match selected tags to plant conditions ---
function diagnose() {
  if (selectedTags.size === 0) return;

  const selectedArray = Array.from(selectedTags);

  // Score each condition by how many selected tags match its symptoms
  const scored = plantConditions.map((condition) => {
    let matchCount = 0;
    condition.symptoms.forEach((symptom) => {
      selectedArray.forEach((tagId) => {
        // Match tag id against symptom strings (case-insensitive, partial)
        if (
          symptom.toLowerCase().includes(tagId) ||
          tagId.includes(symptom.toLowerCase()) ||
          fuzzyMatch(tagId, symptom)
        ) {
          matchCount++;
        }
      });
    });
    return { condition, matchCount };
  });

  // Filter to conditions with at least 1 match, sort by match count desc
  const matches = scored
    .filter((s) => s.matchCount > 0)
    .sort((a, b) => b.matchCount - a.matchCount);

  renderResults(matches);
}

// --- Fuzzy matching helper ---
function fuzzyMatch(tagId, symptom) {
  const t = tagId.toLowerCase().replace(/[^a-z]/g, "");
  const s = symptom.toLowerCase().replace(/[^a-z]/g, "");
  return t.includes(s) || s.includes(t);
}

// --- Render Care Cards ---
function renderResults(matches) {
  resultsSection.style.display = "block";
  careCardsContainer.innerHTML = "";
  noResults.style.display = "none";

  if (matches.length === 0) {
    noResults.style.display = "block";
    return;
  }

  matches.forEach(({ condition, matchCount }) => {
    const card = createCareCard(condition, matchCount);
    careCardsContainer.appendChild(card);
  });

  // Smooth scroll to results
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- Create a single Care Card ---
function createCareCard(condition, matchCount) {
  const severityClass =
    condition.severity === "high"
      ? "severity-high"
      : condition.severity === "medium"
        ? "severity-medium"
        : "";

  const badgeClass =
    condition.severity === "high"
      ? "badge-high"
      : condition.severity === "medium"
        ? "badge-medium"
        : "badge-low";

  const severityLabel =
    condition.severity.charAt(0).toUpperCase() + condition.severity.slice(1);

  const card = document.createElement("div");
  card.className = `care-card ${severityClass}`;

  // Build symptom tags, highlighting matched ones
  const selectedArray = Array.from(selectedTags);
  const symptomTagsHtml = condition.symptoms
    .map((s) => {
      const isMatched = selectedArray.some(
        (tagId) =>
          s.toLowerCase().includes(tagId) ||
          tagId.includes(s.toLowerCase()) ||
          fuzzyMatch(tagId, s)
      );
      return `<span class="symptom-tag${isMatched ? " matched" : ""}">${s}</span>`;
    })
    .join("");

  card.innerHTML = `
    <div class="care-card-header">
      <span class="care-card-icon">${condition.icon}</span>
      <div>
        <div class="care-card-title">${condition.name}</div>
        <span class="care-card-badge ${badgeClass}">${severityLabel} severity · ${matchCount} match${matchCount > 1 ? "es" : ""}</span>
      </div>
    </div>
    <div class="care-card-symptoms">
      <h4>Symptoms</h4>
      <div class="symptom-tags">${symptomTagsHtml}</div>
    </div>
    <div class="care-card-treatment">
      <h4>Treatment</h4>
      <p>${condition.treatment}</p>
    </div>
    <div class="care-card-prevention">
      <h4>Prevention</h4>
      <p>${condition.prevention}</p>
    </div>
  `;

  return card;
}

// --- Event Listeners ---
clearBtn.addEventListener("click", clearAll);
diagnoseBtn.addEventListener("click", diagnose);

// --- Initialize ---
renderTags();
