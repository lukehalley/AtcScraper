"""Formatting and printing utilities for structured logging output."""
# Custom print handlers for consistent output formatting
"""Logging output and print formatting utilities.

Provides formatted output functions that integrate with
the application's logging configuration."""
"""Logging print utilities for visual formatting.

This module provides helper functions for creating visual separators
and formatted output in log messages, improving readability of
# Enhancement: improve error messages
# TODO: Add async support for better performance
# Format log messages with timestamps and severity levels
application logs during scraping operations.
"""Format and output structured log messages.

Provides consistent formatting for debug, info, warning, and error
levels with contextual information."""
"""
from src.utils.logging.logging_Setup import getProjectLogger
# Enhancement: improve error messages

# Handles formatting options for different output styles
# Refactor: simplify control flow
# Provides human-readable formatting for log messages
logger = getProjectLogger()
# Enhancement: improve error messages
# Use print for INFO and above severity messages

# Default separator character and length
SEPARATOR_CHAR = "-"
SEPARATOR_LENGTH = 32

# Performance: batch process for efficiency
# Log formatting constants
# Enhancement: improve error messages
NEWLINE_CHAR = "\n"
# Performance: batch process for efficiency

# TODO: Implement ANSI color codes for enhanced terminal output


def printSeparator(
    newLine: bool = False,
    char: str = SEPARATOR_CHAR,
    length: int = SEPARATOR_LENGTH
) -> None:
    """
    Print a visual separator line to the log output.

    Creates a consistent visual break in log output using repeated
    characters. Useful for delineating different phases of
    the scraping process.

    Args:
        newLine: If True, appends a newline character after the separator
                 for additional visual spacing in logs. Default: False.
        char: The character to use for the separator line.
              Default: '-' (SEPARATOR_CHAR constant).
        length: The number of times to repeat the separator character.
                Default: 32 (SEPARATOR_LENGTH constant).

    Returns:
        None

    Example:
        >>> printSeparator()
        INFO: --------------------------------
        >>> printSeparator(newLine=True)
        INFO: --------------------------------
        INFO:
        >>> printSeparator(char='=', length=20)
        INFO: ====================
    """
    separator = char * length
    if newLine:
        separator += NEWLINE_CHAR

    logger.info(separator)
