import os

from playwright.async_api import expect, BrowserContext

from src.utils.logging.logging_Setup import getProjectLogger

globalTimeout = int(os.getenv("PLAYWRIGHT_TIMEOUT_SECS")) * 1000

x = 1

logger = getProjectLogger()

# Find + Wait for element
async def findAndCheckElement(page, selector):
    element = page.locator(selector).first
    await expect(element).to_be_visible(timeout=globalTimeout)
    return element

# Wait for element to be removed from DOM
async def waitForElementToGoAway(page, selector):

    elementGoneAway = False
    while not elementGoneAway:
        try:
            element = page.locator(selector)
            await expect(element).not_to_be_visible(timeout=globalTimeout)
            elementGoneAway = True
        except:
            logger.warn(f"Waiting for {selector} to go away again...")
            elementGoneAway = False
            await page.reload()

# Get all 'li' items inside a parent element
async def getListItems(page, listElement):
    listLocated = False
    while not listLocated:
        try:
            allLists = listElement.locator(selector='li')
            return await allLists.all_text_contents()
        except:
            logger.warn(f"Trying get li {listElement} again...")
            listLocated = False
            await page.reload()

# Get all 'a' items inside a parent element
async def getAItems(page, listElement):
    itemsLocated = False
    while not itemsLocated:
        try:
            allLists = listElement.locator(selector='a')
            return await allLists.all_inner_texts()
        except:
            logger.warn(f"Trying get ai {listElement} again...")
            itemsLocated = False
            await page.reload()

# Create a new browser page
async def newPage(browser: BrowserContext):
    page = await browser.new_page()
    page.set_default_timeout(timeout=globalTimeout)
    return page