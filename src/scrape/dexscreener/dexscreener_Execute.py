import os
from pathlib import Path

from faker import Faker
from playwright.async_api import async_playwright, BrowserContext

from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs, gatherTokensForDex
from src.utils.env.utils_Env import checkIsDocker, checkHeadless
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.tasks.task_AyySync import gatherWithConcurrency, getmaxConcurrency

logger = getProjectLogger()

async def scrapeDexScreener():

    maxConcurrency = getmaxConcurrency()

    printSeparator()
    logger.info(f"Dex Screener Setup")
    logger.info(f"Concurrency: {maxConcurrency}")
    printSeparator()

    async with async_playwright() as p:

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        # Run in headless if we are running in Docker
        runHeadless = checkHeadless()

        if runHeadless:
            logger.info(f"Starting headless Chromium...")
        else:
            logger.info(f"Starting Chromium...")

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Get + Navigate To DS Root
        page = await newPage(browser=browser)

        logger.info(f"Chromium started.")
        printSeparator()

        # Navigate To The Dexscreener Home
        dexScreenerHome = getDexscreenerRoot()

        logger.info(f"Navigating to {dexScreenerHome}...")

        await page.goto(dexScreenerHome)

        logger.info(f"Navigated to Dexscreener.")
        printSeparator()

        logger.info(f"Validating Dexscreener has loaded...")

        await validateDexscreenerInit(
            page=page
        )

        logger.info(f"Dexscreener validated.")
        printSeparator(True)

        printSeparator()
        logger.info(f"Gathering Dex Screener Networks")
        printSeparator()

        networkDictionary = await gatherNetworkList(
            page=page
        )
        amountOfNetworks = len(networkDictionary.keys())

        # networkDictionary = {'ethereum': {'url': 'https://dexscreener.com/ethereum'}}

        networksToSkip = os.getenv('NETWORKS_TO_SKIP').split(",")

        logger.info(f"{amountOfNetworks} available to scrape.")

        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]

        if len(networksToSkip) > 0:
            logger.info(f"Skipping networks: {networksToSkip}")

        await page.close()

        printSeparator(True)

        printSeparator()
        logger.info(f"Gathering Dex Screener Dexs")
        printSeparator()

        tasks = [gatherNetworkDexs(networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()]

        allNetworkDexs = await gatherWithConcurrency(maxConcurrency, *tasks)

        await browser.close()

        printSeparator(True)

        finalData = []

        printSeparator()
        logger.info(f"Gathering Dex Tokens")
        printSeparator()

        for network in allNetworkDexs:

            networkName = list(network.keys())[0]
            networkDexs = network[networkName]

            logger.info(f"{networkName.title()}:")

            tasks = [gatherTokensForDex(networkName, dexDetail) for dexDetail in networkDexs]

            result = await gatherWithConcurrency(maxConcurrency, *tasks)
            finalData.append(result)

            await browser.close()

            printSeparator()

        return finalData
