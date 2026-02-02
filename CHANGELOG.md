# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

> **Note:** For releases after `0.1.2`, see [GitHub Releases](https://github.com/Toluwalemi/porosdjango/releases).

## [0.1.2] - 2026-02-02

### Added
- GitHub Actions workflow for automated PyPI publishing via trusted publishing
- Changelog URL to `pyproject.toml` (points to GitHub Releases)

### Changed
- Refactored `cli.py` into focused components (`TemplateRenderer`, `DjangoCommands`, `SettingsModifier`, `ProjectScaffold`)
- Replaced bare `Exception` catches with specific exception types
- Fixed Jinja2 autoescape (disabled HTML escaping for Python code templates)
- Fixed inconsistent Python executable usage in migrations
- Added type hints throughout the codebase
- Added input validation for project and app names
- Updated Dockerfile template to use Python 3.11

### Added
- Custom exception hierarchy in `exceptions.py`
- Constants module for hardcoded values
- `CONTRIBUTING.md` with development guidelines
- Dev dependencies (`pytest`, `pytest-cov`, `ruff`) in `pyproject.toml`
- Ruff and pytest configuration in `pyproject.toml`

### Removed
- Empty `utils.py` placeholder module

### Fixed
- Version mismatch between `__init__.py` and `pyproject.toml` (now derived from package metadata)
- Stale output message ("2. python manage.py runserver")
- Network timeout for `.gitignore` fetch (added 5s timeout)

## [0.1.1] - 2025-01-01

### Fixed
- Resolved ValueError in project setup

### Added
- Helpers module with `BaseModel` (UUID primary key, timestamps, soft delete)
- `auth_app` configuration with custom User model
- Dependency installation step during setup

## [0.1.0] - 2025-01-01

### Added
- Initial release
- CLI tool with `create` command
- Django project scaffolding with configurable project app name
- Optional custom app creation
- Custom User model with email-based authentication
- Django REST Framework integration
- Auto-generated `.gitignore` from gitignore.io
- Automatic database migrations
