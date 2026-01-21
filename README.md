# porosdjango

[![PyPI version](https://img.shields.io/pypi/v/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![Python](https://img.shields.io/pypi/pyversions/porosdjango.svg)](https://pypi.org/project/porosdjango/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An opinionated CLI tool that bootstraps Django projects with production-ready defaults. Get a custom user model, Django REST Framework, and sensible project structure in seconds.

## Features

- Custom User model out of the box (extends `AbstractUser`)
- Django REST Framework pre-configured
- Configurable project and app names
- Auto-generated `.gitignore` for Django projects
- Automatic dependency installation
- Database migrations run automatically

## Installation

```bash
pip install porosdjango
```

## Quick Start

```bash
# Create a new directory for your project
mkdir myproject && cd myproject

# Run the CLI
porosdjango create
```

You'll be prompted to:
1. Name your Django project app (default: `config`)
2. Optionally create a custom app with your chosen name

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
│   ├── models.py          # Custom User model
│   ├── tests.py
│   └── views.py
├── your_app/              # Your custom app (if created)
├── manage.py
├── requirements.txt
└── .gitignore
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

## Requirements

- Python >= 3.11
- Django >= 5.2

## Development

```bash
# Clone the repository
git clone https://github.com/Toluwalemi/porosdjango.git
cd porosdjango

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

[Toluwalemi](https://github.com/Toluwalemi)
