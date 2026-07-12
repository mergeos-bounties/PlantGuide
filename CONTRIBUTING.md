# Contributing to PlantGuide

Thank you for your interest in contributing to PlantGuide — a plant identification and care guide application.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PlantGuide.git
   cd PlantGuide
   ```
3. **Set up a development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

## Good First Issues

If you're new to the project, check out issues tagged with `good-first-issue` in the [issue tracker](https://github.com/mergeos-bounties/PlantGuide/issues). These are beginner-friendly tasks that help you learn the codebase.

Suggested starting points:
- Adding a new plant species to `data/species/`
- Improving the CLI user experience
- Writing additional tests

## How to Contribute

- **Report bugs** by opening a GitHub Issue.
- **Suggest features** by opening a GitHub Issue with the `enhancement` label.
- **Add plant species** by contributing a new JSON file to `data/species/`.
- **Submit code** via a Pull Request.

## Development Workflow

1. Create a feature branch from `master`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes.
3. Run linting and tests:
   ```bash
   ruff check src tests
   pytest
   ```
4. Commit with a clear message:
   ```
   feat: add Monstera Adansonii species data
   ```
5. Push to your fork and open a Pull Request against `master`.
6. Link any related issues in the PR description using `Closes #N`.

## Code Style

- Follow PEP 8 conventions.
- Run `ruff check` before committing.
- Write tests for new functionality.

## Pull Request Checklist

- [ ] Code follows project style (ruff passes)
- [ ] Tests added / updated for new functionality
- [ ] All existing tests pass
- [ ] Documentation updated if needed
- [ ] PR description references related issues

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/PlantGuide/discussions) or ask in the relevant issue.
