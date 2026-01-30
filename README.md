# porosdjango

[![PyPI version](https://img.shields.io/pypi/v/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![Python](https://img.shields.io/pypi/pyversions/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An opinionated CLI tool that bootstraps Django projects with production-ready defaults. Get a custom user model, Django REST Framework, and sensible project structure in seconds.

## Features

- Custom User model out of the box (email-based authentication)
- Django REST Framework pre-configured
- Helpers module with `BaseModel` (UUID primary key, timestamps, soft delete)
- Configurable project and app names
- Input validation for project and app names
- Auto-generated `.gitignore` for Django projects
- Automatic dependency installation
- Database migrations run automatically

## Prerequisites

- Python 3.11 or higher
- pip (comes with Python)

To check your Python version:

```bash
python --version
```

If you see something below 3.11, you'll need to upgrade Python before using porosdjango.

## Usage Guide

This is a step-by-step guide to creating a new Django project using porosdjango.

### Step 1: Create and activate a virtual environment

It's recommended to use a virtual environment so your project dependencies are isolated from your system Python.

**macOS / Linux:**

```bash
mkdir myproject
cd myproject
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
mkdir myproject
cd myproject
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
mkdir myproject
cd myproject
python -m venv .venv
.venv\Scripts\activate.bat
```

Once activated, your terminal prompt will show `(.venv)` at the beginning.

### Step 2: Install porosdjango

```bash
pip install porosdjango
```

This installs porosdjango along with its dependencies (Django, Click, Jinja2, and Requests).

### Step 3: Create your project

```bash
porosdjango create
```

You'll be walked through an interactive setup:

1. **Project app name** — This is the name of your Django configuration module (the folder that contains `settings.py`, `urls.py`, etc.). The default is `config`, which is a common convention. Press Enter to accept the default, or type a name like `mysite` or `core`.

2. **Custom app** — You'll be asked if you want to create a custom app. If you say yes, you'll be prompted for the app name (e.g., `blog`, `accounts`, `products`). This is the app where you'll write most of your project-specific code (models, views, etc.).

Here's what a typical session looks like:

```
$ porosdjango create
What would you like to name your Django project app (default: config)? config
Would you like to create a custom app? [Y/n]: y
What would you like to name your application? blog
Creating requirements.txt...
Installing dependencies...
Dependencies installed successfully.
Creating Django project with app name 'config'...
Creating application 'blog'...
Creating helpers module...
Creating auth_app...
Setting up custom User model and UserManager...
Updating settings.py...
Creating .gitignore...
Running migrations...

Setup complete!

Run your project with:
  python manage.py runserver
```

### Step 4: Run the development server

```bash
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/`. You should see the Django welcome page.

### Step 5: Create a superuser (optional)

To access the Django admin panel at `http://127.0.0.1:8000/admin/`:

```bash
python manage.py createsuperuser
```

Since porosdjango sets up an email-based User model, you'll be prompted for an email and password (not a username).

### Step 6: Start building

You now have a production-ready Django project. Here are some common next steps:

- Add models to your custom app (e.g., `blog/models.py`)
- Your models can extend `BaseModel` from the helpers module to get UUID primary keys, `created_at`, `updated_at`, and `deleted_at` fields for free:

```python
from helpers.db_helpers import BaseModel
from django.db import models

class Post(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
```

- Create views and URL patterns in your custom app
- Add DRF serializers and viewsets for your API
- Run `python manage.py makemigrations && python manage.py migrate` after adding or changing models

## What Gets Generated

```
myproject/
├── config/                 # Your Django project (or custom name)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Pre-configured with your apps
│   ├── urls.py
│   └── wsgi.py
├── auth_app/              # Custom user model app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── managers.py        # Custom UserManager
│   ├── models.py          # Custom User model (email-based)
│   ├── tests.py
│   └── views.py
├── helpers/               # Base model utilities
│   ├── __init__.py
│   └── db_helpers.py      # BaseModel with UUID, timestamps, soft delete
├── your_app/              # Your custom app (if created)
├── manage.py
├── requirements.txt       # Pinned Django and DRF versions
└── .gitignore             # Django-specific gitignore
```

## Generated Configuration

The tool automatically configures `settings.py` with:

```python
INSTALLED_APPS = [
    # ... default Django apps
    'rest_framework',
    'auth_app',
    'your_app',  # if created
]

AUTH_USER_MODEL = 'auth_app.User'
```

## App Naming Rules

Project and app names must be valid Python identifiers:
- Use only letters, numbers, and underscores
- Don't start with a number
- Don't use Python reserved words (`class`, `import`, `for`, etc.)
- Don't use Django reserved names (`django`, `test`, `site`, `admin`)

Valid examples: `blog`, `my_app`, `products`, `user_profiles`

Invalid examples: `my-app` (hyphens), `2fast` (starts with number), `class` (reserved word)

## Development

```bash
# Clone the repository
git clone https://github.com/Toluwalemi/porosdjango.git
cd porosdjango

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

[Toluwalemi](https://github.com/Toluwalemi)
