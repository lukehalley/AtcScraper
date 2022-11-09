import os

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
    retryLimit = int(os.getenv("PAGE_LOAD_RETRY_LIMIT"))
    retryCounter = 0
    pageLoaded = False
    while not pageLoaded:
        if retryCounter < retryLimit:
            try:
                page.goto(url)
                pageLoaded = True
                return pageLoaded
            except:
                retryLimit = retryLimit + 1
                logger.warn(f"Trying to load {url} again...")
                pageLoaded = False
                page.reload()
        else:
            logger.warn(f"Reached retry limit loading {url}!")
            pageLoaded = False
            return pageLoaded
