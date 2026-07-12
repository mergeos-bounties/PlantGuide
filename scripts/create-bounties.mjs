import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = 'mergeos-bounties/PlantGuide';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureLabel(name, color, description) {
  try {
    sh(
      `gh label create ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
    );
  } catch {
    try {
      sh(
        `gh label edit ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
      );
    } catch {
      // ignore
    }
  }
}

function createIssue(title, body, labels) {
  const dir = mkdtempSync(join(tmpdir(), 'plantguide-issue-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    const labelFlags = labels.map((l) => `--label ${JSON.stringify(l)}`).join(' ');
    const out = sh(
      `gh issue create --repo ${REPO} --title ${JSON.stringify(title)} --body-file ${JSON.stringify(file)} ${labelFlags}`,
    );
    console.log(out);
    return out;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const labels = [
  ['bounty', '5319E7', 'Eligible for MergeOS MRG bounty'],
  ['bounty: feature', 'A2EEEF', 'Feature bounty'],
  ['bounty: bug', 'D73A4A', 'Bug bounty'],
  ['ml', 'B60205', 'Models / identification'],
  ['data', 'C5DEF5', 'Species catalog / samples'],
  ['vision', 'D93F0B', 'Image / vision models'],
  ['care', '0E8A16', 'Care schedules / tips'],
  ['api', '1D76DB', 'HTTP / SDK for apps'],
  ['reward:25-mrg', 'FEF2C0', 'Target 25 MRG'],
  ['reward:50-mrg', 'FEF2C0', 'Target 50 MRG'],
  ['reward:100-mrg', 'FEF2C0', 'Target 100 MRG'],
  ['reward:200-mrg', 'FEF2C0', 'Target 200 MRG'],
  ['good first issue', '7057FF', 'Good for newcomers'],
  ['documentation', '0075CA', 'Documentation improvements'],
];

for (const [name, color, description] of labels) {
  ensureLabel(name, color, description);
}

const footer = `

## Claim (MergeOS MRG)

1. Star https://github.com/mergeos-bounties/PlantGuide and https://github.com/mergeos-bounties/mergeos  
2. Comment on **this issue**: \`I claim this bounty\`  
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to this issue  
4. Open a PR to **PlantGuide** (public product repo) with \`Fixes #<this-issue>\`

Policy: [docs/BOUNTY.md](../blob/master/docs/BOUNTY.md)

## Important

Work lands on **https://github.com/mergeos-bounties/PlantGuide**.

## Payout

Maintainer reviews PR → merge on PlantGuide → **MRG credit** on MergeOS ledger to \`github:<author>\` (25/50/100/200 scale).
`;

const issues = [
  {
    title: '[25 MRG] Docs: SPECIES.md catalog overview + how to add a plant',
    labels: ['bounty', 'bounty: feature', 'documentation', 'data', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nDocument catalog fields, care schema, and contribution checklist for new species JSON.\n\n## Acceptance\n\n- [ ] docs/SPECIES.md + README link\n${footer}`,
  },
  {
    title: '[25 MRG] Expand houseplant catalog to 30+ species with care cards',
    labels: ['bounty', 'bounty: feature', 'data', 'care', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nAdd more species under data/species/ with tags + full care objects.\n\n## Acceptance\n\n- [ ] ≥30 species total\n- [ ] plantguide species list works\n- [ ] No copyrighted long-form text copied wholesale\n${footer}`,
  },
  {
    title: '[25 MRG] CLI: plantguide identify batch — score all samples to report',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nAdd plantguide identify batch --out data/out/batch.json summarizing top1 hits.\n\n## Acceptance\n\n- [ ] Command + tests + README\n${footer}`,
  },
  {
    title: '[25 MRG] Pydantic schema validation for species and samples',
    labels: ['bounty', 'bounty: feature', 'data', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nValidate species/sample JSON with pydantic; clear errors for missing care fields.\n\n## Acceptance\n\n- [ ] Good/bad fixture tests\n${footer}`,
  },
  {
    title: '[50 MRG] Vision stub: extract color/edge tags from leaf photo (optional vision extra)',
    labels: ['bounty', 'bounty: feature', 'vision', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nOptional Pillow/OpenCV path: image → coarse trait tags → identify pipeline. Graceful if vision extra missing.\n\n## Acceptance\n\n- [ ] CLI plantguide identify image --file ...\n- [ ] CI green without vision deps\n- [ ] No large private photos committed\n${footer}`,
  },
  {
    title: '[50 MRG] Disease/pest symptom matcher',
    labels: ['bounty', 'bounty: feature', 'ml', 'care', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nGiven symptom tags (yellow spots, sticky leaves), suggest likely issues + remedies with disclaimers.\n\n## Acceptance\n\n- [ ] Module + fixtures + tests\n- [ ] Linked from care show optionally\n${footer}`,
  },
  {
    title: '[50 MRG] Watering schedule calculator by pot size / season / climate',
    labels: ['bounty', 'bounty: feature', 'care', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nExpand watering_hint into a schedule with next-check dates (offline heuristic).\n\n## Acceptance\n\n- [ ] CLI + unit tests\n- [ ] Document assumptions\n${footer}`,
  },
  {
    title: '[50 MRG] Vietnamese care tip localization pack',
    labels: ['bounty', 'bounty: feature', 'care', 'documentation', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nAdd --lang vi care text for catalog species (or locale files).\n\n## Acceptance\n\n- [ ] ≥10 species localized\n- [ ] Fallback to EN\n${footer}`,
  },
  {
    title: '[50 MRG] FastAPI: POST /identify and GET /species/{id}/care',
    labels: ['bounty', 'bounty: feature', 'api', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nOptional FastAPI under src/plantguide/api/ for plant apps.\n\n## Acceptance\n\n- [ ] Documented uvicorn entry\n- [ ] TestClient tests\n${footer}`,
  },
  {
    title: '[50 MRG] App SDK: JSON Schema + TypeScript types for identify/care',
    labels: ['bounty', 'bounty: feature', 'api', 'documentation', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nPublish schemas/ and optional sdk/typescript contracts.\n\n## Acceptance\n\n- [ ] Schema matches Python payload\n- [ ] README integration section\n${footer}`,
  },
  {
    title: '[50 MRG] Ranking model beyond Jaccard (embeddings or weighted tags)',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nImprove ToyPlantIdentifier with trainable or weighted features; keep toy fallback.\n\n## Acceptance\n\n- [ ] Train/save/load path or config weights\n- [ ] Tests offline\n${footer}`,
  },
  {
    title: '[50 MRG] Dataset index: public plant/leaf datasets with licenses',
    labels: ['bounty', 'bounty: feature', 'data', 'documentation', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\ndocs/DATASETS.md with ≥8 corpora (PlantNet, iNaturalist subsets notes, etc.) — no redistributing restricted media.\n\n## Acceptance\n\n- [ ] License + link per row\n${footer}`,
  },
  {
    title: '[100 MRG] Photo ID baseline with optional torch (leaf crops)',
    labels: ['bounty', 'bounty: feature', 'vision', 'ml', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG\n\nOptional torch baseline for species classification on a tiny licensed subset or synthetic features; CPU tests skip if torch missing.\n\n## Acceptance\n\n- [ ] Train/infer scripts\n- [ ] Docs + license notes\n${footer}`,
  },
  {
    title: '[100 MRG] Care planner: fertilize + repot calendar export JSON/ICS',
    labels: ['bounty', 'bounty: feature', 'care', 'api', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG\n\nGenerate multi-month care calendar for a species collection.\n\n## Acceptance\n\n- [ ] CLI export\n- [ ] Tests for schedule rules\n${footer}`,
  },
  {
    title: '[100 MRG] Web demo: tag picker + care card UI',
    labels: ['bounty', 'bounty: feature', 'api', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG\n\nLightweight web/ under web/ for identify + care display.\n\n## Acceptance\n\n- [ ] Local README\n- [ ] Screenshots in PR\n${footer}`,
  },
  {
    title: '[100 MRG] Multi-species collection manager (user plant list + reminders stub)',
    labels: ['bounty', 'bounty: feature', 'care', 'api', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG\n\nLocal JSON store for a user plant collection with last-watered dates and due reminders.\n\n## Acceptance\n\n- [ ] CLI add/list/due\n- [ ] Tests\n${footer}`,
  },
  {
    title: '[200 MRG] End-to-end product path: photo/tags → ID → care plan for apps',
    labels: ['bounty', 'bounty: feature', 'vision', 'ml', 'care', 'api', 'reward:200-mrg'],
    body: `## Bounty: 200 MRG\n\nPolished E2E command/API path suitable for embedding in a plant app with sample evidence.\n\n## Acceptance\n\n- [ ] Single documented path\n- [ ] Evidence logs + sample care report\n- [ ] License-safe assets only\n${footer}`,
  },
  {
    title: '[25 MRG] CONTRIBUTING.md + good-first-issue path',
    labels: ['bounty', 'bounty: feature', 'documentation', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nWrite CONTRIBUTING with setup, tests, claim flow.\n\n## Acceptance\n\n- [ ] File + README link\n${footer}`,
  },
  {
    title: '[25 MRG] CI: coverage + ruff format check',
    labels: ['bounty', 'bounty: feature', 'documentation', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG\n\nImprove CI with pytest-cov and ruff format --check.\n\n## Acceptance\n\n- [ ] CI green\n${footer}`,
  },
  {
    title: '[50 MRG] Toxicity and pet-safety flag pack across catalog',
    labels: ['bounty', 'bounty: feature', 'care', 'data', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nNormalize toxicity fields + CLI filter plantguide species list --pet-safe.\n\n## Acceptance\n\n- [ ] Schema + tests + disclaimers\n${footer}`,
  },
  {
    title: '[50 MRG] Metrics: top-k accuracy, confusion between similar species',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nEval module + plantguide eval report for labeled samples.\n\n## Acceptance\n\n- [ ] hit@k helpers + tests\n${footer}`,
  },
  {
    title: '[50 MRG] Outdoor/vegetable pack: tomato, chili, mint care profiles',
    labels: ['bounty', 'bounty: feature', 'data', 'care', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG\n\nAdd outdoor edible plants with climate notes for tropical/subtropical care.\n\n## Acceptance\n\n- [ ] ≥8 new outdoor species + samples\n${footer}`,
  },
];

for (const issue of issues) {
  createIssue(issue.title, issue.body, issue.labels);
}
console.log(`Created ${issues.length} issues on ${REPO}`);
