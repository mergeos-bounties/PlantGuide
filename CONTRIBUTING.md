# Contributing to PlantGuide

Thank you for your interest in contributing to PlantGuide — a plant identification and care guide application. This guide covers setup, development workflow, testing, and the MergeOS bounty claim process.

## Getting Started

### Prerequisites

- **Python 3.11+**
- **uv** (recommended) or pip + venv
- **Git**

### Setup

1. **Fork** the repository on GitHub.
2. **Star** the repos (required for MergeOS bounty claims):
   - [mergeos-bounties/PlantGuide](https://github.com/mergeos-bounties/PlantGuide)
   - [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos)
3. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PlantGuide.git
   cd PlantGuide
   ```
4. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync --dev

   # Or using pip + venv
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # .\.venv\Scripts\activate  # Windows
   pip install -e ".[dev]"
   ```
5. **Verify your setup:**
   ```bash
   plantguide version
   plantguide species list
   plantguide demo photo
   ```

## Good First Issues

If you're new to the project, check out issues tagged with [`good-first-issue`](https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`bounty`](https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Abounty). These are beginner-friendly tasks that help you learn the codebase while earning MRG rewards.

**Suggested starting points:**
- Adding a new plant species to `data/species/` (see [SPECIES.md](SPECIES.md))
- Improving the CLI user experience
- Writing additional tests
- Contributing care tips in your native language

## Development Workflow

1. **Create a feature branch** from `master`:
   ```bash
   git checkout master
   git pull origin master
   git checkout -b feat/my-feature
   ```

2. **Make your changes.** Follow the code style below.

3. **Run linting and tests:**
   ```bash
   ruff check src tests
   pytest -q
   ```

4. **Run the demo** to verify end-to-end:
   ```bash
   plantguide demo photo
   ```

5. **Commit** with a descriptive message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add Monstera Adansonii species data
   fix: correct watering frequency for snake plant
   docs: update setup instructions in README
   ```

6. **Push** to your fork:
   ```bash
   git push origin feat/my-feature
   ```

7. **Open a Pull Request** against `master`. In the PR description, include `Fixes #N` (replacing `N` with the issue number).

## Code Style

- Follow **PEP 8** conventions.
- Run `ruff check src tests` before committing — it catches style issues and potential bugs.
- Write **tests** for new functionality in the `tests/` directory.
- Use **type hints** for new functions.

## Testing

Run the full test suite:

```bash
pytest -q
```

Run specific test files:

```bash
pytest tests/test_identify.py -q
pytest tests/test_care.py -q
```

Run with coverage:

```bash
pytest --cov=src/plantguide --cov-report=term-missing
```

### Test conventions

- Unit tests go in `tests/` and mirror the `src/plantguide/` structure.
- Use `data/samples/` fixtures for integration tests.
- New species data should include a test loading from `data/species/`.

## MergeOS Bounty Claim Flow

PlantGuide pays contributors in **MRG** through the MergeOS bounty program. Here's how to claim and earn bounties:

### Before You Start

1. **Star** these repos:
   - [mergeos-bounties/PlantGuide](https://github.com/mergeos-bounties/PlantGuide)
   - [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos)
2. **Find a bounty** — browse [open bounty issues](https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Abounty).

### Claiming a Bounty

1. **Comment** on the issue: `I claim this bounty`
2. **Comment** on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the issue.
3. **Open a PR** to `master` with `Fixes #<issue-number>` in the description.
4. A maintainer reviews → merges → **MRG credit** is applied to `github:<your-username>` on the MergeOS ledger.

### Payout Scale

| Scope | Typical MRG |
| --- | ---: |
| Small / good-first | 25 |
| Medium feature | 50 |
| Large system piece | 100 |
| Extra-large | 200 |

For full details, see [docs/BOUNTY.md](docs/BOUNTY.md).

## Pull Request Checklist

- [ ] Branch is up-to-date with `master`
- [ ] Code follows project style (`ruff check` passes)
- [ ] Tests added / updated for new functionality
- [ ] All existing tests pass (`pytest -q`)
- [ ] `plantguide demo photo` works end-to-end
- [ ] Documentation updated if needed
- [ ] PR description references the issue (`Fixes #N`)
- [ ] If claiming a bounty: followed the [claim flow](#mergeos-bounty-claim-flow)

## Project Structure

```
src/plantguide/
  identify/   # tags, sample JSON, vision photo path
  care/       # care cards, watering, SVG export
  data/       # loaders
  collection/ # user plants
  integrations/
data/
  species/              # catalog JSON
  samples/              # obs_*.json
  samples/photos/       # demo plant JPGs + manifest.json
tests/
docs/
```

## Need Help?

- Ask in the relevant [GitHub Issue](https://github.com/mergeos-bounties/PlantGuide/issues).
- Check [docs/BOUNTY.md](docs/BOUNTY.md) for bounty program details.
- See the [ROADMAP](docs/ROADMAP.md) for planned features.
