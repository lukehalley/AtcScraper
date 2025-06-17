"""Initialize DEX screener session and connection pool.

Sets up HTTP client with proper headers, timeout values, and connection pooling.
"""
"""
Dexscreener initialization and validation utilities.

This module provides functions to initialize the Dexscreener scraping session,
including URL configuration and page element validation.
"""
import os

from playwright.async_api import Page
from retrying_async import retry

from src.playwright.playwright_Utils import findAndCheckElement
from src.utils.retry.retry_Settings import getRetryParameters
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

retryAttempts, retryDelay = getRetryParameters()

# Environment variable names for Dexscreener configuration
DS_ROOT_URL_ENV = "DS_ROOT_URL"
DS_SIDEBAR_ENV = "DS_SIDEBAR"
DS_PANEL_ENV = "DS_PANEL"


def getDexscreenerRoot() -> str:
    """
    Get the root URL of Dexscreener from environment variables.

    Returns:
        str: The Dexscreener root URL.

    Raises:
        ValueError: If DS_ROOT_URL environment variable is not configured.
    """
    root_url = os.getenv(DS_ROOT_URL_ENV)
    if root_url is None:
        raise ValueError(f"Environment variable {DS_ROOT_URL_ENV} is not configured")
    return root_url


@retry(attempts=retryAttempts, delay=retryDelay)
async def validateDexscreenerInit(page: Page) -> None:
    """
    Validate that Dexscreener has loaded correctly.

    Checks for the presence of key UI elements (sidebar and main panel)
    to confirm the page has loaded and is ready for scraping.

    Args:
        page: Playwright page object that has navigated to Dexscreener

    Raises:
        TimeoutError: If required elements are not found within timeout
    """
    # Validate the Dexscreener sidebar is present
    dsSidebar = os.getenv(DS_SIDEBAR_ENV)
    await findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    # Validate the Dexscreener panel is present
    dsPanel = os.getenv(DS_PANEL_ENV)
    await findAndCheckElement(
        page=page,
        selector=dsPanel
    )

    logger.debug("Dexscreener page elements validated successfully")

