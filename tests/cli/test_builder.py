from unittest.mock import MagicMock, patch

from porosdjango.cli import DjangoProjectBuilder, DjangoCommands


def test_setup_succeeds(mock_subprocess, mock_requests, mock_click):
    """GIVEN a DjangoProjectBuilder configured with a project and app name
    WHEN setup is called with all dependencies mocked
    THEN all scaffold, command, and settings steps are executed in order and setup returns True
    """
    builder = DjangoProjectBuilder("testproj", "testapp")

    builder.scaffold = MagicMock()
    builder.settings = MagicMock()

    with patch.object(DjangoCommands, 'startproject') as mock_startproject, \
         patch.object(DjangoCommands, 'startapp') as mock_startapp, \
         patch.object(DjangoCommands, 'install_dependencies') as mock_install, \
         patch.object(DjangoCommands, 'run_migrations') as mock_migrate:

        success = builder.setup()

        assert success is True
        builder.scaffold.create_requirements.assert_called_once()
        mock_install.assert_called_once()
        mock_startproject.assert_called_with("testproj")
        mock_startapp.assert_any_call("testapp")
        mock_startapp.assert_any_call("auth_app")
        builder.scaffold.create_helpers_module.assert_called_once()
        builder.scaffold.create_auth_app_files.assert_called_once()
        builder.settings.add_apps_and_auth.assert_called_with("testapp")
        mock_migrate.assert_called_once()
