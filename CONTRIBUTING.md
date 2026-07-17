# Contributing to PlantGuide

Thank you for your interest in contributing to PlantGuide — a plant identification and care guide application.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PlantGuide.git
   ```
3. **Install** the package in development mode:
   ```bash
   cd PlantGuide
   uv pip install -e ".[dev]"
   ```

## Running Tests

To run the test suite:

```bash
uv run pytest
```

To run tests with coverage:
```bash
uv run pytest --cov=plantguide
```

To run a specific test:
```bash
uv run pytest tests/test_specific_feature.py -v
```

## Claim Flow for MergeOS Bounties

1. **Comment** on the MergeOS bounty issue: "I claim this bounty"
2. **Fork** this repository if you haven't already
3. **Create** a feature branch: `git checkout -b fix/issue-NN-description`
4. **Implement** the feature or fix according to the issue requirements
5. **Add tests** for any new functionality
6. **Run tests** to ensure everything passes: `uv run pytest`
7. **Commit** your changes: `git commit -m "feat: description (#NN)"`
8. **Push** to your fork: `git push origin fix/issue-NN-description`
9. **Open** a Pull Request against the main repository
10. **Comment** on the MergeOS bounty issue with your PR URL
11. **Wait** for review and merging

## Development Guidelines

- Follow PEP 8 code style
- Run `ruff check` before committing
- Write tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features.

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/PlantGuide/discussions) or ask in the relevant issue.