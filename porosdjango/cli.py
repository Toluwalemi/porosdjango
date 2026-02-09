from __future__ import annotations

import os
import shutil
import subprocess
import sys

import click
import requests
from jinja2 import Environment, PackageLoader

from porosdjango.constants import (
    DOCKER_REQUIREMENTS_CONTENT,
    FALLBACK_GITIGNORE,
    GITIGNORE_URL,
    REQUIREMENTS_CONTENT,
)
from porosdjango.exceptions import (
    AppCreationError,
    DependencyInstallError,
    DockerScaffoldError,
    InvalidAppNameError,
    ProjectCreationError,
    SettingsUpdateError,
    TemplateRenderError,
)
from porosdjango.utils import validate_app_name


class TemplateRenderer:
    """Handles Jinja2 template loading and rendering."""

    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("porosdjango", "templates"),
            autoescape=False,
        )

    def render(self, template_name: str, **context: str) -> str:
        """Render a template by name and return the result as a string.

        Args:
            template_name: The filename of the template (e.g. 'models.py.j2').
            **context: Template variables to pass to the renderer.

        Returns:
            The rendered template content.

        Raises:
            TemplateRenderError: If rendering fails.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateRenderError(
                f"Failed to render template '{template_name}': {e}"
            ) from e


class DjangoCommands:
    """Runs Django management commands via subprocess."""

    @staticmethod
    def startproject(project_name: str) -> None:
        """Run django-admin startproject.

        Raises:
            ProjectCreationError: If the command fails.
        """
        try:
            subprocess.run(
                ["django-admin", "startproject", project_name, "."],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ProjectCreationError(
                "Failed to create Django project. Make sure django-admin is available."
            ) from e

    @staticmethod
    def startapp(app_name: str) -> None:
        """Run manage.py startapp.

        Raises:
            AppCreationError: If the command fails.
        """
        try:
            subprocess.run(
                [sys.executable, "manage.py", "startapp", app_name],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise AppCreationError(f"Failed to create app '{app_name}'.") from e

    @staticmethod
    def run_migrations() -> None:
        """Run makemigrations and migrate."""
        try:
            subprocess.run(
                [sys.executable, "manage.py", "makemigrations"],
                check=True,
            )
            subprocess.run(
                [sys.executable, "manage.py", "migrate"],
                check=True,
            )
        except subprocess.CalledProcessError:
            click.echo(
                "Warning: Failed to run migrations. You may need to run them manually."
            )

    @staticmethod
    def install_dependencies() -> None:
        """Install dependencies from requirements.txt.

        Raises:
            DependencyInstallError: If pip install fails.
        """
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise DependencyInstallError(
                "Failed to install dependencies from requirements.txt."
            ) from e


class SettingsModifier:
    """Handles modifications to Django's settings.py."""

    def __init__(self, settings_path: str) -> None:
        self.settings_path = settings_path

    def _read_settings(self) -> str:
        """Read the settings file content.

        Returns:
            The file content as a string.

        Raises:
            SettingsUpdateError: If the file cannot be read.
        """
        try:
            with open(self.settings_path) as f:
                return f.read()
        except OSError as e:
            raise SettingsUpdateError(
                f"Cannot read settings file at '{self.settings_path}': {e}"
            ) from e

    def _write_settings(self, content: str) -> None:
        """Write content to the settings file.

        Raises:
            SettingsUpdateError: If the file cannot be written.
        """
        try:
            with open(self.settings_path, "w") as f:
                f.write(content)
        except OSError as e:
            raise SettingsUpdateError(
                f"Failed to write updated settings.py: {e}"
            ) from e

    def _find_list_boundaries(
        self, lines: list[str], list_name: str
    ) -> tuple[int, int]:
        """Find the start and end indices of a Python list assignment.

        Args:
            lines: The settings file split into lines.
            list_name: The variable name (e.g. "INSTALLED_APPS", "MIDDLEWARE").

        Returns:
            A (start_index, end_index) tuple.

        Raises:
            SettingsUpdateError: If the list cannot be found.
        """
        pattern = f"{list_name} = ["
        list_start = None
        list_end = None

        for i, line in enumerate(lines):
            if pattern in line:
                list_start = i
            elif list_start is not None and "]" in line:
                list_end = i
                break

        if list_start is None or list_end is None:
            raise SettingsUpdateError(
                f"Could not locate {list_name} boundaries in settings.py. "
                "Manual update required."
            )
        return list_start, list_end

    def add_apps_and_auth(self, custom_app_name: str | None) -> None:
        """Insert apps into INSTALLED_APPS and set AUTH_USER_MODEL.

        Args:
            custom_app_name: Optional custom app name to add.

        Raises:
            SettingsUpdateError: If settings.py cannot be parsed or written.
        """
        settings_content = self._read_settings()

        if "INSTALLED_APPS = [" not in settings_content:
            raise SettingsUpdateError(
                "Could not find INSTALLED_APPS in settings.py. Manual update required."
            )

        lines = settings_content.split("\n")
        _, app_list_end = self._find_list_boundaries(lines, "INSTALLED_APPS")

        if custom_app_name:
            lines.insert(app_list_end, f"    '{custom_app_name}',")
        lines.insert(app_list_end, "    'auth_app',")
        lines.insert(app_list_end, "    'rest_framework',")

        lines.append("\n# Custom user model")
        lines.append("AUTH_USER_MODEL = 'auth_app.User'")

        self._write_settings("\n".join(lines))

    def add_docker_settings(self, project_name: str) -> None:
        """Add Docker-related settings to settings.py.

        Modifies settings.py to include PostgreSQL database config,
        Prometheus monitoring, Celery task queue, and email settings
        required by the Docker infrastructure.

        Args:
            project_name: The Django project name.

        Raises:
            SettingsUpdateError: If settings.py cannot be parsed or written.
        """
        settings_content = self._read_settings()
        lines = settings_content.split("\n")

        # 1. Add `import os` after `from pathlib import Path`
        for i, line in enumerate(lines):
            if "from pathlib import Path" in line:
                lines.insert(i + 1, "import os")
                break

        # 2. Update ALLOWED_HOSTS
        for i, line in enumerate(lines):
            if "ALLOWED_HOSTS = []" in line:
                lines[i] = (
                    "ALLOWED_HOSTS = os.environ.get("
                    '"DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"'
                    ').split(",")'
                )
                break

        # 3. Add STATIC_ROOT after STATIC_URL
        for i, line in enumerate(lines):
            if line.startswith("STATIC_URL"):
                lines.insert(
                    i + 1, 'STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")'
                )
                break

        # 4. Add docker apps to INSTALLED_APPS
        _, app_list_end = self._find_list_boundaries(lines, "INSTALLED_APPS")
        lines.insert(app_list_end, "    'django_celery_beat',")
        lines.insert(app_list_end, "    'django_prometheus',")

        # 5. Add Prometheus middleware
        mw_start, mw_end = self._find_list_boundaries(lines, "MIDDLEWARE")
        lines.insert(
            mw_end,
            "    'django_prometheus.middleware.PrometheusAfterMiddleware',",
        )
        lines.insert(
            mw_start + 1,
            "    'django_prometheus.middleware.PrometheusBeforeMiddleware',",
        )

        # 6. Replace DATABASES block with PostgreSQL/SQLite fallback
        db_start = None
        for i, line in enumerate(lines):
            if "DATABASES = {" in line:
                db_start = i
                break

        if db_start is not None:
            depth = 0
            db_end = db_start
            for i in range(db_start, len(lines)):
                depth += lines[i].count("{") - lines[i].count("}")
                if depth == 0:
                    db_end = i
                    break

            db_replacement = [
                'if os.environ.get("POSTGRES_DB"):',
                "    DATABASES = {",
                '        "default": {',
                '            "ENGINE": "django.db.backends.postgresql",',
                '            "NAME": os.environ["POSTGRES_DB"],',
                '            "USER": os.environ["POSTGRES_USER"],',
                '            "PASSWORD": os.environ["POSTGRES_PASSWORD"],',
                '            "HOST": os.environ.get("POSTGRES_HOST", "db"),',
                '            "PORT": os.environ.get("POSTGRES_PORT", "5432"),',
                "        }",
                "    }",
                "else:",
                "    DATABASES = {",
                '        "default": {',
                '            "ENGINE": "django.db.backends.sqlite3",',
                '            "NAME": BASE_DIR / "db.sqlite3",',
                "        }",
                "    }",
            ]
            lines[db_start : db_end + 1] = db_replacement

        # 7. Append Celery config
        lines.append("")
        lines.append("# Celery")
        lines.append(
            "CELERY_BROKER_URL = os.environ.get("
            '"CELERY_BROKER_URL", "redis://localhost:6379/1")'
        )
        lines.append(
            "CELERY_RESULT_BACKEND = os.environ.get("
            '"CELERY_RESULT_BACKEND", "redis://localhost:6379/2")'
        )

        # 8. Append email config
        lines.append("")
        lines.append("# Email")
        lines.append(
            "EMAIL_BACKEND = os.environ.get("
            '"EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")'
        )
        lines.append('EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")')
        lines.append('EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))')
        lines.append(
            'EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() '
            'in ("true", "1")'
        )
        lines.append(
            f"DEFAULT_FROM_EMAIL = os.environ.get("
            f'"DEFAULT_FROM_EMAIL", "noreply@{project_name}.local")'
        )

        self._write_settings("\n".join(lines))


