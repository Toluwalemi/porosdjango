# Contributing to PorosDjango

Thanks for your interest in contributing to PorosDjango! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:

```bash
git clone https://github.com/<your-username>/porosdjango.git
cd porosdjango
```

2. Create a virtual environment and install dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=porosdjango
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. The pre-commit hooks will run these automatically, but you can also run them manually:

```bash
ruff check .
ruff format .
```

Key style rules:
- Target Python 3.11+
- Use type hints on all function signatures
- Use specific exception types (avoid bare `except Exception`)
- Keep functions focused and small

## Making Changes

1. Create a feature branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and write tests for new functionality.

3. Ensure all tests pass and linting is clean:

```bash
pytest
ruff check .
```

4. Commit your changes using [conventional commits](https://www.conventionalcommits.org/):

```
feat: add new template for docker-compose
fix: resolve issue with settings.py parsing
docs: update installation instructions
refactor: split builder class into modules
```

5. Push your branch and open a Pull Request against `main`.

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation if behavior changes
- Ensure CI checks pass before requesting review

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/Toluwalemi/porosdjango/issues) to report bugs or request features. Include:

- Python version
- Django version
- Steps to reproduce the issue
- Expected vs actual behavior
