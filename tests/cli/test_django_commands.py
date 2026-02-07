import sys

from porosdjango.cli import DjangoCommands


def test_startproject_succeeds(mock_subprocess):
    """GIVEN a mocked subprocess environment
    WHEN DjangoCommands.startproject is called with a project name
    THEN django-admin startproject is invoked with the correct arguments
    """
    DjangoCommands.startproject("myproject")
    mock_subprocess.assert_called_with(
        ["django-admin", "startproject", "myproject", "."], check=True
    )


def test_startapp_succeeds(mock_subprocess):
    """GIVEN a mocked subprocess environment
    WHEN DjangoCommands.startapp is called with an app name
    THEN manage.py startapp is invoked with the correct arguments
    """
    DjangoCommands.startapp("myapp")
    mock_subprocess.assert_called_with(
        [sys.executable, "manage.py", "startapp", "myapp"], check=True
    )
