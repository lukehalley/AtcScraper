"""
Playwright utility functions for web scraping operations.

This module provides helper functions for common Playwright operations
including element finding, waiting, and page creation.
"""
import os
from typing import List

from playwright.async_api import expect, BrowserContext, Page, Locator

# Timeout configuration
PLAYWRIGHT_TIMEOUT_ENV = "PLAYWRIGHT_TIMEOUT_SECS"
DEFAULT_TIMEOUT_SECS = 30  # Default timeout if environment variable not set
MILLISECONDS_PER_SECOND = 1000

# Calculate timeout in milliseconds, with fallback to default
_timeout_secs = int(os.getenv(PLAYWRIGHT_TIMEOUT_ENV, DEFAULT_TIMEOUT_SECS))
PLAYWRIGHT_TIMEOUT_MS = _timeout_secs * MILLISECONDS_PER_SECOND


async def findAndCheckElement(page: Page, selector: str) -> Locator:
    """
    Find an element and wait for it to be visible.

    Args:
        page: The Playwright page object.
        selector: CSS selector for the element.

    Returns:
        The first matching Locator element.
    """
    element = page.locator(selector).first
    await expect(element).to_be_visible(timeout=PLAYWRIGHT_TIMEOUT_MS)
    return element


async def waitForElementToGoAway(page: Page, selector: str) -> None:
    """
    Wait for an element to be removed from the DOM.

    Args:
        page: The Playwright page object.
        selector: CSS selector for the element to wait for removal.
    """
    element = page.locator(selector)
    await expect(element).not_to_be_visible(timeout=PLAYWRIGHT_TIMEOUT_MS)


async def getListItems(listElement: Locator) -> List[str]:
    """
    Get all list item text contents from a parent element.

    Args:
        listElement: Parent Locator containing li elements.

    Returns:
        List of text contents from all li elements.
    """
    allLists = listElement.locator(selector='li')
    return await allLists.all_text_contents()


async def getAItems(listElement: Locator) -> List[str]:
    """
    Get all anchor element inner texts from a parent element.

    Args:
        listElement: Parent Locator containing anchor elements.

    Returns:
        List of inner texts from all anchor elements.
    """
    allLists = listElement.locator(selector='a')
    return await allLists.all_inner_texts()


async def newPage(browser: BrowserContext) -> Page:
    """
    Create a new browser page with configured timeout.

    Args:
        browser: The browser context to create the page in.

    Returns:
        A new Page object with default timeout configured.
    """
    page = await browser.new_page()
    page.set_default_timeout(timeout=PLAYWRIGHT_TIMEOUT_MS)
    return page