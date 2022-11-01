from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def safeClick(page, selector):
    elementClicked = False
    while not elementClicked:
        try:
            page.locator(selector).first.click()
            elementClicked = True
        except:
            logger.warn(f"Trying to click {selector} again...")
            elementClicked = False
            page.reload()

def safePageLoad(page, url):
    pageLoaded = False
    while not pageLoaded:
        try:
            page.goto(url)
            pageLoaded = True
        except:
            # logger.warn(f"Trying to load {url} again...")
            pageLoaded = False
            page.reload()
