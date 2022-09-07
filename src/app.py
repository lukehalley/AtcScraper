import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, BrowserContext

from src.scrape.dexscreener.dexscreener_Init import validateDexscreenerInit, getDexscreenerRoot
from src.scrape.dexscreener.dexscreener_Scrape import getNetworkList, getDexListFromTabs, getTokensForDex
from src.utils.env import checkIsDocker

load_dotenv()
isDocker = checkIsDocker()

async def gatherNetworkDexs(networkName, networkDetails, browser: BrowserContext):

    page = await browser.new_page()
    print(networkName)
    await page.goto(networkDetails["url"])

    # Init Dexscreener
    await validateDexscreenerInit(
        page=page
    )

    print(f"Scraping: {networkName.title()}...")

    networksDexs = await getDexListFromTabs(
        page=page
    )

    await page.close()

    obj = {
        networkName: networksDexs
    }

    return obj

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

        # Navigate To The Dexscreener Home
        dexScreenerHome = getDexscreenerRoot()
        await page.goto(dexScreenerHome)

        await validateDexscreenerInit(
            page=page
        )

        networkDictionary = await getNetworkList(
            page=page
        )

        await page.close()

        allNetworkDexs = await asyncio.gather(*(gatherNetworkDexs(networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()))

        finalData = []

        for network in allNetworkDexs:
            networkName = list(network.keys())[0]
            networkDexs = network[networkName]
            result = await asyncio.gather(*(getTokensForDex(networkName, dexDetail, browser) for dexDetail in networkDexs))
            finalData.append(result)

        x = 1


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