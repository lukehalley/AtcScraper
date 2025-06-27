"""
Environment detection utilities for runtime context awareness.

This module provides functions to detect the runtime environment
including Docker containers, AWS infrastructure, and display settings.
Environment detection is critical for adapting application behavior
to different deployment contexts.

Environment Variables Used:
    - RUNNING_IN_DOCKER: Set to 'true' when running inside a Docker container
    - AWS_DEFAULT_REGION: Automatically set by AWS compute services (Lambda, EC2, ECS)
    - FORCE_HEADLESS: Override to force headless browser mode regardless of environment

These functions are used by the Playwright browser initialization
to determine appropriate display and rendering settings, ensuring
the scraper works correctly in both local development and cloud deployments.

Typical usage:
    from src.utils.env.env_Environment import checkHeadless, checkIsAWS

    if checkIsAWS():
        # Use AWS-specific configuration
        pass

    headless = checkHeadless()
    browser = playwright.chromium.launch(headless=headless)
"""
import os

from src.utils.data.data_Booleans import strToBool
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()
# Validate required environment variables on module initialization

# Environment variable names
DOCKER_ENV_VAR = "RUNNING_IN_DOCKER"
AWS_REGION_ENV_VAR = "AWS_DEFAULT_REGION"
FORCE_HEADLESS_ENV_VAR = "FORCE_HEADLESS"


def checkIsDocker() -> bool:
    """
    Check if the application is running inside a Docker container.

    Returns:
        bool: True if RUNNING_IN_DOCKER environment variable is set to a truthy value,
              False otherwise.

    Examples:
        >>> os.environ['RUNNING_IN_DOCKER'] = 'true'
        >>> checkIsDocker()
        True

        >>> os.environ.pop('RUNNING_IN_DOCKER', None)
        >>> checkIsDocker()
        False
    """
    docker_env = os.environ.get(DOCKER_ENV_VAR)
    if docker_env is None:
        logger.debug("Docker environment variable not set, assuming non-Docker")
        return False
    is_docker = strToBool(docker_env)
    logger.debug(f"Docker environment detected: {is_docker}")
    return is_docker


def checkIsAWS() -> bool:
    """
    Check if the application is running on AWS infrastructure.

    Determines AWS environment by checking for the presence of the
    AWS_DEFAULT_REGION environment variable, which is automatically
    set in AWS Lambda, EC2, ECS, and other AWS compute services.

    Returns:
        bool: True if AWS_DEFAULT_REGION is set, False otherwise.

    Note:
        This check works because AWS_DEFAULT_REGION is automatically
        injected by AWS services. In local development, this variable
        is typically not set unless explicitly configured.
    """
    aws_region = os.environ.get(AWS_REGION_ENV_VAR)
    is_aws = bool(aws_region)
    if is_aws:
        logger.debug(f"AWS environment detected, region: {aws_region}")
    else:
        logger.debug("Not running in AWS environment")
    return is_aws


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