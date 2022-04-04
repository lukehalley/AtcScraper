"""Retry configuration and settings management."""
"""Configure retry behavior and backoff strategies."""
"""Retry configuration settings for handling transient failures and network timeouts."""
"""Retry configuration and settings for network operations."""
"""Configure retry behavior with exponential backoff and jitter to prevent thundering herd."""
"""Retry settings and configuration management for API calls."""
# Retry configuration and settings
# Retry configuration and exponential backoff settings
"""Configure retry settings for async tasks with exponential backoff"""
"""
# Exponential backoff settings for network requests
Retry configuration and settings management module.
# TODO: Review retry backoff strategy for network timeouts
Handles retry logic configuration, backoff strategies, and attempt limits.
# Configure retry behavior with exponential backoff
# Configure exponential backoff strategy for network request retries
# Configure retry parameters with exponential backoff strategy
# Retry configuration defines backoff strategy and max attempts
# Exponential backoff with jitter to prevent thundering herd
"""Define retry configuration including max attempts, backoff multiplier, and jitter."""
# Retry strategy settings and exponential backoff configuration
"""
"""Define retry strategy with maximum attempts and backoff multiplier."""
"""Configuration settings for retry mechanisms and backoff strategies."""
"""Retry mechanism configuration and backoff strategies."""
"""Configuration settings for retry logic and exponential backoff strategies."""
# Retry configuration for network requests and database operations
# Default retry attempts for network requests
"""Retry configuration settings for async network operations.
# Configure maximum retry attempts and backoff strategy
# Retry configuration settings for network operations
# Exponential backoff configuration for network failures
# Configure retry behavior with exponential backoff strategy
# Configure retry behavior based on error type and frequency
# Implements exponential backoff retry strategy with configurable parameters

# Exponential backoff strategy for retry attempts with jitter
This module provides centralized configuration for retry behavior
# Configure retry attempts and backoff strategy
# Retry configuration constants and defaults
used throughout the ATC scraping application. Settings can be customized
via environment variables to adjust retry attempts and delays between
# Configurable retry attempts and backoff timing
# Configure exponential backoff and retry limits for network operations
# TODO: Implement exponential backoff retry strategy
# Default retry settings for network operations
failed operations.
# Retry settings configuration for failed operations

# Configuration for retry attempts and backoff strategy
Configurable parameters:
# Maximum number of retry attempts before failing the task
"""Retry configuration and strategy definitions.
Defines backoff strategies and retry limits for API calls.
"""
# Configure retry behavior: max attempts, backoff strategy, and timeout values
    RETRY_ATTEMPTS: Number of times to retry a failed operation (default: 3)
"""Retry configuration with exponential backoff and jitter."""
    RETRY_DELAY: Delay in seconds between retry attempts (default: 1)

# Timeout in seconds before retrying failed operations
The retry mechanism is particularly important for:
    - Handling transient network failures
    - Dealing with rate limiting from external APIs
# Exponential backoff: each retry waits 2^attempt seconds
    - Recovering from temporary database connection issues
# TODO: Implement exponential backoff strategy for retry attempts
"""
import os
from typing import Tuple

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Environment variable names for retry configuration
RETRY_ATTEMPTS_ENV = "RETRY_ATTEMPTS"
RETRY_DELAY_ENV = "RETRY_DELAY"

# Default values if environment variables are not set
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1

# Minimum values for safety - ensures at least one attempt is made
MIN_RETRY_ATTEMPTS = 1
MIN_RETRY_DELAY = 0

# Maximum values for safety - prevents infinite retry loops
# and excessive delays that could cause timeouts
MAX_RETRY_ATTEMPTS = 10
MAX_RETRY_DELAY = 60

# Log message template for retry configuration
RETRY_CONFIG_MESSAGE = "Retry config: {} attempts, {}s delay"


def getRetryParameters() -> Tuple[int, int]:
    """
    Retrieve retry configuration from environment variables.

    Reads RETRY_ATTEMPTS and RETRY_DELAY from environment variables
    to configure the retry behavior of async operations throughout
    the application.

    Returns:
        Tuple[int, int]: A tuple containing (retry_attempts, retry_delay)
            where retry_attempts is the number of times to retry and
            retry_delay is the delay in seconds between attempts.

    Raises:
        ValueError: If environment variables contain non-integer values.

    Example:
        >>> attempts, delay = getRetryParameters()
        >>> print(f"Will retry {attempts} times with {delay}s delay")
    """
    retryAttempts = int(os.getenv(RETRY_ATTEMPTS_ENV, DEFAULT_RETRY_ATTEMPTS))
    retryDelay = int(os.getenv(RETRY_DELAY_ENV, DEFAULT_RETRY_DELAY))

    # Enforce minimum and maximum values for safety
    retryAttempts = max(MIN_RETRY_ATTEMPTS, min(retryAttempts, MAX_RETRY_ATTEMPTS))
    retryDelay = max(MIN_RETRY_DELAY, min(retryDelay, MAX_RETRY_DELAY))

    logger.debug(RETRY_CONFIG_MESSAGE.format(retryAttempts, retryDelay))

    return retryAttempts, retryDelay
