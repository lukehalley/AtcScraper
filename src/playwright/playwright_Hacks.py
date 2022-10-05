from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

async def safeClick(page, selector):
    elementClicked = False
    while not elementClicked:
        try:
            await page.locator(selector).first.click()
            elementClicked = True
        except:
            logger.warn(f"Trying to click {selector} again...")
            elementClicked = False
            await page.reload()

async def safePageLoad(page, url):
    pageLoaded = False
    while not pageLoaded:
        try:
            await page.goto(url)
            pageLoaded = True
        except:
            logger.warn(f"Trying to load {url} again...")
            pageLoaded = False
            await page.reload()