class ProjectScaffold:
    """Creates project files and directories."""

    def __init__(self, renderer: TemplateRenderer) -> None:
        self.renderer = renderer

    def create_requirements(self, docker: bool = False) -> None:
        """Write requirements.txt with pinned dependencies.

        Args:
            docker: If True, append Docker-specific dependencies.
        """
        content = REQUIREMENTS_CONTENT
        if docker:
            content += DOCKER_REQUIREMENTS_CONTENT
        with open("requirements.txt", "w") as f:
            f.write(content)

    def create_gitignore(self) -> None:
        """Fetch .gitignore from the network, falling back to a bundled default."""
        try:
            response = requests.get(GITIGNORE_URL, timeout=5)
            response.raise_for_status()
            content = response.text
        except requests.RequestException:
            click.echo(
                "Could not fetch .gitignore from network. Using bundled default."
            )
            content = FALLBACK_GITIGNORE

        with open(".gitignore", "w") as f:
            f.write(content)

    def create_helpers_module(self) -> None:
        """Create the helpers module with BaseModel utilities.

        Raises:
            TemplateRenderError: If the template cannot be rendered.
        """
        os.makedirs("helpers", exist_ok=True)
        with open(os.path.join("helpers", "__init__.py"), "w") as f:
            f.write("")

        content = self.renderer.render("db_helpers.py.j2")
        with open(os.path.join("helpers", "db_helpers.py"), "w") as f:
            f.write(content)

    def create_auth_app_files(self) -> None:
        """Write custom User model and UserManager into auth_app.

        Raises:
            TemplateRenderError: If templates cannot be rendered.
        """
        models_content = self.renderer.render("models.py.j2")
        with open(os.path.join("auth_app", "models.py"), "w") as f:
            f.write(models_content)

        managers_content = self.renderer.render("managers.py.j2")
        with open(os.path.join("auth_app", "managers.py"), "w") as f:
            f.write(managers_content)

    def create_docker_setup(self, project_name: str) -> None:
        """Create Docker integration files for the project.

        Args:
            project_name: The project name used for template variable substitution.

        Raises:
            DockerScaffoldError: If Docker scaffolding fails.
        """
        try:
            dirs = [
                os.path.join("infrastructure", "docker", "scripts"),
                os.path.join("infrastructure", "docker", "nginx"),
                os.path.join("infrastructure", "docker", "prometheus"),
                os.path.join("infrastructure", "docker", "alertmanager"),
                os.path.join(
                    "infrastructure",
                    "docker",
                    "grafana",
                    "provisioning",
                    "datasources",
                ),
                os.path.join(
                    "infrastructure",
                    "docker",
                    "grafana",
                    "provisioning",
                    "dashboards",
                    "json",
                ),
            ]
            for d in dirs:
                os.makedirs(d, exist_ok=True)

            ctx = {"project_name": project_name}

            template_map = {
                os.path.join(
                    "infrastructure", "docker", "Dockerfile"
                ): "docker/Dockerfile.j2",
                "docker-compose.yml": "docker/docker_compose.yml.j2",
                ".dockerignore": "docker/dockerignore.j2",
                ".env.example": "docker/env_example.j2",
                os.path.join(
                    "infrastructure", "docker", "scripts", "dev.sh"
                ): "docker/dev.sh.j2",
                os.path.join(
                    "infrastructure", "docker", "scripts", "celery_worker.sh"
                ): "docker/celery_worker.sh.j2",
                os.path.join(
                    "infrastructure", "docker", "scripts", "celery_beat.sh"
                ): "docker/celery_beat.sh.j2",
                os.path.join(
                    "infrastructure", "docker", "scripts", "flower.sh"
                ): "docker/flower.sh.j2",
                os.path.join(
                    "infrastructure", "docker", "nginx", "nginx.conf"
                ): "docker/nginx.conf.j2",
                os.path.join(
                    "infrastructure", "docker", "prometheus", "prometheus.yml"
                ): "docker/prometheus.yml.j2",
                os.path.join(
                    "infrastructure", "docker", "prometheus", "alert_rules.yml"
                ): "docker/alert_rules.yml.j2",
                os.path.join(
                    "infrastructure", "docker", "alertmanager", "alertmanager.yml"
                ): "docker/alertmanager.yml.j2",
                os.path.join(
                    "infrastructure",
                    "docker",
                    "grafana",
                    "provisioning",
                    "datasources",
                    "datasource.yml",
                ): "docker/grafana_datasource.yml.j2",
                os.path.join(
                    "infrastructure",
                    "docker",
                    "grafana",
                    "provisioning",
                    "dashboards",
                    "dashboard.yml",
                ): "docker/grafana_dashboard.yml.j2",
                os.path.join(project_name, "celery.py"): "docker/celery_conf.py.j2",
                os.path.join(project_name, "__init__.py"): "docker/init_celery.py.j2",
            }

            for dest, template_name in template_map.items():
                content = self.renderer.render(template_name, **ctx)
                with open(dest, "w") as f:
                    f.write(content)

            # Copy static Grafana dashboard JSON files
            grafana_json_dir = os.path.join(
                "infrastructure",
                "docker",
                "grafana",
                "provisioning",
                "dashboards",
                "json",
            )
            static_dir = os.path.join(
                os.path.dirname(__file__),
                "templates",
                "docker",
                "grafana",
            )
            for json_file in ("django-app.json", "infrastructure.json", "celery.json"):
                src = os.path.join(static_dir, json_file)
                dst = os.path.join(grafana_json_dir, json_file)
                shutil.copy2(src, dst)

        except TemplateRenderError:
            raise
        except Exception as e:
            raise DockerScaffoldError(f"Failed to create Docker setup: {e}") from e


