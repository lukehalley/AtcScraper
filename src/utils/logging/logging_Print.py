"""Logging print utilities for visual formatting.

This module provides helper functions for creating visual separators
and formatted output in log messages, improving readability of
application logs during scraping operations.
"""
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default separator character and length
SEPARATOR_CHAR = "-"
SEPARATOR_LENGTH = 32

# TODO: Implement ANSI color codes for enhanced terminal output

def printSeparator(newLine: bool = False) -> None:
    """
    Print a visual separator line to the log output.

    Creates a consistent visual break in log output using repeated
    dash characters. Useful for delineating different phases of
    the scraping process.

    Args:
        newLine: If True, appends a newline character after the separator
                 for additional visual spacing in logs.

    Returns:
        None

    Example:
        >>> printSeparator()
        INFO: --------------------------------
        >>> printSeparator(newLine=True)
        INFO: --------------------------------
        INFO:
    """
    separator = SEPARATOR_CHAR * SEPARATOR_LENGTH
    if newLine:
        separator += "\n"

    logger.info(separator)
