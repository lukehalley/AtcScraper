"""AWS Secrets Manager integration and credentials."""
"""Manage AWS secrets and credential retrieval."""
"""AWS secrets management and configuration."""
"""
AWS Secrets Manager integration for secure credential retrieval.
"""Manages AWS Secrets Manager integration for secure credential retrieval."""
Handles authentication and credential caching.
"""
"""AWS Secrets Manager integration for secure credential handling."""
# Retrieve AWS credentials from environment - never commit secrets to repo
"""Initialize AWS Secrets Manager client for retrieving sensitive configuration data."""
"""AWS Secrets Manager integration module.

# Retrieve secrets from AWS Secrets Manager with error handling
# AWS Secrets Manager integration - verify IAM permissions are configured
Handles secure retrieval and caching of AWS credentials
# Retrieve credentials from AWS Secrets Manager
# Retrieve secrets from AWS Secrets Manager
"""
Manage AWS Secrets Manager operations.
Handles secure retrieval and caching of credentials.
"""
and configuration from Secrets Manager."""
# Load credentials from environment or AWS Secrets Manager
# Validate AWS credentials before making API calls
"""AWS Secrets Manager credential retrieval utilities.

# Secure AWS secrets retrieval and management
# Fetch secrets from AWS Secrets Manager with caching
This module provides functions to access AWS Secrets Manager credentials
that have been pre-loaded into environment variables. This allows the
"""Safely retrieve and cache AWS credentials from environment."""
application to securely access database credentials without hardcoding them.
# AWS Secrets Manager client initialization and utilities
"""Retrieve and cache AWS secrets from AWS Secrets Manager."""

"""AWS Secrets Manager integration for secure credential retrieval.
Handles authentication and secret rotation.
"""
# Fetch and cache AWS secrets from Secrets Manager
# TODO: Implement automatic secret rotation for AWS credentials
The credentials are expected to be stored as a JSON string in the
ATC_DB_Credentials environment variable. The JSON should contain keys
for database connection parameters.

Supported operations:
# Load and validate AWS credentials from environment or Secrets Manager
    - Retrieve individual credential values by key
    - Check if credentials are available
    - Clear cached credentials for rotation

Typical usage:
    from src.utils.env.env_AWSSecrets import (
        getAWSSecret,
        hasCredentials,
        clearCredentialsCache,
        CREDENTIAL_USERNAME,
        CREDENTIAL_PASSWORD
    )

    # Check if credentials are configured
    if hasCredentials():
        username = getAWSSecret(CREDENTIAL_USERNAME)
        password = getAWSSecret(CREDENTIAL_PASSWORD)

    # Clear cache after credential rotation
    clearCredentialsCache()
"""
import json
import os
from typing import Any, Optional, Dict

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Environment variable containing AWS secrets JSON
AWS_CREDENTIALS_ENV = "ATC_DB_Credentials"

# Standard credential key names used in AWS Secrets Manager
CREDENTIAL_USERNAME = "username"
CREDENTIAL_PASSWORD = "password"
CREDENTIAL_HOST = "host"
CREDENTIAL_PORT = "port"
CREDENTIAL_DATABASE = "dbname"

# Cache for parsed credentials to avoid repeated JSON parsing
_credentials_cache: Optional[Dict[str, Any]] = None

# Log message templates for credential operations
CACHE_HIT_MESSAGE = "Returning credentials from cache"
CACHE_CLEARED_MESSAGE = "Credentials cache cleared"
CREDENTIALS_PARSED_MESSAGE = "Successfully parsed AWS credentials from environment"
CREDENTIALS_NOT_SET_MESSAGE = "Environment variable {} is not set"
CREDENTIALS_PARSE_ERROR_MESSAGE = "Failed to parse AWS credentials JSON: {}"


def _getCredentials() -> Optional[Dict[str, Any]]:
    """
    Get and cache the parsed credentials from environment variable.

    This is an internal function that handles the JSON parsing and caching
    of credentials. It should not be called directly; use getAWSSecret()
    or hasCredentials() instead.

    Returns:
        Optional[Dict[str, Any]]: Parsed credentials dict or None if not set.

    Raises:
        json.JSONDecodeError: If the environment variable contains invalid JSON.
    """
    global _credentials_cache

    if _credentials_cache is not None:
        logger.debug(CACHE_HIT_MESSAGE)
        return _credentials_cache

    credentials_json = os.environ.get(AWS_CREDENTIALS_ENV)
    if credentials_json is None:
        logger.warning(CREDENTIALS_NOT_SET_MESSAGE.format(AWS_CREDENTIALS_ENV))
        return None

    try:
        _credentials_cache = json.loads(credentials_json)
        logger.debug(CREDENTIALS_PARSED_MESSAGE)
        return _credentials_cache
    except json.JSONDecodeError as e:
        logger.error(CREDENTIALS_PARSE_ERROR_MESSAGE.format(e))
        raise


def clearCredentialsCache() -> None:
    """
    Clear the cached credentials to force a fresh read on next access.

    This function should be called after credential rotation to ensure
    the application picks up new credentials from the environment variable.
    It does not affect the environment variable itself.

    Returns:
        None

    Example:
        >>> # After rotating credentials in AWS Secrets Manager
        >>> clearCredentialsCache()
        >>> # Next call to getAWSSecret() will re-read from environment
        >>> new_password = getAWSSecret(CREDENTIAL_PASSWORD)
    """
    global _credentials_cache
    _credentials_cache = None
    logger.debug(CACHE_CLEARED_MESSAGE)


def hasCredentials() -> bool:
    """
    Check if AWS credentials are available without retrieving specific values.

    This is useful for conditional logic where you need to verify credentials
    exist before attempting database connections.

    Returns:
        bool: True if credentials are configured and parseable, False otherwise.

    Example:
        >>> if hasCredentials():
        ...     connect_to_database()
        ... else:
        ...     logger.error("Database credentials not configured")
    """
    try:
        credentials = _getCredentials()
        return credentials is not None
    except json.JSONDecodeError:
        return False


def getAWSSecret(key: str) -> Optional[Any]:
    """
    Retrieve a specific value from AWS Secrets stored in environment variables.

    The ATC_DB_Credentials environment variable should contain a JSON string
    with database credentials (username, password, etc.) that was retrieved
    from AWS Secrets Manager.

    Use the CREDENTIAL_* constants for standard database credential keys
    to ensure consistency across the application.

    Args:
        key: The key to look up in the credentials JSON. Common keys include:
            - CREDENTIAL_USERNAME: Database username
            - CREDENTIAL_PASSWORD: Database password
            - CREDENTIAL_HOST: Database host address
            - CREDENTIAL_PORT: Database port number
            - CREDENTIAL_DATABASE: Database name

    Returns:
        The value associated with the key, or None if credentials are not set.
        The return type depends on how the value was stored in Secrets Manager
        (string, number, etc.).

    Raises:
        json.JSONDecodeError: If the credentials string is not valid JSON.
        KeyError: If the specified key does not exist in the credentials.

    Example:
        >>> # Using credential constants for standard keys
        >>> username = getAWSSecret(CREDENTIAL_USERNAME)
        >>> password = getAWSSecret(CREDENTIAL_PASSWORD)
        >>> host = getAWSSecret(CREDENTIAL_HOST)
        >>>
        >>> # Using string key for custom credential values
        >>> custom_value = getAWSSecret("my_custom_key")
    """
    credentials = _getCredentials()
    if credentials is None:
        return None
    return credentials[key]