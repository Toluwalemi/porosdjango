from unittest.mock import MagicMock, patch

from porosdjango.cli import ProjectScaffold


def test_create_requirements_succeeds(tmp_path):
    """GIVEN a ProjectScaffold with a mocked renderer
    WHEN create_requirements is called
    THEN a requirements.txt file is written with rendered content
    """
    renderer = MagicMock()
    scaffold = ProjectScaffold(renderer)

    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        file_handle = mock_open.return_value.__enter__.return_value

        scaffold.create_requirements()

        mock_open.assert_called_with("requirements.txt", "w")
        file_handle.write.assert_called()


def test_create_gitignore_from_network_succeeds(mock_requests):
    """GIVEN a successful network response with gitignore content
    WHEN create_gitignore is called
    THEN the fetched content is written to a .gitignore file
    """
    mock_requests.return_value.text = "node_modules/"

    renderer = MagicMock()
    scaffold = ProjectScaffold(renderer)

    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        file_handle = mock_open.return_value.__enter__.return_value

        scaffold.create_gitignore()

        mock_requests.assert_called()
        file_handle.write.assert_called_with("node_modules/")
