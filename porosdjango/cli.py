from __future__ import annotations

import os
import subprocess
import sys

import click
import requests
from jinja2 import Environment, PackageLoader

from porosdjango.constants import (
    FALLBACK_GITIGNORE,
    GITIGNORE_URL,
    REQUIREMENTS_CONTENT,
)
from porosdjango.exceptions import (
    AppCreationError,
    DependencyInstallError,
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

    def render(self, template_name: str) -> str:
        """Render a template by name and return the result as a string.

        Args:
            template_name: The filename of the template (e.g. 'models.py.j2').

        Returns:
            The rendered template content.

        Raises:
            TemplateRenderError: If rendering fails.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render()
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

    def add_apps_and_auth(self, custom_app_name: str | None) -> None:
        """Insert apps into INSTALLED_APPS and set AUTH_USER_MODEL.

        Args:
            custom_app_name: Optional custom app name to add.

        Raises:
            SettingsUpdateError: If settings.py cannot be parsed or written.
        """
        try:
            with open(self.settings_path) as f:
                settings_content = f.read()
        except OSError as e:
            raise SettingsUpdateError(
                f"Cannot read settings file at '{self.settings_path}': {e}"
            ) from e

        if "INSTALLED_APPS = [" not in settings_content:
            raise SettingsUpdateError(
                "Could not find INSTALLED_APPS in settings.py. Manual update required."
            )

        lines = settings_content.split("\n")
        app_list_start = None
        app_list_end = None

        for i, line in enumerate(lines):
            if "INSTALLED_APPS = [" in line:
                app_list_start = i
            elif app_list_start is not None and "]" in line:
                app_list_end = i
                break

        if app_list_start is None or app_list_end is None:
            raise SettingsUpdateError(
                "Could not locate INSTALLED_APPS boundaries in settings.py. "
                "Manual update required."
            )

        if custom_app_name:
            lines.insert(app_list_end, f"    '{custom_app_name}',")
        lines.insert(app_list_end, "    'auth_app',")
        lines.insert(app_list_end, "    'rest_framework',")

        lines.append("\n# Custom user model")
        lines.append("AUTH_USER_MODEL = 'auth_app.User'")

        try:
            with open(self.settings_path, "w") as f:
                f.write("\n".join(lines))
        except OSError as e:
            raise SettingsUpdateError(
                f"Failed to write updated settings.py: {e}"
            ) from e


class ProjectScaffold:
    """Creates project files and directories."""

    def __init__(self, renderer: TemplateRenderer) -> None:
        self.renderer = renderer

    def create_requirements(self) -> None:
        """Write requirements.txt with pinned dependencies."""
        with open("requirements.txt", "w") as f:
            f.write(REQUIREMENTS_CONTENT)

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


class DjangoProjectBuilder:
    """Orchestrates the full project setup process."""

    def __init__(
        self,
        project_app_name: str = "config",
        custom_app_name: str | None = None,
    ) -> None:
        self.project_app_name = project_app_name
        self.custom_app_name = custom_app_name
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
            self.scaffold.create_requirements()

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

            click.echo("Running migrations...")
            DjangoCommands.run_migrations()

            click.echo("\nSetup complete!")
            click.echo("\nRun your project with:")
            click.echo("  python manage.py runserver")
            return True

        except (
            ProjectCreationError,
            AppCreationError,
            SettingsUpdateError,
            TemplateRenderError,
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

    builder = DjangoProjectBuilder(project_app_name, custom_app_name)
    builder.setup()


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
