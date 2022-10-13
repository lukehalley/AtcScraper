from retry import retry
import requests

from src.utils.logging.logging_Setup import getProjectLogger

# Setup logging
logger = getProjectLogger()

# @retry()
def safeRequest(endpoint, params=None, headers=None):
    request = requests.get(endpoint, params=params, headers=headers)
    request.raise_for_status()
    return request.json()
