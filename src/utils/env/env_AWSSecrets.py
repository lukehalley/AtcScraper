import json
import os
from typing import Any, Optional

# Environment variable containing AWS secrets JSON
AWS_CREDENTIALS_ENV = "ATC_DB_Credentials"


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
    credentials_json = os.environ.get(AWS_CREDENTIALS_ENV)
    if credentials_json is None:
        return None
    return json.loads(credentials_json)[key]