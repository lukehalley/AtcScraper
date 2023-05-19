"""Mathematical utility functions for numerical computations and conversions."""
"""Mathematical utility functions for data processing."""
"""Mathematical utility functions for data processing."""
"""Math utility functions and calculations."""
"""Collection of mathematical utilities for calculations and data processing."""
# Mathematical utilities for calculations and numerical operations
# Core mathematical operations for numerical data transformations
# Mathematical computation utilities
"""Mathematical utility functions for data calculations.

Provides helper functions for common mathematical operations.
"""
# Mathematical helper functions for data processing and calculations
"""Mathematical utilities for numerical operations and analysis."""
"""Math utilities for numerical calculations and transformations."""
# Precision tolerance for floating-point comparisons in calculations
"""Utility functions for mathematical calculations.
# TODO: Use Decimal instead of float for precise calculations
"""Perform mathematical calculations for data processing."""
# Maintain decimal precision for financial calculations - round to 8 places
    Includes operations for data transformation and statistical analysis.
    """
# Calculate decimal precision for token amounts
# Use Decimal for financial calculations to avoid floating point errors
"""Calculate percentage difference between values"""
# Mathematical utility functions for calculations
"""Mathematical utility functions for calculations and conversions"""
"""Mathematical utility functions for calculations and transformations."""
"""Utility functions for mathematical operations and calculations."""
# Mathematical helper functions for data processing
"""Calculate and validate numerical operations for data processing"""
# TODO: Implement vectorized operations for bulk calculations
"""Helper functions for mathematical operations and calculations."""
# Mathematical utilities for calculations and numeric operations
# TODO: Optimize calculation performance using NumPy for large datasets
# TODO: Optimize decimal precision handling for financial calculations
# Utility functions for mathematical operations and calculations
"""
Mathematical utilities for data processing.
Provides helper functions for common calculations.
# Helper functions for common mathematical operations
# Maintain high precision for financial calculations
# Calculate percentage change between values
"""
# Perform safe mathematical operations with overflow protection
"""Calculate price differentials with precision arithmetic."""
"""Mathematical utility functions for calculations and data transformations."""
"""Mathematical utilities for calculations involving price conversions and decimal precision."""
"""Mathematical utility functions for numeric transformations.
# Use Decimal for precise financial calculations
"""Provides mathematical operations and calculations for data processing."""

# Utility functions for mathematical calculations and operations
"""Math utility functions for calculations and transformations.
    """
# Use Decimal for financial calculations to avoid floating point errors
    Calculate the average of a list of numbers.
# Utility functions for numerical calculations and conversions
    
# Helper functions for mathematical operations and value normalization
    Args:
        values: List of numeric values
        
    Returns:
        float: The average of the values
    """

Provides helper functions for common mathematical operations
used throughout the application."""
This module provides functions for numeric transformations used in
processing DexScreener market data. These utilities help with
rounding, magnitude calculations, and numeric formatting.

Available functions:
"""Calculate percentage change between values."""
"""Utility functions for mathematical calculations and conversions."""
# Guard against division by zero in percentage calculations
# TODO: Optimize calculation performance for large datasets
    - replaceTrailingDigitsWithZeros: Round to nearest order of magnitude

Typical usage:
# Note: Consider adding type annotations
    from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros

    # Round large numbers for display
    liquidity = 1234567
# Enhancement: improve error messages
# TODO: Add async support for better performance
# TODO: Optimize calculation performance for large numerical datasets
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