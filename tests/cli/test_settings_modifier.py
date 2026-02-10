import pytest

from porosdjango.cli import SettingsModifier
from porosdjango.exceptions import SettingsUpdateError

DJANGO_SETTINGS_FIXTURE = """\
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-test-key"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'rest_framework',
    # local
    'auth_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth_app.User'
"""


def test_add_apps_and_auth_succeeds(tmp_path):
    """GIVEN a settings.py file with a default INSTALLED_APPS list
    WHEN add_apps_and_auth is called with a custom app name
    THEN the settings file contains section comments, the custom app,
    auth_app, rest_framework, and AUTH_USER_MODEL
    """
    settings_file = tmp_path / "settings.py"
    settings_content = """
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
]
"""
    settings_file.write_text(settings_content)

    modifier = SettingsModifier(str(settings_file))
    modifier.add_apps_and_auth("custom_app")

    new_content = settings_file.read_text()

    assert "'custom_app'," in new_content
    assert "'auth_app'," in new_content
    assert "'rest_framework'," in new_content
    assert "AUTH_USER_MODEL = 'auth_app.User'" in new_content
    assert "# third-party" in new_content
    assert "# local" in new_content


def test_add_apps_with_missing_file_fails():
    """GIVEN a SettingsModifier pointing to a nonexistent file
    WHEN add_apps_and_auth is called
    THEN a SettingsUpdateError is raised with 'Cannot read settings file'
    """
    modifier = SettingsModifier("nonexistent_settings.py")
    with pytest.raises(SettingsUpdateError, match="Cannot read settings file"):
        modifier.add_apps_and_auth("app")


def test_add_apps_with_invalid_format_fails(tmp_path):
    """GIVEN a settings.py file that does not contain INSTALLED_APPS
    WHEN add_apps_and_auth is called
    THEN a SettingsUpdateError is raised with 'Could not find INSTALLED_APPS'
    """
    settings_file = tmp_path / "settings.py"
    settings_file.write_text("DEBUG = True")

    modifier = SettingsModifier(str(settings_file))
    with pytest.raises(SettingsUpdateError, match="Could not find INSTALLED_APPS"):
        modifier.add_apps_and_auth("app")


@pytest.fixture
def docker_settings_file(tmp_path):
    """Create a realistic Django settings.py for docker settings tests."""
    settings_file = tmp_path / "settings.py"
    settings_file.write_text(DJANGO_SETTINGS_FIXTURE)
    return settings_file


def test_add_docker_settings_adds_import_os_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py
    WHEN add_docker_settings is called
    THEN 'import os' is added after 'from pathlib import Path'
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()
    lines = content.split("\n")

    pathlib_idx = next(
        i for i, line in enumerate(lines) if "from pathlib import Path" in line
    )
    assert lines[pathlib_idx + 1] == "import os"


def test_add_docker_settings_updates_secret_key_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with a hardcoded SECRET_KEY
    WHEN add_docker_settings is called
    THEN SECRET_KEY reads from the DJANGO_SECRET_KEY env var
    with the original value as default
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert "DJANGO_SECRET_KEY" in content
    assert "django-insecure-test-key" in content
    assert "os.environ.get(" in content


def test_add_docker_settings_updates_debug_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with DEBUG = True
    WHEN add_docker_settings is called
    THEN DEBUG reads from the DJANGO_DEBUG env var
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert "DJANGO_DEBUG" in content
    assert 'in ("true", "1", "yes")' in content


def test_add_docker_settings_updates_allowed_hosts_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with ALLOWED_HOSTS = []
    WHEN add_docker_settings is called
    THEN ALLOWED_HOSTS reads from the DJANGO_ALLOWED_HOSTS env var
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert "ALLOWED_HOSTS = []" not in content
    assert "DJANGO_ALLOWED_HOSTS" in content
    assert '.split(",")' in content


