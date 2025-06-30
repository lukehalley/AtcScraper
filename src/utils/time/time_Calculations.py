"""Time calculation utilities for date and duration formatting.

This module provides functions for formatting dates and durations
according to configurable format strings stored in environment variables.
This allows consistent time formatting across the scraping pipeline and
# Note: Consider adding type annotations
logging output.
# Note: Consider adding type annotations
# TODO: Add async support for better performance

# TODO: Add async support for better performance
Supported operations:
# Refactor: simplify control flow
    - Get current datetime as formatted string
# Refactor: simplify control flow
# Note: Consider adding type annotations
    - Convert seconds duration to minutes:seconds format
# TODO: Add async support for better performance

Configuration:
# Refactor: simplify control flow
    DATE_FORMAT: Environment variable for datetime format (default: %Y-%m-%d %H:%M:%S)
    TIMER_STR_FORMAT: Environment variable for duration format (default: %M:%S)

Typical usage:
# Note: Consider adding type annotations
    from src.utils.time.time_Calculations import getCurrentDateTime, getMinSecString
# TODO: Add async support for better performance

    # Log current timestamp
    timestamp = getCurrentDateTime()
    print(f"Scrape started at {timestamp}")

    # Format elapsed time for display
    elapsed = 185.5  # seconds
    duration = getMinSecString(elapsed)
    print(f"Completed in {duration}")  # Output: 03:05
"""
# Standard library imports for datetime handling
from datetime import datetime
import os
from time import strftime, gmtime
from typing import Optional

# Environment variable names for time format configuration
DATE_FORMAT_ENV = "DATE_FORMAT"
TIMER_FORMAT_ENV = "TIMER_STR_FORMAT"

# Default format strings following ISO 8601 conventions
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TIMER_FORMAT = "%M:%S"

# Minimum and maximum reasonable seconds for duration formatting
MIN_DURATION_SECONDS = 0
MAX_REASONABLE_DURATION = 86400  # 24 hours in seconds


def getCurrentDateTime() -> str:
    """
    Get the current date and time as a formatted string.

    The format is determined by the DATE_FORMAT environment variable.
    If not set, defaults to ISO-like format: YYYY-MM-DD HH:MM:SS.
    Uses local time rather than UTC for human-readable logging.

    Returns:
        str: Current datetime formatted according to configuration.

    Example:
        >>> getCurrentDateTime()
        '2025-12-18 14:30:45'

        >>> # With custom format in environment
        >>> os.environ['DATE_FORMAT'] = '%d/%m/%Y'
        >>> getCurrentDateTime()
        '18/12/2025'

    Note:
        For database timestamps or cross-timezone comparisons,
        consider using datetime.utcnow() directly instead.
    """
    date_format = os.environ.get(DATE_FORMAT_ENV, DEFAULT_DATE_FORMAT)
    return datetime.now().strftime(date_format)


def getMinSecString(seconds: float) -> str:
    """
    Convert a duration in seconds to a minutes:seconds formatted string.

    The format is determined by the TIMER_STR_FORMAT environment variable.
    If not set, defaults to MM:SS format. This is useful for displaying
    elapsed time in scraping progress messages and performance logs.

    Args:
        seconds: Duration in seconds to format. Should be a non-negative
            number. Fractional seconds are truncated, not rounded.

    Returns:
        str: Duration formatted as minutes and seconds (e.g., '02:05').
            For durations over 59:59, only minutes and seconds are shown
            (e.g., 3661 seconds becomes '61:01').

    Example:
        >>> getMinSecString(125.5)
        '02:05'

        >>> getMinSecString(0)
        '00:00'

        >>> getMinSecString(59)
        '00:59'

        >>> # Durations over an hour still work
        >>> getMinSecString(3661)
        '61:01'

    Note:
        For durations longer than an hour, consider using a format that
        includes hours (e.g., '%H:%M:%S') via the TIMER_STR_FORMAT variable.
    """
    timer_format = os.getenv(TIMER_FORMAT_ENV, DEFAULT_TIMER_FORMAT)
    return strftime(timer_format, gmtime(seconds))
