from unittest.mock import MagicMock, patch

from porosdjango.cli import DjangoCommands, DjangoProjectBuilder


def test_setup_succeeds(mock_subprocess, mock_requests, mock_click):
    """GIVEN a DjangoProjectBuilder configured with a project and app name
    WHEN setup is called with all dependencies mocked
    THEN all scaffold, command, and settings steps execute
    and setup returns True
    """
    builder = DjangoProjectBuilder("testproj", "testapp")

    builder.scaffold = MagicMock()
    builder.settings = MagicMock()

    with (
        patch.object(DjangoCommands, "startproject") as mock_startproject,
        patch.object(DjangoCommands, "startapp") as mock_startapp,
        patch.object(DjangoCommands, "install_dependencies") as mock_install,
        patch.object(DjangoCommands, "run_migrations") as mock_migrate,
    ):
        success = builder.setup()

        assert success is True
        builder.scaffold.create_requirements.assert_called_once_with(docker=False)
        mock_install.assert_called_once()
        mock_startproject.assert_called_with("testproj")
        mock_startapp.assert_any_call("testapp")
        mock_startapp.assert_any_call("auth_app")
        builder.scaffold.create_helpers_module.assert_called_once()
        builder.scaffold.create_auth_app_files.assert_called_once()
        builder.settings.add_apps_and_auth.assert_called_with("testapp")
        builder.scaffold.create_docker_setup.assert_not_called()
        builder.settings.add_docker_settings.assert_not_called()
        mock_migrate.assert_called_once()


def test_setup_with_docker_integration_calls_docker_setup_succeeds(
    mock_subprocess, mock_requests, mock_click
):
    """GIVEN a DjangoProjectBuilder with docker_integration=True
    WHEN setup is called
    THEN create_docker_setup is called with the project name
    and requirements include docker dependencies
    """
    builder = DjangoProjectBuilder(
        "testproj", "testapp", docker_integration=True, docker_project_name="mysite"
    )

    builder.scaffold = MagicMock()
    builder.settings = MagicMock()

    with (
        patch.object(DjangoCommands, "startproject"),
        patch.object(DjangoCommands, "startapp"),
        patch.object(DjangoCommands, "install_dependencies"),
        patch.object(DjangoCommands, "run_migrations"),
    ):
        success = builder.setup()

        assert success is True
        builder.scaffold.create_requirements.assert_called_once_with(docker=True)
        builder.scaffold.create_docker_setup.assert_called_once_with(
            "testproj", "mysite"
        )
        builder.settings.add_docker_settings.assert_called_once_with(
            "testproj", "mysite"
        )


def test_setup_without_docker_skips_docker_setup_succeeds(
    mock_subprocess, mock_requests, mock_click
):
    """GIVEN a DjangoProjectBuilder with docker_integration=False
    WHEN setup is called
    THEN create_docker_setup is not called
    """
    builder = DjangoProjectBuilder("testproj", "testapp", docker_integration=False)

    builder.scaffold = MagicMock()
    builder.settings = MagicMock()

    with (
        patch.object(DjangoCommands, "startproject"),
        patch.object(DjangoCommands, "startapp"),
        patch.object(DjangoCommands, "install_dependencies"),
        patch.object(DjangoCommands, "run_migrations"),
    ):
        success = builder.setup()

        assert success is True
        builder.scaffold.create_requirements.assert_called_once_with(docker=False)
        builder.scaffold.create_docker_setup.assert_not_called()
        builder.settings.add_docker_settings.assert_not_called()
