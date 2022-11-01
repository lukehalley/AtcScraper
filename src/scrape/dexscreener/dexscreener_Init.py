import os

# retryAttempts, retryDelay = getRetryParameters()

# Get the root url of Dexscreener
from src.playwright.playwright_Utils import findAndCheckElement


def getDexscreenerRoot():
    return os.getenv('DS_ROOT_URL')

# @retry(attempts=retryAttempts, delay=retryDelay)
def validateDexscreenerInit(page):
    
    # Validate the Dexscreener sidebar is present
    dsSidebar = os.getenv('DS_SIDEBAR')
    findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    # Validate the Dexscreener panel is present
    dsPanel = os.getenv('DS_PANEL')
    findAndCheckElement(
        page=page,
        selector=dsPanel
    )

