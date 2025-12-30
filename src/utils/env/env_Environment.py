"""
Environment detection utilities.

This module provides functions to detect the runtime environment
including Docker containers, AWS infrastructure, and display settings.
"""
import os

from src.utils.data.data_Booleans import strToBool

# Environment variable names
DOCKER_ENV_VAR = "RUNNING_IN_DOCKER"
AWS_REGION_ENV_VAR = "AWS_DEFAULT_REGION"
FORCE_HEADLESS_ENV_VAR = "FORCE_HEADLESS"


def checkIsDocker() -> bool:
    """
    Check if the application is running inside a Docker container.

    Returns:
        bool: True if RUNNING_IN_DOCKER environment variable is set to a truthy value.

    Examples:
        >>> os.environ['RUNNING_IN_DOCKER'] = 'true'
        >>> checkIsDocker()
        True
    """
    docker_env = os.environ.get(DOCKER_ENV_VAR)
    if docker_env is None:
        return False
    return strToBool(docker_env)


def checkIsAWS() -> bool:
    """
    Check if the application is running on AWS infrastructure.

    Determines AWS environment by checking for the presence of the
    AWS_DEFAULT_REGION environment variable, which is automatically
    set in AWS Lambda and other AWS compute services.

    Returns:
        bool: True if AWS_DEFAULT_REGION is set, False otherwise.
    """
    return bool(os.environ.get(AWS_REGION_ENV_VAR))


def checkHeadless() -> bool:
    """
    Determine if the browser should run in headless mode.

    The browser runs headless when either:
    - Running inside a Docker container (no display available)
    - FORCE_HEADLESS environment variable is set to true

    Returns:
        bool: True if browser should run in headless mode.
    """
    # Check Docker environment first
    if checkIsDocker():
        return True

    # Check force headless flag
    force_headless = os.getenv(FORCE_HEADLESS_ENV_VAR)
    if force_headless is None:
        return False
    return strToBool(force_headless)