from __future__ import annotations

from porosdjango.constants import RESERVED_NAMES
from porosdjango.exceptions import InvalidAppNameError


def validate_app_name(name: str) -> str:
    """Validate that a name is a legal Django/Python identifier.

    Args:
        name: The app name to validate.

    Returns:
        The validated name.

    Raises:
        InvalidAppNameError: If the name is not valid.
    """
    if not name.isidentifier():
        raise InvalidAppNameError(
            f"'{name}' is not a valid Python identifier. "
            "Use only letters, numbers, and underscores, and don't start with a number."
        )
    if name in RESERVED_NAMES:
        raise InvalidAppNameError(
            f"'{name}' is a reserved Python or Django name and cannot be used."
        )

    return name
