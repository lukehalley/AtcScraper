from playwright.async_api import expect


async def findAndCheckElement(page, selector):
    element = page.locator(selector)
    await expect(element).to_be_visible()
    return element