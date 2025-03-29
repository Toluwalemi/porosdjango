import os
import subprocess
import click
import requests
from jinja2 import Environment, PackageLoader, select_autoescape


@click.group()
def cli():
    """Porosdjango - Opinionated Django Project Setup Tool."""
    pass


@cli.command()
def create():
    """Create a new Django project with custom preferences."""
    # Prompt for project app name
    project_app_name = click.prompt(
        "What would you like to name your Django project app (default: config)?",
        default="config",
        show_default=False,
    )

    # Create the Django project
    click.echo(f"Creating Django project with app name '{project_app_name}'...")
    try:
        subprocess.run(
            ["django-admin", "startproject", project_app_name, "."], check=True
        )
    except subprocess.CalledProcessError:
        click.echo(
            "Failed to create Django project. Make sure django-admin is available."
        )
        return

    custom_app_name = ""
    while not custom_app_name:
        custom_app_name = click.prompt("What would you like to name your application?")
        if not custom_app_name:
            click.echo("Application name is required.")

    # Create the custom app
    click.echo(f"Creating application '{custom_app_name}'...")
    try:
        subprocess.run(["python", "manage.py", "startapp", custom_app_name], check=True)
    except subprocess.CalledProcessError:
        click.echo(f"Failed to create app {custom_app_name}.")
        return

    # Create auth_app
    click.echo("Creating auth_app...")
    try:
        subprocess.run(["python", "manage.py", "startapp", "auth_app"], check=True)
    except subprocess.CalledProcessError:
        click.echo("Failed to create auth_app.")
        return

    # Set up Jinja2 environment
    env = Environment(
        loader=PackageLoader("porosdjango", "templates"), autoescape=select_autoescape()
    )

    # Create auth_app/models.py
    click.echo("Setting up custom User model...")
    models_template = env.get_template("models.py.j2")
    with open(os.path.join("auth_app", "models.py"), "w") as f:
        f.write(models_template.render())

    # Modify settings.py
    click.echo("Updating settings.py...")
    settings_path = os.path.join(project_app_name, "settings.py")

    try:
        # Read existing settings.py
        with open(settings_path, "r") as f:
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
                # Insert our apps before the closing bracket
                lines.insert(app_list_end, f"    '{custom_app_name}',")
                lines.insert(
                    app_list_end,
                    "auth_app",
                )
                lines.insert(
                    app_list_end,
                    "rest_framework",
                )

                # Add AUTH_USER_MODEL at the end
                lines.append("\n# Custom user model")
                lines.append("AUTH_USER_MODEL = 'auth_app.User'")

                # Write the modified settings back
                with open(settings_path, "w") as f:
                    f.write("\n".join(lines))
            else:
                click.echo(
                    "Could not locate INSTALLED_APPS in settings.py. Manual update required."
                )
        else:
            click.echo(
                "Could not find INSTALLED_APPS in settings.py. Manual update required."
            )
    except Exception as e:
        click.echo(f"Failed to update settings.py: {e}")
        return

    # Create requirements.txt
    click.echo("Creating requirements.txt...")
    with open("requirements.txt", "w") as f:
        f.write("Django==5.0.7\ndjangorestframework==3.15.2\n")

    # Create .gitignore
    click.echo("Fetching .gitignore for Django...")
    try:
        gitignore_url = "https://www.toptal.com/developers/gitignore/api/django"
        response = requests.get(gitignore_url)
        if response.status_code == 200:
            with open(".gitignore", "w") as f:
                f.write(response.text)
        else:
            click.echo("Failed to fetch .gitignore. Creating a basic one...")
            with open(".gitignore", "w") as f:
                f.write(
                    "__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nenv/\nbuild/\n"
                )
    except Exception as e:
        click.echo(f"Failed to create .gitignore: {e}")

    # Run migrations
    click.echo("Running migrations...")
    try:
        subprocess.run(["python", "manage.py", "makemigrations"], check=True)
        subprocess.run(["python", "manage.py", "migrate"], check=True)
    except subprocess.CalledProcessError:
        click.echo("Failed to run migrations. You may need to run them manually.")

    click.echo("\nSetup complete!")
    click.echo("\nTo run your project:")
    click.echo("1. pip install -r requirements.txt")
    click.echo("2. python manage.py runserver")
