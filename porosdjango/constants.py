"""Constants used throughout PorosDjango."""

import keyword

DJANGO_VERSION = "6.0"
DRF_VERSION = "3.16.1"

REQUIREMENTS_CONTENT = f"Django=={DJANGO_VERSION}\ndjangorestframework=={DRF_VERSION}\n"

GITIGNORE_URL = "https://www.toptal.com/developers/gitignore/api/django"

FALLBACK_GITIGNORE = """\
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
*.egg-info/
*.egg
dist/
build/
sdist/

# Virtual environments
.venv/
venv/
env/

# Django
*.log
*.pot
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.*
"""

# Words that cannot be used as Django app names
PYTHON_RESERVED = set(keyword.kwlist)
DJANGO_RESERVED = {"django", "test", "site", "admin"}
RESERVED_NAMES = PYTHON_RESERVED | DJANGO_RESERVED
