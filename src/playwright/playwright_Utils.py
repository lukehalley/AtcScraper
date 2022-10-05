import os

from playwright.async_api import expect, BrowserContext

globalTimeout = int(os.getenv("PLAYWRIGHT_TIMEOUT_SECS")) * 1000

x = 1

# Find + Wait for element
async def findAndCheckElement(page, selector):
    element = page.locator(selector).first
    await expect(element).to_be_visible(timeout=globalTimeout)
    return element

# Wait for element to be removed from DOM
async def waitForElementToGoAway(page, selector):
    element = page.locator(selector)
    await expect(element).not_to_be_visible(timeout=globalTimeout)

# Get all 'li' items inside a parent element
async def getListItems(listElement):
    allLists = listElement.locator(selector='li')
    return await allLists.all_text_contents()

# Get all 'a' items inside a parent element
async def getAItems(listElement):
    allLists = listElement.locator(selector='a')
    return await allLists.all_inner_texts()

# Create a new browser page
async def newPage(browser: BrowserContext):
    page = await browser.new_page()
    page.set_default_timeout(timeout=globalTimeout)
    return page