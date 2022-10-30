import os
from pathlib import Path

from faker import Faker
from playwright.async_api import expect, BrowserContext
from playwright.sync_api import sync_playwright

from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger

globalTimeout = int(os.getenv("PLAYWRIGHT_TIMEOUT_SECS")) * 1000

logger = getProjectLogger()

# Find + Wait for element
def findAndCheckElement(page, selector):
    element = page.locator(selector).first
    element.is_visible(timeout=globalTimeout)
    return element

# Wait for element to be removed from DOM
def waitForElementToGoAway(page, selector):

    elementGoneAway = False
    while not elementGoneAway:
        try:
            element = page.locator(selector)
            element.not_to_be_visible(timeout=globalTimeout)
            elementGoneAway = True
        except:
            logger.warn(f"Waiting for {selector} to go away again...")
            elementGoneAway = False
            page.reload()

# Get all 'li' items inside a parent element
def getListItems(page, listElement):
    listLocated = False
    while not listLocated:
        try:
            allLists = listElement.locator(selector='li')
            return allLists.all_text_contents()
        except:
            logger.warn(f"Trying get li {listElement} again...")
            listLocated = False
            page.reload()

# Get all 'a' items inside a parent element
def getAItems(page, listElement):
    itemsLocated = False
    while not itemsLocated:
        try:
            allLists = listElement.locator(selector='a')
            return allLists.all_inner_texts()
        except:
            logger.warn(f"Trying get ai {listElement} again...")
            itemsLocated = False
            page.reload()

# Create a new browser page
def newPage(browser: BrowserContext):
    page = browser.new_page()
    return page