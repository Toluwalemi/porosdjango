import pytest
from unittest.mock import patch

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run to prevent actual command execution."""
    with patch("porosdjango.cli.subprocess.run") as mock:
        yield mock

@pytest.fixture
def mock_requests():
    """Mock requests.get to prevent network calls."""
    with patch("porosdjango.cli.requests.get") as mock:
        yield mock

@pytest.fixture
def mock_click():
    """Mock click interactions."""
    with patch("porosdjango.cli.click") as mock:
        yield mock
