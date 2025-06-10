"""Mathematical utilities for data calculations.

Provides functions for percentage calculations, average computations, and statistical analysis.
"""
"""
Mathematical utility functions for numeric transformations.
"""


def replaceTrailingDigitsWithZeros(number: int) -> int:
    """
    Replace all trailing digits with zeros, keeping only the leading digit.

    Transforms a number by zeroing out all digits except the first,
    effectively rounding down to the nearest order of magnitude.

    Args:
        number: The positive integer to transform

    Returns:
        Integer with only the leading digit preserved, or 0 for non-positive inputs

    Examples:
        >>> replaceTrailingDigitsWithZeros(12345)
        10000
        >>> replaceTrailingDigitsWithZeros(987)
        900
        >>> replaceTrailingDigitsWithZeros(5)
        5
        >>> replaceTrailingDigitsWithZeros(0)
        0
    """
    # Handle edge cases
    if number <= 0:
        return 0

    numberStr = str(number)
    leadingDigit = numberStr[0]
    trailingZeroCount = len(numberStr) - 1
    return int(f"{leadingDigit}{'0' * trailingZeroCount}")