import os
import subprocess
import click
import requests
from jinja2 import Environment, PackageLoader, select_autoescape
import sys


class DjangoProjectBuilder:
    """Class for building and configuring Django projects."""

    def __init__(self, project_app_name="config", custom_app_name=None):
        """Initialize the project builder with project settings.

        Args:
            project_app_name (str): Name of the Django project app
            custom_app_name (str): Name of the custom application
        """
        self.project_app_name = project_app_name
        self.custom_app_name = custom_app_name
        self.settings_path = os.path.join(project_app_name, "settings.py")
        self.jinja_env = Environment(
            loader=PackageLoader("porosdjango", "templates"),
            autoescape=select_autoescape(),
        )

    def create_django_project(self):
        """Create the Django project using django-admin."""
        try:
            click.echo(
                f"Creating Django project with app name '{self.project_app_name}'..."
            )
            subprocess.run(
                ["django-admin", "startproject", self.project_app_name, "."], check=True
            )
            return True
        except subprocess.CalledProcessError:
            click.echo(
                "Failed to create Django project. Make sure django-admin is available."
            )
            return False

    def create_custom_app(self):
        """Create the custom application."""
        if not self.custom_app_name:
            click.echo("Skipping custom app creation as none was specified.")
            return True
        try:
            click.echo(f"Creating application '{self.custom_app_name}'...")
            subprocess.run(
                [sys.executable, "manage.py", "startapp", self.custom_app_name],
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to create app {self.custom_app_name}: {e}")
            return False

    def create_helpers_module(self):
        """Create the helpers module with base model utilities."""
        try:
            click.echo("Creating helpers module...")
            os.makedirs("helpers", exist_ok=True)
            with open(os.path.join("helpers", "__init__.py"), "w") as f:
                f.write("")

            db_helpers_template = self.jinja_env.get_template("db_helpers.py.j2")
            with open(os.path.join("helpers", "db_helpers.py"), "w") as f:
                f.write(db_helpers_template.render())
            return True
        except Exception as e:
            click.echo(f"Failed to create helpers module: {e}")
            return False

    def create_auth_app(self):
        """Create and configure the auth_app with a custom User model."""
        try:
            click.echo("Creating auth_app...")
            subprocess.run(
                [sys.executable, "manage.py", "startapp", "auth_app"], check=True
            )

            # Setup custom User model
            click.echo("Setting up custom User model...")
            models_template = self.jinja_env.get_template("models.py.j2")
            with open(os.path.join("auth_app", "models.py"), "w") as f:
                f.write(models_template.render())

            # Setup custom UserManager
            click.echo("Setting up custom UserManager...")
            managers_template = self.jinja_env.get_template("managers.py.j2")
            with open(os.path.join("auth_app", "managers.py"), "w") as f:
                f.write(managers_template.render())

            return True
        except subprocess.CalledProcessError:
            click.echo("Failed to create auth_app.")
            return False
        except Exception as e:
            click.echo(f"Failed to configure auth_app: {e}")
            return False

    def update_settings(self):
        """Update the settings.py file with custom configurations."""
        click.echo("Updating settings.py...")
        try:
            with open(self.settings_path, "r") as f:
                settings_content = f.read()

            # Update INSTALLED_APPS
            if "INSTALLED_APPS = [" in settings_content:
                # Find the INSTALLED_APPS list and add our apps
                lines = settings_content.split("\n")
                app_list_start = None
                app_list_end = None

                for i, line in enumerate(lines):
                    if "INSTALLED_APPS = [" in line:
                        app_list_start = i
                    elif app_list_start is not None and "]" in line:
                        app_list_end = i
                        break

                if app_list_start is not None and app_list_end is not None:
                    # Insert app(s) before the closing bracket
                    if self.custom_app_name:
                        lines.insert(app_list_end, f"    '{self.custom_app_name}',")
                    lines.insert(app_list_end, "    'auth_app',")
                    lines.insert(app_list_end, "    'rest_framework',")

                    # Add AUTH_USER_MODEL at the end
                    lines.append("\n# Custom user model")
                    lines.append("AUTH_USER_MODEL = 'auth_app.User'")

                    with open(self.settings_path, "w") as f:
                        f.write("\n".join(lines))
                    return True
                else:
                    click.echo(
                        "Could not locate INSTALLED_APPS in settings.py. Manual update required."
                    )
                    return False
            else:
                click.echo(
                    "Could not find INSTALLED_APPS in settings.py. Manual update required."
                )
                return False
        except Exception as e:
            click.echo(f"Failed to update settings.py: {e}")
            return False

    def create_requirements(self):
        """Create the requirements.txt file."""
        click.echo("Creating requirements.txt...")
        try:
            with open("requirements.txt", "w") as f:
                f.write("Django==6.0\ndjangorestframework==3.16.1\n")
            return True
        except Exception as e:
            click.echo(f"Failed to create requirements.txt: {e}")
            return False

    def create_gitignore(self):
        """Create .gitignore file for Django projects."""
        click.echo("Fetching .gitignore for Django...")
        try:
            gitignore_url = "https://www.toptal.com/developers/gitignore/api/django"
            response = requests.get(gitignore_url)
            if response.status_code == 200:
                with open(".gitignore", "w") as f:
                    f.write(response.text)
                return True
            else:
                click.echo("Failed to fetch .gitignore. Creating a basic one...")
                with open(".gitignore", "w") as f:
                    f.write(
                        "__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nenv/\nbuild/\n"
                    )
                return True
        except Exception as e:
            click.echo(f"Failed to create .gitignore: {e}")
            return False

    def run_migrations(self):
        """Run Django migrations for the project."""
        click.echo("Running migrations...")
        try:
            subprocess.run(["python", "manage.py", "makemigrations"], check=True)
            subprocess.run(["python", "manage.py", "migrate"], check=True)
            return True
        except subprocess.CalledProcessError:
            click.echo("Failed to run migrations. You may need to run them manually.")
            return False

    def install_dependencies(self):
        """Install required dependencies from requirements.txt."""
        click.echo("Installing dependencies from requirements.txt...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
            click.echo("Dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to install dependencies: {e}")
            return False

    def setup(self):
        """Run the complete setup process."""
        if not self.create_requirements():
            return False
        if not self.install_dependencies():
            click.echo(
                "Warning: Failed to install dependencies. Continuing with setup..."
            )
        if not self.create_django_project():
            return False
        if not self.create_custom_app():
            return False
        if not self.create_helpers_module():
            return False
        if not self.create_auth_app():
            return False
        if not self.update_settings():
            return False
        self.create_gitignore()
        self.run_migrations()

        click.echo("\nSetup complete!")
        click.echo("\nUse this command to run your project:")
        click.echo("2. python manage.py runserver")

        return True


@click.group()
def cli():
    """PorosDjango - Opinionated Django Project Setup Tool."""
    pass


@cli.command()
def create():
    """Create a new Django project with custom preferences."""
    project_app_name = click.prompt(
        "What would you like to name your Django project app (default: config)?",
        default="config",
        show_default=False,
    )
    # Prompt for custom app name (optional)
    create_custom = click.confirm(
        "Would you like to create a custom app?", default=True
    )
    custom_app_name = None
    if create_custom:
        while not custom_app_name:
            custom_app_name = click.prompt(
                "What would you like to name your application?"
            )
            if not custom_app_name:
                click.echo("Application name is required if creating a custom app")

    # Create and run the project builder
    builder = DjangoProjectBuilder(project_app_name, custom_app_name)
    builder.setup()


def main():
    cli()


if __name__ == "__main__":
    main()