def test_add_docker_settings_adds_static_root_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with STATIC_URL
    WHEN add_docker_settings is called
    THEN STATIC_ROOT is added after STATIC_URL
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert "STATIC_ROOT" in content
    assert '"staticfiles"' in content


def test_add_docker_settings_adds_docker_apps_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with section comments
    WHEN add_docker_settings is called
    THEN django_prometheus is first in INSTALLED_APPS
    and django_celery_beat is in the third-party section
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()
    lines = content.split("\n")

    app_start = next(i for i, line in enumerate(lines) if "INSTALLED_APPS = [" in line)
    app_entries = [
        lines[i].strip().strip("',")
        for i in range(app_start + 1, len(lines))
        if lines[i].strip()
        and lines[i].strip() != "]"
        and not lines[i].strip().startswith("#")
    ]

    assert app_entries[0] == "django_prometheus"
    assert "django_celery_beat" in app_entries
    # django_celery_beat should appear after rest_framework (third-party section)
    rf_idx = app_entries.index("rest_framework")
    cb_idx = app_entries.index("django_celery_beat")
    assert cb_idx > rf_idx


def test_add_docker_settings_adds_prometheus_middleware_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with MIDDLEWARE
    WHEN add_docker_settings is called
    THEN PrometheusBeforeMiddleware is first and PrometheusAfterMiddleware is last
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()
    lines = content.split("\n")

    mw_start = next(i for i, line in enumerate(lines) if "MIDDLEWARE = [" in line)
    mw_end = next(i for i in range(mw_start, len(lines)) if lines[i].strip() == "]")

    mw_lines = [entry.strip().strip("',") for entry in lines[mw_start + 1 : mw_end]]
    mw_lines = [entry for entry in mw_lines if entry]

    assert mw_lines[0] == "django_prometheus.middleware.PrometheusBeforeMiddleware"
    assert mw_lines[-1] == "django_prometheus.middleware.PrometheusAfterMiddleware"


def test_add_docker_settings_updates_databases_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py with sqlite3 DATABASES
    WHEN add_docker_settings is called
    THEN DATABASES uses PostgreSQL with env vars and SQLite fallback
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert 'if os.environ.get("POSTGRES_DB"):' in content
    assert "django.db.backends.postgresql" in content
    assert "django.db.backends.sqlite3" in content
    assert 'os.environ["POSTGRES_DB"]' in content


