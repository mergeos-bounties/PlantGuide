# Contributing to PlantGuide

Thank you for your interest in contributing to **PlantGuide**!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mergeos-bounties/PlantGuide.git
   cd PlantGuide
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies in editable mode with development tools:**
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests & Linter

Before submitting code, make sure all tests pass and your code adheres to linting standards:

```bash
# Run linting check
ruff check src tests

# Run unit tests
pytest -q

# Run end-to-end demo check
plantguide demo photo
```

## MergeOS Bounty Claim Flow

If you are working on a MergeOS bounty for PlantGuide, follow these steps to claim and receive your payout:

1. **Star** the relevant repositories:
   - [mergeos-bounties/PlantGuide](https://github.com/mergeos-bounties/PlantGuide)
   - [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos)
2. **Comment** on the issue you wish to work on: `I claim this bounty`
3. **Comment** on [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the issue you are claiming.
4. **Create a Pull Request** to `mergeos-bounties/PlantGuide` (target `master` branch) with `Fixes #<issue-number>` in the description.
5. Once your PR is reviewed and merged by a maintainer, **MRG credit** will be issued to your GitHub account based on the bounty scale (25/50/100/200 MRG).

For further details on bounty rules, consult [docs/BOUNTY.md](docs/BOUNTY.md).
