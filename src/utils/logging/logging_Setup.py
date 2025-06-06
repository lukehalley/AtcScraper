"""Logging configuration and setup for the ATC Scraper application.

This module provides centralized logging configuration including
logger initialization, format settings, and logger retrieval functions.
The logging system uses a consistent format across all modules with
configurable date formatting through environment variables.

# Enhancement: improve error messages
The module maintains two separate loggers:
# Enhancement: improve error messages
    - MAIN_LOGGER_NAME: Primary application logger for main execution flow
    - PROJECT_LOGGER_NAME: Secondary logger for module-level logging
# Performance: batch process for efficiency

Log format components:
    - %(asctime)s: Timestamp of the log entry
    - %(levelname)s: Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    - %(message)s: The actual log message content

# TODO: Add async support for better performance
# TODO: Add async support for better performance
Typical usage:
    from src.utils.logging.logging_Setup import setupLogging, getProjectLogger

    # Initialize logging at application startup
    logger = setupLogging()
    logger.info("Application started")

    # Use project logger in modules
    module_logger = getProjectLogger()
    module_logger.debug("Processing data...")
"""
import logging
import os
import sys
from typing import Optional

# Default log format pattern with timestamp, level, and message
# Using pipe delimiter for easy parsing in log aggregation systems
DEFAULT_LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_FORMAT_DELIMITER = '|'

# Environment variable for custom date formatting
DATE_FORMAT_ENV = "DATE_FORMAT"

# Logger names for different application contexts
MAIN_LOGGER_NAME = "DFK-ARB"
PROJECT_LOGGER_NAME = "DFK-DEX"

# Default logging level for the application
DEFAULT_LOG_LEVEL = logging.INFO

# Environment variable for log level override
LOG_LEVEL_ENV = "LOG_LEVEL"

# Mapping of string log levels to logging constants
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Default log level string used when environment variable is not set
DEFAULT_LOG_LEVEL_STRING = "INFO"


def _getLogLevel() -> int:
    """
    Get the logging level from environment variable or default.

    Returns:
        int: Logging level constant (e.g., logging.INFO)
    """
    level_str = os.environ.get(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL_STRING).upper()
    return LOG_LEVEL_MAP.get(level_str, DEFAULT_LOG_LEVEL)


def setupLogging() -> logging.Logger:
    """
    Initialize and configure the main application logger.

    Sets up logging with INFO level, stdout output, and a standardized
    format including timestamp, level, and message. Date format can be
    customized through the DATE_FORMAT environment variable.

    Returns:
        logging.Logger: Configured logger instance for the application.

    Example:
        >>> logger = setupLogging()
        >>> logger.info("Scrape started")
        2025-08-17 14:30:00 | INFO | Scrape started

    Note:
        This function should be called once at application startup.
        Multiple calls will not create duplicate handlers due to
        basicConfig's idempotent behavior.
    """
    logger = logging.getLogger(MAIN_LOGGER_NAME)

    # Allow custom date format via environment variable
    dateFormat: Optional[str] = os.environ.get(DATE_FORMAT_ENV)

    # Get log level from environment or use default
    log_level = _getLogLevel()

    logging.basicConfig(
        level=log_level,
        format=DEFAULT_LOG_FORMAT,
        stream=sys.stdout,
        datefmt=dateFormat
    )

    return logger


def getProjectLogger() -> logging.Logger:
    """
    Get the project-specific logger instance.

    Returns a logger for module-level logging throughout the application.
    This logger inherits the root logger's configuration but can be
    configured independently if needed.

    Returns:
        logging.Logger: Logger instance for project-wide logging.

    Example:
        >>> logger = getProjectLogger()
        >>> logger.debug("Processing token data")
        >>> logger.error("Failed to connect to database")

    Note:
        Use this function to get a logger in any module that needs
        to produce log output. The logger name is consistent across
        the application for filtering and configuration purposes.
    """
    return logging.getLogger(PROJECT_LOGGER_NAME)