def test_add_docker_settings_adds_cache_config_succeeds(docker_settings_file):
    """GIVEN a standard Django settings.py
    WHEN add_docker_settings is called
    THEN Redis cache config is appended
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject")

    content = docker_settings_file.read_text()

    assert "REDIS_URL" in content
    assert "CACHES" in content
    assert "django.core.cache.backends.redis.RedisCache" in content


def test_add_docker_settings_adds_celery_and_email_config_succeeds(
    docker_settings_file,
):
    """GIVEN a standard Django settings.py
    WHEN add_docker_settings is called with a docker_project_name
    THEN full Celery config and email settings are appended
    using the docker project name
    """
    modifier = SettingsModifier(str(docker_settings_file))
    modifier.add_docker_settings("myproject", docker_project_name="coolproject")

    content = docker_settings_file.read_text()

    assert "CELERY_BROKER_URL" in content
    assert "CELERY_RESULT_BACKEND" in content
    assert 'CELERY_ACCEPT_CONTENT = ["json"]' in content
    assert 'CELERY_TASK_SERIALIZER = "json"' in content
    assert 'CELERY_RESULT_SERIALIZER = "json"' in content
    assert "CELERY_TIMEZONE = TIME_ZONE" in content
    assert "CELERY_BEAT_SCHEDULER" in content
    assert "EMAIL_BACKEND" in content
    assert "EMAIL_HOST" in content
    assert "EMAIL_PORT" in content
    assert "EMAIL_USE_TLS" in content
    assert "DEFAULT_FROM_EMAIL" in content
    assert "noreply@coolproject.local" in content


def test_add_docker_settings_with_missing_file_fails():
    """GIVEN a SettingsModifier pointing to a nonexistent file
    WHEN add_docker_settings is called
    THEN a SettingsUpdateError is raised
    """
    modifier = SettingsModifier("nonexistent_settings.py")
    with pytest.raises(SettingsUpdateError, match="Cannot read settings file"):
        modifier.add_docker_settings("myproject")


def test_add_prometheus_urls_succeeds(tmp_path):
    """GIVEN a standard Django urls.py
    WHEN add_prometheus_urls is called
    THEN django_prometheus.urls is included and include is imported
    """
    urls_file = tmp_path / "urls.py"
    urls_file.write_text(
        "from django.contrib import admin\n"
        "from django.urls import path\n"
        "\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "]\n"
    )
    settings_file = tmp_path / "settings.py"
    settings_file.write_text("")

    modifier = SettingsModifier(str(settings_file))
    modifier.add_prometheus_urls()

    content = urls_file.read_text()

    assert "include" in content
    assert "django_prometheus.urls" in content


def test_add_prometheus_urls_with_include_in_docstring_succeeds(tmp_path):
    """GIVEN a Django 6.0 urls.py whose docstring mentions 'include'
    WHEN add_prometheus_urls is called
    THEN include is added to the actual import and django_prometheus.urls is included
    """
    urls_file = tmp_path / "urls.py"
    urls_file.write_text(
        '"""\nURL configuration for config project.\n'
        "Including another URLconf\n"
        "    1. Import the include() function: from django.urls import include, path\n"
        "    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))\n"
        '"""\n'
        "from django.contrib import admin\n"
        "from django.urls import path\n"
        "\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "]\n"
    )
    settings_file = tmp_path / "settings.py"
    settings_file.write_text("")

    modifier = SettingsModifier(str(settings_file))
    modifier.add_prometheus_urls()

    content = urls_file.read_text()

    assert "from django.urls import include, path" in content
    assert "django_prometheus.urls" in content


def test_add_prometheus_urls_with_nonstandard_import_succeeds(tmp_path):
    """GIVEN a urls.py with a non-standard import line (extra spacing)
    WHEN add_prometheus_urls is called
    THEN include is still added and django_prometheus.urls is included
    """
    urls_file = tmp_path / "urls.py"
    urls_file.write_text(
        "from django.contrib import admin\n"
        "from  django.urls  import  path\n"
        "\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "]\n"
    )
    settings_file = tmp_path / "settings.py"
    settings_file.write_text("")

    modifier = SettingsModifier(str(settings_file))
    modifier.add_prometheus_urls()

    content = urls_file.read_text()

    assert "include" in content
    assert "django_prometheus.urls" in content


def test_add_prometheus_urls_with_missing_import_succeeds(tmp_path):
    """GIVEN a urls.py that does not have 'from django.urls import path'
    WHEN add_prometheus_urls is called
    THEN include is prepended and django_prometheus.urls is included
    """
    urls_file = tmp_path / "urls.py"
    urls_file.write_text(
        "from django.contrib import admin\n"
        "import django.urls\n"
        "\n"
        "urlpatterns = [\n"
        "    django.urls.path('admin/', admin.site.urls),\n"
        "]\n"
    )
    settings_file = tmp_path / "settings.py"
    settings_file.write_text("")

    modifier = SettingsModifier(str(settings_file))
    modifier.add_prometheus_urls()

    content = urls_file.read_text()

    assert "from django.urls import include, path" in content
    assert "django_prometheus.urls" in content


def test_add_prometheus_urls_with_missing_file_fails():
    """GIVEN a SettingsModifier pointing to a directory without urls.py
    WHEN add_prometheus_urls is called
    THEN a SettingsUpdateError is raised
    """
    modifier = SettingsModifier("/nonexistent/settings.py")
    with pytest.raises(SettingsUpdateError, match="Cannot read urls.py"):
        modifier.add_prometheus_urls()
