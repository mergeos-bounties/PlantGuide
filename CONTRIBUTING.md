# Contributing to PlantGuide

Thank you for helping improve PlantGuide — a plant identification and care guide application. This guide explains the local setup, test commands, good-first-issue path, and MergeOS bounty claim workflow.

## Quick Start

1. **Fork** the repository on GitHub.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/PlantGuide.git
   cd PlantGuide
   ```

3. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install the project with development dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

5. **Run a smoke test:**

   ```bash
   plantguide demo photo
   ```

## Good First Issue Path

If you are new to the project, start with small, reviewable changes:

- Add or improve one plant species entry.
- Improve a care tip, watering schedule, or documentation page.
- Add a small test for an existing CLI command.
- Improve README examples or generated demo instructions.

Recommended flow:

1. Pick an open issue labeled `good first issue`, `documentation`, or `bounty`.
2. Comment on the issue before starting so maintainers can see your intent.
3. Keep your first PR narrow: one issue, one behavior, one documentation topic, or one species pack.
4. Link the issue in your PR description with `Fixes #<issue-number>` when your PR fully resolves it.

## Development Workflow

Create a branch from `master`:

```bash
git checkout master
git pull origin master
git checkout -b docs/my-contribution
```

Make your changes, then run checks before opening a PR.

## Test Commands

Run the common checks locally:

```bash
ruff check src tests
pytest -q
```

Useful focused checks:

```bash
pytest -q tests/test_identify.py
pytest -q tests/test_care.py
pytest -q tests/test_watering_schedule.py
plantguide demo photo
plantguide species list
```

If you change documentation only, still run at least a smoke check when possible:

```bash
plantguide demo photo
```

## Code Style

- Keep Python code readable and typed where practical.
- Follow existing CLI and JSON field naming patterns.
- Prefer small functions and focused tests.
- Do not commit generated output unless the issue specifically asks for it.
- Keep documentation examples copy-pasteable.

## Pull Request Checklist

Before submitting, confirm:

- [ ] The PR targets the `master` branch.
- [ ] The PR title clearly describes the change.
- [ ] The PR body links the issue, for example `Fixes #18`.
- [ ] `ruff check src tests` passes, or the PR explains why it was not run.
- [ ] `pytest -q` passes, or the PR explains why it was not run.
- [ ] Documentation is updated when behavior or workflow changes.
- [ ] The diff is focused and does not include unrelated formatting churn.

## MergeOS Bounty Claim Workflow

For bounty issues that pay MRG credit, follow the issue-specific instructions and the repository bounty policy in [`docs/BOUNTY.md`](docs/BOUNTY.md).

Typical claim flow:

1. Star the product repository, such as <https://github.com/mergeos-bounties/PlantGuide>.
2. Star the MergeOS repository: <https://github.com/mergeos-bounties/mergeos>.
3. Comment on the bounty issue:

   ```text
   I claim this bounty
   ```

4. Comment on the MergeOS claim-token issue requested by the bounty, usually <https://github.com/mergeos-bounties/mergeos/issues/1>, with a link to the PlantGuide bounty issue.
5. Open a PR against `mergeos-bounties/PlantGuide` with a body that includes `Fixes #<issue-number>`.
6. After maintainer review and merge, MRG credit is recorded on the MergeOS ledger for `github:<your-username>`.

Do not include private wallet keys, secrets, or access tokens in issues, commits, or PR descriptions.

## Need Help?

Ask in the relevant GitHub issue, or open a discussion if the question is not tied to a specific change.
