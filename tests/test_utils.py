import pytest

from porosdjango.constants import RESERVED_NAMES
from porosdjango.exceptions import InvalidAppNameError
from porosdjango.utils import validate_app_name


def test_validate_valid_name_succeeds():
    """GIVEN valid Python identifier app names
    WHEN validate_app_name is called with each name
    THEN the same name is returned without error
    """
    assert validate_app_name("my_app") == "my_app"
    assert validate_app_name("config") == "config"
    assert validate_app_name("api_v1") == "api_v1"


def test_validate_name_with_invalid_chars_fails():
    """GIVEN app names containing invalid characters (hyphens, leading digits, dots)
    WHEN validate_app_name is called with each name
    THEN an InvalidAppNameError is raised with 'is not a valid Python identifier'
    """
    with pytest.raises(InvalidAppNameError, match="is not a valid Python identifier"):
        validate_app_name("my-app")

    with pytest.raises(InvalidAppNameError, match="is not a valid Python identifier"):
        validate_app_name("1app")

    with pytest.raises(InvalidAppNameError, match="is not a valid Python identifier"):
        validate_app_name("my.app")


def test_validate_reserved_name_fails():
    """GIVEN app names that are reserved Python or Django keywords
    WHEN validate_app_name is called with each reserved name
    THEN an InvalidAppNameError is raised with 'is a reserved Python or Django name'
    """
    # Test a few reserved names
    reserved_to_test = list(RESERVED_NAMES)[:3] if RESERVED_NAMES else ["django"]

    for name in reserved_to_test:
        with pytest.raises(
            InvalidAppNameError, match="is a reserved Python or Django name"
        ):
            validate_app_name(name)
