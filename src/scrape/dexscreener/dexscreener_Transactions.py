import json
from pathlib import Path

from faker import Faker
from playwright.sync_api import sync_playwright, BrowserContext

from src.playwright.playwright_Hacks import safePageLoad
from src.playwright.playwright_Utils import newPage
from src.utils.env.env_Environment import checkHeadless

def gatherTransactionsForPair(transactionUrl):

    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    # Check if we want to start our browser in headless
    runHeadless = checkHeadless()

    # Create async instance of playwright
    with sync_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = playwright.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = newPage(browser=browser)

        # Navigate to the dexs url
        safePageLoad(
            page=page,
            url=transactionUrl
        )

        innerText = page.inner_text("*")

        resultJson = json.loads(innerText)

        return resultJson

