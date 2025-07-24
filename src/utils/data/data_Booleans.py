"""
Boolean conversion utilities for handling string to boolean transformations.

Provides robust conversion functions that handle various string representations
of boolean values (e.g., 'true', 'yes', '1', 'on').
"""
from distutils.util import strtobool
from typing import Optional, Union

# Type alias for values that can be converted to boolean
BoolConvertible = Union[str, bool, None]

# Default return value for None/empty inputs
DEFAULT_BOOL_VALUE = False


def strToBool(value: Optional[BoolConvertible]) -> bool:
    """
    Convert a string or boolean value to a boolean.

    Handles various string representations including:
    - True values: 'y', 'yes', 't', 'true', 'on', '1'
    - False values: 'n', 'no', 'f', 'false', 'off', '0'

    Args:
        value: A string or boolean value to convert

    Returns:
        Boolean representation of the input value

    Raises:
        ValueError: If the string value cannot be converted to boolean

    Examples:
        >>> strToBool('yes')
        True
        >>> strToBool('false')
        False
        >>> strToBool(True)
        True
    """
    if isinstance(value, bool):
        return value
    return bool(strtobool(value))
