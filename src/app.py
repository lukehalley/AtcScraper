import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from faker import Faker
from playwright.async_api import async_playwright, BrowserContext

from src.playwright.playwright_Setup import getBrowsersArgs
from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import validateDexscreenerInit, getDexscreenerRoot
from src.scrape.dexscreener.dexscreener_Scrape import getNetworkList, getDexListFromTabs, getTokensForDex
from src.utils.env import checkIsDocker

load_dotenv()
isDocker = checkIsDocker()

MAX_CONCURRENCY = int(os.getenv('MAX_CONCURRENCY'))

async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))

async def gatherNetworkDexs(networkName, networkDetails, browser: BrowserContext):

    page = await newPage(browser=browser)

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

async def main():
    async with async_playwright() as p:

        browserArgs = getBrowsersArgs()

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=False,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Get + Navigate To DS Root
        page = await newPage(browser=browser)

        # Navigate To The Dexscreener Home
        dexScreenerHome = getDexscreenerRoot()
        await page.goto(dexScreenerHome)

        await validateDexscreenerInit(
            page=page
        )



        networkDictionary = await getNetworkList(
            page=page
        )

        networkDictionary = {'ethereum': {'url': 'https://dexscreener.com/ethereum'}}

        networksToSkip = os.getenv('NETWORKS_TO_SKIP').split(",")


        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]



        await page.close()

        tasks = [gatherNetworkDexs(networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()]

        allNetworkDexs = await gather_with_concurrency(MAX_CONCURRENCY, *tasks)

        await browser.close()

        finalData = []

        for network in allNetworkDexs:
            networkName = list(network.keys())[0]
            networkDexs = network[networkName]

            tasks = [getTokensForDex(networkName, dexDetail) for dexDetail in networkDexs]

            result = await gather_with_concurrency(MAX_CONCURRENCY, *tasks)
            finalData.append(result)

            await browser.close()

        return finalData


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