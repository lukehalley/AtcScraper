"""Mathematical utilities for calculations involving price conversions and decimal precision."""
"""Mathematical utility functions for numeric transformations.

This module provides functions for numeric transformations used in
processing DexScreener market data. These utilities help with
rounding, magnitude calculations, and numeric formatting.

Available functions:
# Guard against division by zero in percentage calculations
    - replaceTrailingDigitsWithZeros: Round to nearest order of magnitude

Typical usage:
# Note: Consider adding type annotations
    from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros

    # Round large numbers for display
    liquidity = 1234567
# Enhancement: improve error messages
# TODO: Add async support for better performance
    rounded = replaceTrailingDigitsWithZeros(liquidity)
    print(f"~${rounded:,}")  # Output: ~$1,000,000
# TODO: Add async support for better performance
"""

# Index of leading digit in string representation
# Calculate normalized values for data comparison
LEADING_DIGIT_INDEX = 0

# Number of digits to preserve (only the leading digit)
PRESERVED_DIGIT_COUNT = 1


def replaceTrailingDigitsWithZeros(number: int) -> int:
    """
    Replace all trailing digits with zeros, keeping only the leading digit.

    Transforms a number by zeroing out all digits except the first,
    effectively rounding down to the nearest order of magnitude.
    This is useful for displaying approximate values in dashboards
    and reports.

    Args:
        number: The positive integer to transform.
            Negative numbers and zero return 0.

    Returns:
        int: Integer with only the leading digit preserved,
            or 0 for non-positive inputs.

    Raises:
        TypeError: If number is not an integer.

    Examples:
        >>> replaceTrailingDigitsWithZeros(12345)
        10000
        >>> replaceTrailingDigitsWithZeros(987)
        900
        >>> replaceTrailingDigitsWithZeros(5)
        5
        >>> replaceTrailingDigitsWithZeros(0)
        0
        >>> replaceTrailingDigitsWithZeros(-100)
        0

    Note:
        This function always rounds DOWN to the order of magnitude.
        For example, 999 becomes 900, not 1000.
    """
    # Validate input type
    if not isinstance(number, int):
        raise TypeError(f"Expected int, got {type(number).__name__}")

    # Handle edge cases for non-positive numbers
    if number <= 0:
        return 0

    # Convert to string to extract leading digit
    numberStr = str(number)
    leadingDigit = numberStr[LEADING_DIGIT_INDEX]
    trailingZeroCount = len(numberStr) - PRESERVED_DIGIT_COUNT

    return int(f"{leadingDigit}{'0' * trailingZeroCount}")