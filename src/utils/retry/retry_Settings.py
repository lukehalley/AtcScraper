import os
from typing import Tuple

# Environment variable names for retry configuration
RETRY_ATTEMPTS_ENV = "RETRY_ATTEMPTS"
RETRY_DELAY_ENV = "RETRY_DELAY"

# Default values if environment variables are not set
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1


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
    """
    retryAttempts = int(os.getenv(RETRY_ATTEMPTS_ENV, DEFAULT_RETRY_ATTEMPTS))
    retryDelay = int(os.getenv(RETRY_DELAY_ENV, DEFAULT_RETRY_DELAY))

    return retryAttempts, retryDelay
