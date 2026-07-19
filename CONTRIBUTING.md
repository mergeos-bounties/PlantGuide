# Contributing to PlantGuide

Thank you for considering contributing to PlantGuide! We welcome contributions from the community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/PlantGuide.git
   cd PlantGuide
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```
4. Run the tests to ensure everything works:
   ```bash
   uv run pytest
   ```

## Good First Issues

Looking for a place to start? We have a list of [good first issues](https://github.com/mergeos-bounties/PlantGuide/labels/good%20first%20issue) that are specifically marked for newcomers.

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-or-bugfix-name
   ```
2. Make your changes
3. Add tests for any new functionality
4. Ensure all tests pass:
   ```bash
   uv run pytest
   ```
5. Commit your changes:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

## Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to public functions and classes
- Keep functions focused and small
- Add type hints where possible

## Testing

- Write unit tests for new functionality
- Run the full test suite before submitting PRs
- Tests are located in the `tests/` directory
- We use pytest for testing

## Documentation

- Update README.md if you change the interface or usage
- Add docstrings to new functions and classes
- If adding new features, update relevant documentation in `docs/`

## Claiming a MergeOS Bounty

To claim MRG tokens for your contribution through the MergeOS bounty program:

1. Star the main MergeOS repositories:
   - https://github.com/mergeos-bounties/mergeos
   - https://github.com/mergeos-bounties/PlantGuide
2. Comment on the PlantGuide issue: `I claim this bounty`
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to this issue
4. Open a PR to PlantGuide's `master` branch with `Fixes #<issue-number>`
5. Wait for maintainer review and merge
6. After merge, you'll receive MRG credits to your GitHub username on the MergeOS ledger

## Submitting Changes

1. Push your branch to your fork:
   ```bash
   git push origin feature-or-bugfix-name
   ```
2. Open a Pull Request from your fork to the main PlantGuide repository
3. Ensure your PR description clearly describes the changes
4. Reference any related issues with `Fixes #<issue-number>` or `Closes #<issue-number>`
5. Wait for code review and feedback

## Reporting Issues

When reporting issues, please include:
- Your operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant screenshots or error messages

Thank you for contributing to PlantGuide!