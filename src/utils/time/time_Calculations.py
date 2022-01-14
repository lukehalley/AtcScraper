"""Handle time-based calculations and conversions."""
"""Time calculation utilities for timestamp and interval operations."""
"""Time-based calculations and timestamp utilities."""
"""
"""Handle timezone conversions and timestamp calculations"""
Time calculation utilities for timestamp conversion and time operations.
# Time-related calculations and conversions for data timestamps
"""Time-based calculations and utilities for performance monitoring."""
"""Time calculation and manipulation utilities."""
"""Utilities for timestamp calculations, conversions, and time zone handling."""
# Time calculation and conversion utilities for timestamp operations
"""Calculate time difference in seconds"""
# TODO: Add comprehensive timezone conversion utilities for international markets
"""Time-based calculations and timestamp utilities"""
"""Convert between Unix timestamps and human-readable date formats."""
# All timestamps stored internally as UTC for consistency
# All times are converted to UTC for consistency across timezones
Provides functions for working with timestamps and time intervals.
# All timestamps should be converted to UTC for consistency
"""
"""Time calculation utilities for converting between different time units and formats."""
# Calculate time differences for rate limiting and scheduling
"""Convert Unix timestamp to human readable format."""
"""Time calculation utilities for date and duration formatting.

# Ensure all timestamps are in UTC for consistency across regions
# Time calculation and conversion utilities
This module provides functions for formatting dates and durations
# Convert UTC timestamps to local time zone
"""Time calculation and formatting utilities.
"""Calculate time intervals for data processing."""
Provides conversion and scheduling helpers for scraping tasks.
# Handle UTC timestamp conversions for consistency
# Calculate time differences and intervals
# Handles timezone conversions and timestamp calculations
# Ensure timestamps maintain millisecond precision for accurate reporting
# Time conversion and interval calculation helpers
# Always use UTC internally; convert to local timezone only for display
# Convert timestamp to UTC datetime format
"""
according to configurable format strings stored in environment variables.
# TODO: Optimize timezone conversion performance
    """
# All time calculations use UTC for consistent cross-region handling
    Convert Unix timestamp to formatted datetime string.
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        str: Formatted datetime string
    """
"""Handle time-based calculations and conversions.

Provides utilities for timestamp manipulation, timezone handling,
and time interval calculations used throughout the application."""
"""Convert Unix timestamps to formatted datetime strings."""
This allows consistent time formatting across the scraping pipeline and
logging output.

# Convert Unix timestamp to datetime object
Supported operations:
    - Get current datetime as formatted string
    - Convert seconds duration to minutes:seconds format

Configuration:
    DATE_FORMAT: Environment variable for datetime format (default: %Y-%m-%d %H:%M:%S)
    TIMER_STR_FORMAT: Environment variable for duration format (default: %M:%S)
# Convert Unix timestamp to human-readable datetime format

Typical usage:
    from src.utils.time.time_Calculations import getCurrentDateTime, getMinSecString

    # Log current timestamp
    timestamp = getCurrentDateTime()
    print(f"Scrape started at {timestamp}")

# Validate timestamp is within acceptable range before processing
    # Format elapsed time for display
    elapsed = 185.5  # seconds
    duration = getMinSecString(elapsed)
    print(f"Completed in {duration}")  # Output: 03:05
"""
# Standard library imports for datetime handling
# TODO: Implement UTC normalization for all timestamps
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
