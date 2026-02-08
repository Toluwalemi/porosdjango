from unittest.mock import patch

from click.testing import CliRunner

from porosdjango.cli import cli


def test_create_command_succeeds(mock_subprocess, mock_requests):
    """GIVEN a mocked DjangoProjectBuilder that returns success
    WHEN the 'create' CLI command is invoked with valid inputs (no Docker)
    THEN the command exits with code 0 and the builder
    is called with the correct arguments
    """
    runner = CliRunner()

    with patch("porosdjango.cli.DjangoProjectBuilder") as mock_builder:
        instance = mock_builder.return_value
        instance.setup.return_value = True

        # Input: project_name, create custom app (y), app name, docker (n)
        result = runner.invoke(cli, ["create"], input="config\ny\nmyapp\nn\n")

        assert result.exit_code == 0
        mock_builder.assert_called_with("config", "myapp", False)
        instance.setup.assert_called_once()


def test_create_command_with_docker_succeeds(mock_subprocess, mock_requests):
    """GIVEN a mocked DjangoProjectBuilder that returns success
    WHEN the 'create' CLI command is invoked with Docker enabled
    THEN the builder is called with docker_integration=True
    """
    runner = CliRunner()

    with patch("porosdjango.cli.DjangoProjectBuilder") as mock_builder:
        instance = mock_builder.return_value
        instance.setup.return_value = True

        # Input: project_name, create custom app (y), app name, docker (y)
        result = runner.invoke(cli, ["create"], input="config\ny\nmyapp\ny\n")

        assert result.exit_code == 0
        mock_builder.assert_called_with("config", "myapp", True)
        instance.setup.assert_called_once()


def test_create_with_invalid_name_fails():
    """GIVEN a CLI runner
    WHEN the 'create' command is invoked with an invalid project name (contains hyphens)
    THEN the command exits with code 1 and an error message is displayed
    """
    runner = CliRunner()

    result = runner.invoke(cli, ["create"], input="invalid-name\n")

    assert result.exit_code == 1
    assert "Error" in result.output
