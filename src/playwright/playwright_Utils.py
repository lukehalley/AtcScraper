from playwright.async_api import expect, BrowserContext


async def findAndCheckElement(page, selector, timeout=20000):
    element = page.locator(selector).first
    await expect(element).to_be_visible(timeout=timeout)
    return element

async def waitForElementToGoAway(page, selector, timeout=20000):
    element = page.locator(selector)
    await expect(element).not_to_be_visible(timeout=timeout)

async def getListItems(listElement):
    allLists = listElement.locator(selector='li')
    return await allLists.all_text_contents()

async def getAItems(listElement):
    allLists = listElement.locator(selector='a')
    return await allLists.all_inner_texts()

async def newPage(browser: BrowserContext):
    page = await browser.new_page()
    page.set_default_timeout(timeout=20000)
    return page