import os


from playwright.async_api import expect

from src.playwright.playwright_Utils import findAndCheckElement


def getDexscreenerRoot():
    return os.getenv('DS_ROOT_URL')

async def validateDexscreenerInit(page):

    # Navigate To The Dexscreener Home
    dexScreenerHome = getDexscreenerRoot()
    await page.goto(dexScreenerHome)

    dsSidebar = os.getenv('DS_SIDEBAR')
    sidebar = await findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    dsPanel = os.getenv('DS_PANEL')
    panel = await findAndCheckElement(
        page=page,
        selector=dsPanel
    )

