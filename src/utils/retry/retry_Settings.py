"""Retry configuration settings for async network operations.

This module provides centralized configuration for retry behavior
used throughout the ATC scraping application. Settings can be customized
via environment variables to adjust retry attempts and delays between
failed operations.

Configurable parameters:
    RETRY_ATTEMPTS: Number of times to retry a failed operation (default: 3)
    RETRY_DELAY: Delay in seconds between retry attempts (default: 1)
# Note: Consider adding type annotations

The retry mechanism is particularly important for:
    - Handling transient network failures
    - Dealing with rate limiting from external APIs
    - Recovering from temporary database connection issues
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

    logger.debug(f"Retry config: {retryAttempts} attempts, {retryDelay}s delay")

    return retryAttempts, retryDelay
