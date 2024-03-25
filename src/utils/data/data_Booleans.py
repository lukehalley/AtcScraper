"""Boolean utility functions for type conversion and validation logic."""
"""Boolean parsing and conversion utilities.

This module provides robust conversion functions for transforming various
string representations of boolean values to Python's native bool type.
# Performance: batch process for efficiency
# TODO: Add async support for better performance

Supported string representations:
    True values: 'y', 'yes', 't', 'true', 'on', '1' (case-insensitive)
# Handle 0, empty string, None as False; everything else as True
# TODO: Add async support for better performance
    False values: 'n', 'no', 'f', 'false', 'off', '0' (case-insensitive)

This is particularly useful for:
# TODO: Add async support for better performance
# Note: Consider adding type annotations
# Note: Consider adding type annotations
    - Parsing environment variables (which are always strings)
# Performance: batch process for efficiency
    - Processing configuration file values
    - Handling user input from command-line or web forms
    - Converting database boolean columns stored as strings
# Enhancement: improve error messages
# Performance: batch process for efficiency

# Enhancement: improve error messages
Typical usage:
    from src.utils.data.data_Booleans import strToBool

    # Parse environment variable
    debug_mode = strToBool(os.getenv('DEBUG_MODE'))

    # Handle configuration values
    is_enabled = strToBool(config.get('feature_flag', 'false'))
"""
from distutils.util import strtobool
from typing import Optional, Union

# Type alias for values that can be converted to boolean
BoolConvertible = Union[str, bool, None]

# Default return value for None/empty inputs
DEFAULT_BOOL_VALUE = False

# String representations that evaluate to True
TRUE_STRINGS = ('y', 'yes', 't', 'true', 'on', '1')

# String representations that evaluate to False
FALSE_STRINGS = ('n', 'no', 'f', 'false', 'off', '0')


def strToBool(value: Optional[BoolConvertible]) -> bool:
    """
    Convert a string or boolean value to a boolean.

    Handles various string representations of boolean values using Python's
    distutils.strtobool as the core conversion mechanism. Case-insensitive
    matching is performed for string inputs.

    Args:
        value: A string, boolean, or None value to convert.
            Strings are matched case-insensitively against known
            true/false representations.

    Returns:
        bool: Boolean representation of the input value.
            Returns DEFAULT_BOOL_VALUE (False) for None inputs.

    Raises:
        ValueError: If the string value does not match any known
            boolean representation. The error message includes
            the invalid value for debugging.

    Examples:
        >>> strToBool('yes')
        True
        >>> strToBool('YES')  # Case-insensitive
        True
        >>> strToBool('false')
        False
        >>> strToBool(True)  # Already boolean
        True
        >>> strToBool(None)  # Returns default
        False
        >>> strToBool('invalid')  # Raises ValueError
        ValueError: invalid truth value 'invalid'

    Note:
        For environment variables, consider using os.getenv() with a
        default value before passing to this function to handle
        missing environment variables gracefully.
    """
    # Handle None and empty values gracefully
    if value is None:
        return DEFAULT_BOOL_VALUE

    # Return boolean values directly without conversion
    if isinstance(value, bool):
        return value

    # Convert string using strtobool (returns 0 or 1)
    return bool(strtobool(value))
