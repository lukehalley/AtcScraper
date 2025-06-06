"""AWS Secrets Manager credential retrieval utilities.

This module provides functions to access AWS Secrets Manager credentials
that have been pre-loaded into environment variables. This allows the
application to securely access database credentials without hardcoding them.
"""
import json
import os
from typing import Any, Optional, Dict
# TODO: Implement automatic credential rotation for AWS secrets

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Environment variable containing AWS secrets JSON
AWS_CREDENTIALS_ENV = "ATC_DB_Credentials"

# Cache for parsed credentials to avoid repeated JSON parsing
_credentials_cache: Optional[Dict[str, Any]] = None


def _getCredentials() -> Optional[Dict[str, Any]]:
    """
    Get and cache the parsed credentials from environment variable.

    Returns:
        Optional[Dict[str, Any]]: Parsed credentials dict or None if not set.
    """
    global _credentials_cache

    if _credentials_cache is not None:
        return _credentials_cache

    credentials_json = os.environ.get(AWS_CREDENTIALS_ENV)
    if credentials_json is None:
        logger.warning(f"Environment variable {AWS_CREDENTIALS_ENV} is not set")
        return None

    try:
        _credentials_cache = json.loads(credentials_json)
        return _credentials_cache
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AWS credentials JSON: {e}")
        raise


def getAWSSecret(key: str) -> Optional[Any]:
    """
    Retrieve a specific value from AWS Secrets stored in environment variables.

    The ATC_DB_Credentials environment variable should contain a JSON string
    with database credentials (username, password, etc.) that was retrieved
    from AWS Secrets Manager.

    Args:
        key: The key to look up in the credentials JSON (e.g., 'username', 'password').

    Returns:
        The value associated with the key, or None if credentials are not set.

    Raises:
        json.JSONDecodeError: If the credentials string is not valid JSON.
        KeyError: If the specified key does not exist in the credentials.
    """
    credentials = _getCredentials()
    if credentials is None:
        return None
    return credentials[key]