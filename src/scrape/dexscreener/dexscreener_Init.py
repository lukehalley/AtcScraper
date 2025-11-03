"""
Dexscreener initialization and validation utilities.

This module provides functions to initialize the Dexscreener scraping session,
including URL configuration and page element validation.
"""
import os
from typing import Optional

from playwright.async_api import Page
from retrying_async import retry

from src.playwright.playwright_Utils import findAndCheckElement
from src.utils.retry.retry_Settings import getRetryParameters

retryAttempts, retryDelay = getRetryParameters()

# Environment variable name for Dexscreener root URL
DS_ROOT_URL_ENV = "DS_ROOT_URL"


def getDexscreenerRoot() -> Optional[str]:
    """
    Get the root URL of Dexscreener from environment variables.

    Returns:
        Optional[str]: The Dexscreener root URL, or None if not configured.
    """
    return os.getenv(DS_ROOT_URL_ENV)

@retry(attempts=retryAttempts, delay=retryDelay)
async def validateDexscreenerInit(page):
    # Validate the Dexscreener sidebar is present
    dsSidebar = os.getenv('DS_SIDEBAR')
    await findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    # Validate the Dexscreener panel is present
    dsPanel = os.getenv('DS_PANEL')
    await findAndCheckElement(
        page=page,
        selector=dsPanel
    )

