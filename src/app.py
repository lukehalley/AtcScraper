import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, BrowserContext

from src.scrape.dexscreener.dexscreener_Init import validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import getNetworkListFromSidebar
from src.utils.env import checkIsDocker

load_dotenv()
isDocker = checkIsDocker()

async def runScrapes(websiteName, websiteUrl, browser: BrowserContext) -> None:

    async with async_playwright() as p:

        page = await browser.new_page()
        print(websiteName)
        await page.goto(websiteUrl)

        # Dexscreener Scraping ##############
        # Init Dexscreener
        # validateDexscreenerInit(
        #     driver=driver
        # )
        #
        # # Get Network List
        # networkDictionary = getNetworkListFromSidebar(
        #     driver=driver
        # )
        #
        # # networkDictionary = {
        # #     'harmony': {'url': 'https://dexscreener.com/harmony'}
        # # }
        #
        # networkData = {}
        #
        # for networkName, networkDetails in networkDictionary.items():
        #
        #     if networkName not in networkData:
        #         networkData[networkName] = {}
        #
        #     print(f"Scraping: {networkName}...")
        #     driver.get(networkDetails["url"])
        #
        #     dexDictionary = getDexListFromTabs(
        #         driver=driver
        #     )
        #
        #     for dexName, dexDetails in dexDictionary.items():
        #
        #         print(f"  - {dexName}")
        #
        #         if dexName not in networkData[networkName]:
        #             networkData[networkName][dexName] = {}
        #
        #         driver.get(dexDetails["url"])
        #
        #         networkData[networkName][dexName] = getTokensFromTable(
        #             driver=driver,
        #             networkName=networkName,
        #             dexName=dexName
        #         )
        #
        #     with open("networkData.json", "w") as outfile:
        #         json.dump(networkData, outfile)
        #
        #     print(websiteName)
        #     page = await browser.new_page()
        #     await page.goto(websiteUrl)
        #     await page.screenshot(path=f'imgs/{websiteName}.jpg', type="jpeg")

async def main() -> None:
    async with async_playwright() as p:

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=False,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
        )

        # Get + Navigate To DS Root

        page = await browser.new_page()

        await validateDexscreenerInit(
            page=page
        )

        networks = await getNetworkListFromSidebar(
            page=page
        )

        data = {
            "google": "https://www.google.com/",
            "geeks": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "1": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "2": "https://www.google.com/",
            "3": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "4": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "5": "https://www.google.com/",
            "6": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "7": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "8": "https://www.google.com/",
            "9": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "10": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "11": "https://www.google.com/",
            "12": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "13": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
        }

        await asyncio.gather(*(runScrapes(websiteName, websiteUrl, browser) for websiteName, websiteUrl in data.items()))
        await browser.close()

# Function that setup the browser parameters and return browser object.
def lambda_handler(event, context):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps({
            "message": "This is the message in a JSON object."
        })
    }

    return response

if __name__ == "__main__" and not isDocker:

    lambda_handler(None, None)