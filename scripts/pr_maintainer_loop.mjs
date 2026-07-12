/**
 * PlantGuide PR maintainer loop (species packs + general PRs).
 *
 *   node scripts/pr_maintainer_loop.mjs
 *   node scripts/pr_maintainer_loop.mjs --dry-run
 *   node scripts/pr_maintainer_loop.mjs --repo=mergeos-bounties/PlantGuide
 */
import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const repoArg = args.find((a) => a.startsWith('--repo='));
const REPO = repoArg ? repoArg.split('=')[1] : 'mergeos-bounties/PlantGuide';
const TWO_HOURS_MS = 2 * 60 * 60 * 1000;
const GUIDE = 'https://github.com/mergeos-bounties/PlantGuide/blob/master/docs/guides/README.md';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function shJson(cmd) {
  const out = sh(cmd);
  return out ? JSON.parse(out) : null;
}

function commentPr(number, body) {
  const dir = mkdtempSync(join(tmpdir(), 'pg-pr-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    if (dryRun) {
      console.log(`[dry-run] comment #${number}\n${body.slice(0, 240)}...\n`);
      return;
    }
    sh(`gh pr comment ${number} --repo ${REPO} --body-file ${JSON.stringify(file)}`);
    console.log(`commented #${number}`);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function listComments(number) {
  try {
    const raw = shJson(`gh api repos/${REPO}/issues/${number}/comments`);
    return (raw || []).map((c) => ({
      login: c.user?.login,
      createdAt: c.created_at,
      body: c.body || '',
    }));
  } catch {
    return [];
  }
}

function canPingAuthor(comments, authorLogin) {
  const now = Date.now();
  let latest = 0;
  for (const c of comments) {
    if (c.body.includes(`@${authorLogin}`)) {
      const t = Date.parse(c.createdAt);
      if (!Number.isNaN(t) && t > latest) latest = t;
    }
  }
  if (!latest) return true;
  return now - latest >= TWO_HOURS_MS;
}

function hasPhotoEvidence(body, files) {
  const b = body || '';
  if (/user-images\.githubusercontent\.com|github\.com\/user-attachments\//i.test(b)) return true;
  if (/!\[[^\]]*\]\(https?:\/\//i.test(b)) return true;
  return (files || []).some(
    (f) =>
      /^docs\/species-photos\//i.test(f.path) && /\.(png|jpe?g|webp|gif)$/i.test(f.path),
  );
}

function isSpeciesPackPr(title, files) {
  if (/species|species-pack|auto-patch for issue/i.test(title || '')) return true;
  return (files || []).some((f) => f.path.startsWith('data/species/') && f.path.endsWith('.json'));
}

function hasSpeciesAndSample(files) {
  const paths = (files || []).map((f) => f.path);
  return (
    paths.some((p) => p.startsWith('data/species/') && p.endsWith('.json')) &&
    paths.some((p) => p.startsWith('data/samples/') && p.endsWith('.json'))
  );
}

function main() {
  console.log(`=== PR loop ${REPO} dryRun=${dryRun} utc=${new Date().toISOString()} ===`);
  const prs = shJson(
    `gh pr list --repo ${REPO} --state open --base master --limit 50 --json number,title,author,isDraft,mergeable,mergeStateStatus,url,body,files,headRefOid,updatedAt`,
  );
  if (!prs?.length) {
    console.log('No open PRs');
    console.log(JSON.stringify({ scanned: 0, pinged: [], waiting: [], merged: [] }, null, 2));
    return;
  }

  const summary = { scanned: prs.length, pinged: [], waiting: [], merged: [], notes: [] };

  for (const pr of prs) {
    const n = pr.number;
    const login = pr.author?.login || 'unknown';
    const comments = listComments(n);
    const pingOk = canPingAuthor(comments, login);
    const speciesPack = isSpeciesPackPr(pr.title, pr.files);
    const filesOk = !speciesPack || hasSpeciesAndSample(pr.files);
    const photosOk = !speciesPack || hasPhotoEvidence(pr.body, pr.files);
    const conflicting = pr.mergeable === 'CONFLICTING' || pr.mergeStateStatus === 'DIRTY';
    const failCi = pr.mergeStateStatus === 'FAILURE';

    console.log(
      `#${n} @${login} mergeable=${pr.mergeable} state=${pr.mergeStateStatus} species=${speciesPack} filesOk=${filesOk} photos=${photosOk}`,
    );

    if (pr.isDraft) {
      summary.waiting.push(n);
      summary.notes.push(`#${n} draft`);
      continue;
    }

    if (!pr.files?.length) {
      if (pingOk) {
        commentPr(n, `@${login} this PR has **no file changes**. Push commits or close it.\n\nGuides: ${GUIDE}`);
        summary.pinged.push(n);
      } else summary.waiting.push(n);
      continue;
    }

    if (conflicting) {
      if (pingOk) {
        commentPr(
          n,
          `@${login} PR is **CONFLICTING** against \`master\`.

Please rebase:
\`\`\`bash
git fetch origin
git rebase origin/master
# fix conflicts, then:
git push --force-with-lease
\`\`\`

Guides (all languages): ${GUIDE}`,
        );
        summary.pinged.push(n);
      } else summary.waiting.push(n);
      continue;
    }

    if (failCi) {
      if (pingOk) {
        commentPr(
          n,
          `@${login} **CI is failing**. Fix \`ruff\` / \`pytest\`, push again.

Guides: ${GUIDE}`,
        );
        summary.pinged.push(n);
      } else summary.waiting.push(n);
      continue;
    }

    if (speciesPack && !filesOk) {
      if (pingOk) {
        commentPr(
          n,
          `@${login} species-pack needs **both** \`data/species/<id>.json\` and \`data/samples/obs_<id>.json\`.

Guides: ${GUIDE}`,
        );
        summary.pinged.push(n);
      } else summary.waiting.push(n);
      continue;
    }

    if (speciesPack && !photosOk) {
      if (pingOk) {
        commentPr(
          n,
          `@${login} **photo evidence required** for species packs.

Please add to the PR description (≥2 original photos: whole plant + close-up), or commit under \`docs/species-photos/<id>/\`.

No unlicensed web images. Multilingual guides: ${GUIDE}

Leaving open until evidence is attached.`,
        );
        summary.pinged.push(n);
      } else summary.waiting.push(n);
      continue;
    }

    // Ready path: species with photos + mergeable — still careful with UNSTABLE (no CI)
    if (pr.mergeable === 'MERGEABLE' && filesOk && photosOk) {
      // Prefer CI green; if UNSTABLE only due to missing checks on first contrib, still require photos (already ok)
      if (pr.mergeStateStatus === 'UNSTABLE' || pr.mergeStateStatus === 'BLOCKED') {
        if (pingOk) {
          commentPr(
            n,
            `@${login} almost ready: status is \`${pr.mergeStateStatus}\`. Please ensure **CI checks** complete successfully (re-run if needed). Photos look present — thanks!

Guides: ${GUIDE}`,
          );
          summary.pinged.push(n);
        } else summary.waiting.push(n);
        continue;
      }
      if (pr.mergeStateStatus === 'CLEAN' || pr.mergeStateStatus === 'HAS_HOOKS' || pr.mergeStateStatus === 'UNSTABLE') {
        // Only auto-merge CLEAN; UNSTABLE already handled
      }
      if (pr.mergeStateStatus === 'CLEAN') {
        if (!dryRun) {
          sh(`gh pr merge ${n} --repo ${REPO} --squash --admin`);
          commentPr(
            n,
            `## Merged\n\nThanks @${login} — squash-merged to \`master\`.\n\nGuides: ${GUIDE}`,
          );
        }
        summary.merged.push(n);
        continue;
      }
    }

    // Default wait / light ping for UNSTABLE species without photos already handled
    if (pingOk && speciesPack) {
      commentPr(
        n,
        `@${login} not merge-ready yet (\`${pr.mergeStateStatus}\`). Checklist:
1. Species + sample JSON
2. **Original photo evidence** in PR
3. CI green / rebase if needed

${GUIDE}`,
      );
      summary.pinged.push(n);
    } else {
      summary.waiting.push(n);
    }
  }

  console.log('\n=== SUMMARY ===');
  console.log(JSON.stringify(summary, null, 2));
}

main();