class DjangoProjectBuilder:
    """Orchestrates the full project setup process."""

    def __init__(
        self,
        project_app_name: str = "config",
        custom_app_name: str | None = None,
        docker_integration: bool = False,
    ) -> None:
        self.project_app_name = project_app_name
        self.custom_app_name = custom_app_name
        self.docker_integration = docker_integration
        self.renderer = TemplateRenderer()
        self.scaffold = ProjectScaffold(self.renderer)
        self.settings = SettingsModifier(os.path.join(project_app_name, "settings.py"))

    def setup(self) -> bool:
        """Run the complete setup process.

        Returns:
            True if setup completed successfully, False otherwise.
        """
        try:
            click.echo("Creating requirements.txt...")
            self.scaffold.create_requirements(docker=self.docker_integration)

            click.echo("Installing dependencies...")
            try:
                DjangoCommands.install_dependencies()
                click.echo("Dependencies installed successfully.")
            except DependencyInstallError as e:
                click.echo(f"Warning: {e} Continuing with setup...")

            click.echo(
                f"Creating Django project with app name '{self.project_app_name}'..."
            )
            DjangoCommands.startproject(self.project_app_name)

            if self.custom_app_name:
                click.echo(f"Creating application '{self.custom_app_name}'...")
                DjangoCommands.startapp(self.custom_app_name)
            else:
                click.echo("Skipping custom app creation as none was specified.")

            click.echo("Creating helpers module...")
            self.scaffold.create_helpers_module()

            click.echo("Creating auth_app...")
            DjangoCommands.startapp("auth_app")

            click.echo("Setting up custom User model and UserManager...")
            self.scaffold.create_auth_app_files()

            click.echo("Updating settings.py...")
            self.settings.add_apps_and_auth(self.custom_app_name)

            click.echo("Creating .gitignore...")
            self.scaffold.create_gitignore()

            if self.docker_integration:
                click.echo("Setting up Docker integration...")
                self.scaffold.create_docker_setup(self.project_app_name)
                self.settings.add_docker_settings(self.project_app_name)

            click.echo("Running migrations...")
            DjangoCommands.run_migrations()

            click.echo("\nSetup complete!")
            if self.docker_integration:
                click.echo("\nRun your project with Docker:")
                click.echo("  cp .env.example .env")
                click.echo("  docker compose up --build")
            else:
                click.echo("\nRun your project with:")
                click.echo("  python manage.py runserver")
            return True

        except (
            ProjectCreationError,
            AppCreationError,
            SettingsUpdateError,
            TemplateRenderError,
            DockerScaffoldError,
        ) as e:
            click.echo(f"\nError: {e}")
            return False


@click.group()
def cli() -> None:
    """PorosDjango - Opinionated Django Project Setup Tool."""


@cli.command()
def create() -> None:
    """Create a new Django project with custom preferences."""
    project_app_name = click.prompt(
        "What would you like to name your Django project app (default: config)?",
        default="config",
        show_default=False,
    )

    try:
        validate_app_name(project_app_name)
    except InvalidAppNameError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1) from None

    create_custom = click.confirm(
        "Would you like to create a custom app?", default=True
    )
    custom_app_name = None
    if create_custom:
        while not custom_app_name:
            name = click.prompt("What would you like to name your application?")
            try:
                custom_app_name = validate_app_name(name)
            except InvalidAppNameError as e:
                click.echo(f"Error: {e}")

    docker_integration = click.confirm(
        "Would you like to add Docker integration?", default=False
    )

    builder = DjangoProjectBuilder(
        project_app_name, custom_app_name, docker_integration
    )
    builder.setup()


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
