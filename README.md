# porosdjango

[![PyPI version](https://img.shields.io/pypi/v/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![Python](https://img.shields.io/pypi/pyversions/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![Tests](https://github.com/Toluwalemi/porosdjango/actions/workflows/test.yml/badge.svg)](https://github.com/Toluwalemi/porosdjango/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/Toluwalemi/porosdjango/graph/badge.svg)](https://codecov.io/gh/Toluwalemi/porosdjango)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An opinionated CLI tool that bootstraps Django projects with production-ready defaults. Get a custom user model, Django REST Framework, optional Docker integration with full observability, and sensible project structure in seconds.

## Features

- Custom User model out of the box (email-based authentication)
- Django REST Framework pre-configured
- Helpers module with `BaseModel` (UUID primary key, timestamps, soft delete)
- Configurable project and app names
- Input validation for project and app names
- Auto-generated `.gitignore` for Django projects
- Automatic dependency installation
- Database migrations run automatically
- Optional Docker integration with:
  - PostgreSQL, Redis, Nginx, and Celery (worker, beat, flower)
  - Prometheus + Grafana monitoring with pre-built dashboards
  - Mailpit for local email testing
  - Environment-based configuration via `.env`

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

3. **Docker integration** — You'll be asked if you want Docker support. If you say yes, you'll provide a project name used for service naming, and the tool will generate a full Docker Compose stack with PostgreSQL, Redis, Celery, Nginx, Prometheus, Grafana, and more.

Here's what a typical session looks like:

```
$ porosdjango create
What would you like to name your Django project app (default: config)? config
Would you like to create a custom app? [Y/n]: y
What would you like to name your application? blog
Would you like to add Docker integration? [y/N]: y
What is the name of your project? myproject
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
Setting up Docker integration...
Creating Docker infrastructure files...
Updating settings for Docker...

Setup complete!

Run your project with:
  python manage.py runserver

To start with Docker:
  cp .env.example .env
  docker compose up --build
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

### Base project

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

### With Docker integration

When you opt in to Docker, these additional files are generated:

```
myproject/
├── config/
│   ├── __init__.py        # Updated with Celery auto-discovery
│   ├── celery.py          # Celery app configuration
│   └── settings.py        # Updated with Docker-aware settings
├── docker-compose.yml     # Full multi-service stack
├── .dockerignore
├── .env.example           # Environment variable template
└── infrastructure/docker/
    ├── Dockerfile
    ├── scripts/
    │   ├── dev.sh             # Django dev server entrypoint
    │   ├── celery_worker.sh   # Celery worker entrypoint
    │   ├── celery_beat.sh     # Celery beat entrypoint
    │   └── flower.sh          # Flower monitoring entrypoint
    ├── nginx/
    │   └── nginx.conf
    ├── prometheus/
    │   ├── prometheus.yml
    │   └── alert_rules.yml
    ├── alertmanager/
    │   └── alertmanager.yml
    └── grafana/
        └── provisioning/
            ├── datasources/
            │   └── datasource.yml
            └── dashboards/
                ├── dashboard.yml
                └── json/
                    ├── django-app.json
                    ├── infrastructure.json
                    └── celery.json
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

### Docker settings

When Docker integration is enabled, `settings.py` is further updated with:

- **Environment-based config** — `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` read from environment variables with sensible defaults
- **PostgreSQL** — Uses PostgreSQL when `POSTGRES_DB` is set, falls back to SQLite otherwise
- **Redis cache** — Configured via `REDIS_URL`
- **Celery** — Broker and result backend via Redis, with `django-celery-beat` scheduler
- **Prometheus** — `django_prometheus` added to apps and middleware, metrics endpoint at `/metrics`
- **Email** — Configured for Mailpit in development (SMTP on port 1025, UI at `localhost:8025`)
- **Static files** — `STATIC_ROOT` set for Nginx to serve collected static files

### Docker services

The generated `docker-compose.yml` includes 17 services:

| Category | Services |
|---|---|
| **Application** | Django (web), Celery worker, Celery beat, Flower |
| **Data** | PostgreSQL 16, Redis 7 |
| **Reverse proxy** | Nginx |
| **Email** | Mailpit (SMTP + web UI) |
| **Monitoring** | Prometheus, Grafana (with 3 pre-built dashboards), Alertmanager |
| **Exporters** | Node, cAdvisor, PostgreSQL, Redis, Nginx, Celery |

### Getting started with Docker

```bash
# Copy the environment template and adjust as needed
cp .env.example .env

# Build and start all services
docker compose up --build
```

Once running, the key endpoints are:

| Service | URL |
|---|---|
| Django | `http://localhost:8000` |
| Nginx | `http://localhost` |
| Grafana | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |
| Flower | `http://localhost:5555` |
| Mailpit | `http://localhost:8025` |

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
