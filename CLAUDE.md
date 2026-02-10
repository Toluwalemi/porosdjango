# CLAUDE.md

## Project Overview
porosdjango is a CLI tool (`porosdjango create`) that scaffolds Django projects with opinionated defaults: custom User model, REST framework, and optional Docker integration (Celery, Prometheus, Nginx, Grafana, PostgreSQL).

## Architecture (porosdjango/cli.py)
- **TemplateRenderer** — Jinja2 via `PackageLoader("porosdjango", "templates")`. Call `.render(name, **ctx)`.
- **DjangoCommands** — static methods wrapping subprocess: `startproject`, `startapp`, `run_migrations`, `install_dependencies`.
- **SettingsModifier(settings_path)** — reads/transforms/writes Django `settings.py`. Key methods: `add_apps_and_auth(app_name)`, `add_docker_settings(project_name)`. Uses `_find_list_boundaries(lines, list_name)` to locate `INSTALLED_APPS`/`MIDDLEWARE`.
- **ProjectScaffold(renderer)** — creates files: requirements, gitignore, helpers, auth_app, docker setup. `create_docker_setup(project_name)` writes infra files + `{project}/celery.py` and `{project}/__init__.py`.
- **DjangoProjectBuilder(project_name, custom_app, docker)** — orchestrates everything in `setup()`.

## Templates
- All under `porosdjango/templates/`. Docker templates in `docker/` subdir (`.j2` files).
- Static Grafana JSON dashboards in `docker/grafana/` (copied, not rendered).
- Prometheus `{{ $labels }}` syntax escaped with `{% raw %}...{% endraw %}`.
- All docker templates receive `project_name` as context variable.

## Testing
- `pytest tests/ -v` — run from project root.
- Fixtures in `tests/conftest.py`: `mock_subprocess`, `mock_requests`, `mock_click`.
- Builder tests mock `scaffold` and `settings` as `MagicMock()`, patch `DjangoCommands` static methods.
- Docker scaffold tests must `(tmp_path / "project_name").mkdir()` before calling `create_docker_setup`.
- Settings modifier tests use a `DJANGO_SETTINGS_FIXTURE` constant with realistic Django settings.
- Integration tests use `click.testing.CliRunner` with `input=` for sequential prompts.
- **Test naming**: every test name must end with `_succeeds` or `_fails` (e.g. `test_add_apps_and_auth_succeeds`, `test_add_apps_with_missing_file_fails`).
- **Docstrings**: every test must have a GIVEN/WHEN/THEN docstring describing the scenario. Example:
  ```python
  def test_add_apps_and_auth_succeeds(tmp_path):
      """GIVEN a settings.py file with a default INSTALLED_APPS list
      WHEN add_apps_and_auth is called with a custom app name
      THEN the settings file contains the custom app and AUTH_USER_MODEL
      """
  ```

## Workflow
1. Plan non-trivial tasks in `tasks/todo.md` with checkable items. Enter plan mode for 3+ step tasks.
2. Track progress, verify with tests before marking done.
3. Log corrections to `tasks/lessons.md`.
4. Keep changes minimal and simple. No over-engineering.
5. Fix bugs autonomously — find root cause, fix, prove it works.
