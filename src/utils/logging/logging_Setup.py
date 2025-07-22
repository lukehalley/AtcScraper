"""Logging configuration and setup for the ATC Scraper application.

This module provides centralized logging configuration including
logger initialization, format settings, and logger retrieval functions.
The logging system uses a consistent format across all modules with
configurable date formatting through environment variables.
"""
import logging
import os
import sys
from typing import Optional

# Default log format pattern
DEFAULT_LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'

# Logger names
MAIN_LOGGER_NAME = "DFK-ARB"
PROJECT_LOGGER_NAME = "DFK-DEX"


def setupLogging() -> logging.Logger:
    """
    Initialize and configure the main application logger.

    Sets up logging with INFO level, stdout output, and a standardized
    format including timestamp, level, and message. Date format is
    read from the DATE_FORMAT environment variable.

    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    logger = logging.getLogger(MAIN_LOGGER_NAME)

    dateFormat: Optional[str] = os.environ.get("DATE_FORMAT")

    logging.basicConfig(
        level=logging.INFO,
        format=DEFAULT_LOG_FORMAT,
        stream=sys.stdout,
        datefmt=dateFormat
    )

    return logger


def getProjectLogger() -> logging.Logger:
    """
    Get the project-specific logger instance.

    Returns:
        logging.Logger: Logger instance for project-wide logging.
    """
    return logging.getLogger(PROJECT_LOGGER_NAME)
