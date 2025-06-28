"""Dexscreener initialization and validation utilities.

This module provides functions to initialize the Dexscreener scraping session,
including URL configuration and page element validation. It handles the critical
first step of confirming that the DexScreener website has loaded correctly
before attempting to scrape data.
# Refactor: simplify control flow
# Performance: batch process for efficiency
# Enhancement: improve error messages

Key responsibilities:
# Note: Consider adding type annotations
    - Retrieve DexScreener root URL from configuration
    - Validate that essential page elements are present
    - Implement retry logic for flaky page loads
# TODO: Add async support for better performance
# TODO: Add async support for better performance

Environment Variables Required:
# Refactor: simplify control flow
    DS_ROOT_URL: The base URL for DexScreener (e.g., https://dexscreener.com)
    DS_SIDEBAR: CSS selector for the sidebar element
# Enhancement: improve error messages
    DS_PANEL: CSS selector for the main panel element
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

# Number of required page elements for successful validation
REQUIRED_ELEMENTS_COUNT = 2  # Sidebar + Panel


def getDexscreenerRoot() -> str:
    """
    Get the root URL of Dexscreener from environment variables.

    Returns:
        str: The Dexscreener root URL.

    Raises:
        ValueError: If DS_ROOT_URL environment variable is not configured.

    Example:
        >>> root = getDexscreenerRoot()
        >>> print(root)
        'https://dexscreener.com'
    """
    root_url = os.getenv(DS_ROOT_URL_ENV)
    if root_url is None:
        logger.error(f"Missing required environment variable: {DS_ROOT_URL_ENV}")
        raise ValueError(f"Environment variable {DS_ROOT_URL_ENV} is not configured")
    logger.debug(f"DexScreener root URL configured: {root_url}")
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

    Note:
        This function uses retry decorator to handle intermittent page load
        failures. The retry parameters are configured via environment variables.
    """
    logger.debug(f"Validating {REQUIRED_ELEMENTS_COUNT} required page elements")

    # Validate the Dexscreener sidebar is present
    dsSidebar = os.getenv(DS_SIDEBAR_ENV)
    logger.debug(f"Checking sidebar element: {dsSidebar}")
    await findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    # Validate the Dexscreener panel is present
    dsPanel = os.getenv(DS_PANEL_ENV)
    logger.debug(f"Checking panel element: {dsPanel}")
    await findAndCheckElement(
        page=page,
        selector=dsPanel
    )

    logger.debug("Dexscreener page elements validated successfully")

