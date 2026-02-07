import pytest

from porosdjango.cli import SettingsModifier
from porosdjango.exceptions import SettingsUpdateError


def test_add_apps_and_auth_succeeds(tmp_path):
    """GIVEN a settings.py file with a default INSTALLED_APPS list
    WHEN add_apps_and_auth is called with a custom app name
    THEN the settings file contains the custom app,
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
