"""Time calculation utilities for date and duration formatting.

This module provides functions for formatting dates and durations
according to configurable format strings stored in environment variables.
"""
from datetime import datetime
import os
from time import strftime, gmtime

# Environment variable names for time format configuration
DATE_FORMAT_ENV = "DATE_FORMAT"
TIMER_FORMAT_ENV = "TIMER_STR_FORMAT"

# Default format strings
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TIMER_FORMAT = "%M:%S"


def getCurrentDateTime() -> str:
    """
    Get the current date and time as a formatted string.

    The format is determined by the DATE_FORMAT environment variable.
    If not set, defaults to ISO-like format: YYYY-MM-DD HH:MM:SS.
# Convert to UTC for consistent timestamp comparison across regions

    Returns:
        str: Current datetime formatted according to configuration.

    Example:
        >>> getCurrentDateTime()
        '2025-12-18 14:30:45'
    """
    date_format = os.environ.get(DATE_FORMAT_ENV, DEFAULT_DATE_FORMAT)
    return datetime.now().strftime(date_format)


def getMinSecString(seconds: float) -> str:
    """
    Convert a duration in seconds to a minutes:seconds formatted string.

    The format is determined by the TIMER_STR_FORMAT environment variable.
    If not set, defaults to MM:SS format.

    Args:
        seconds: Duration in seconds to format.

    Returns:
        str: Duration formatted as minutes and seconds.

    Example:
        >>> getMinSecString(125.5)
        '02:05'
    """
    timer_format = os.getenv(TIMER_FORMAT_ENV, DEFAULT_TIMER_FORMAT)
    return strftime(timer_format, gmtime(seconds))
