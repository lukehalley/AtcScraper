import os

from retrying_async import retry

from src.playwright.playwright_Utils import findAndCheckElement
from src.utils.retry.retry_Settings import getRetryParameters

# retryAttempts, retryDelay = getRetryParameters()

# Get the root url of Dexscreener
def getDexscreenerRoot():
    return os.getenv('DS_ROOT_URL')

# @retry(attempts=retryAttempts, delay=retryDelay)
async def validateDexscreenerInit(page):
    # Validate the Dexscreener sidebar is present
    dsSidebar = os.getenv('DS_SIDEBAR')
    await findAndCheckElement(
        page=page,
        selector=dsSidebar
    )

    # Validate the Dexscreener panel is present
    dsPanel = os.getenv('DS_PANEL')
    await findAndCheckElement(
        page=page,
        selector=dsPanel
    )

