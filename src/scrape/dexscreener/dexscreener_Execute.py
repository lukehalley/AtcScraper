import os
import sys
from pathlib import Path

from faker import Faker
from playwright.async_api import async_playwright, BrowserContext

from src.db.db_Admin import wipeDb
from src.db.db_Setup import initDBConnection
from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs, gatherTokensForDex
from src.utils.data.data_Booleans import strToBool
from src.utils.env.utils_Env import checkHeadless, checkIsDocker
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.tasks.task_AyySync import gatherWithConcurrency, getmaxConcurrency

logger = getProjectLogger()
lazyMode = strToBool(os.environ.get("LAZY_MODE"))

# Function which runs the scraping of Dexscreener
async def scrapeDexScreener():

    # Get how many task we run in concurrently
    maxConcurrency = getmaxConcurrency()

    # Log setup message
    printSeparator()
    logger.info(f"Dex Screener Setup")
    logger.info(f"Concurrency: {maxConcurrency}")
    printSeparator()

    # Enter an async state
    async with async_playwright() as p:

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        # Run in headless if we are running in Docker
        runHeadless = checkHeadless()

        # Check if we want to run in headless mode or not
        if runHeadless:
            logger.info(f"Starting headless Chromium...")
        else:
            logger.info(f"Starting Chromium...")

        # Setup browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Create new tab/page
        page = await newPage(browser=browser)

        # Log that chromium started
        logger.info(f"Chromium started.")
        printSeparator()

        # Navigate to the Dexscreener Home
        dexScreenerHome = getDexscreenerRoot()
        logger.info(f"Navigating to {dexScreenerHome}...")
        await page.goto(dexScreenerHome)

        # Confirm were there
        logger.info(f"Navigated to Dexscreener.")
        printSeparator()

        # Check some key elements exist so we know we loaded correctly
        logger.info(f"Validating Dexscreener has loaded...")
        await validateDexscreenerInit(
            page=page
        )

        # Confirm validation
        logger.info(f"Dexscreener validated.")
        printSeparator(True)

        # Init MySQL DB
        dbConnection = initDBConnection()

        # Wipe DB everytime we run for testing
        WIPE_DB = strToBool(os.getenv("WIPE_DB")) and not checkIsDocker()
        if WIPE_DB:
            wipeDb(dbConnection=dbConnection)

        # Gather all the networks from the sidebar
        printSeparator()
        logger.info(f"Gathering Dex Screener Networks")
        printSeparator()
        networkDictionary = await gatherNetworkList(
            dbConnection=dbConnection,
            page=page
        )

        # Count how many networks we got
        amountOfNetworks = len(networkDictionary.keys())

        # Delete any networks we have declared to be skipped
        networksToSkip = os.getenv('NETWORKS_TO_SKIP').split(",")
        logger.info(f"{amountOfNetworks} available to scrape.")
        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]

        # Print out skipped networks if we have some
        if len(networksToSkip) > 0:
            logger.info(f"Skipping networks: {networksToSkip}")

        if lazyMode:
            networkDictionary = {
                "ethereum": [networkDictionary.pop(k) for k in list(networkDictionary.keys()) if k == 'ethereum'][0]
            }

        # Close the tab as we don't need it anymore
        await page.close()

        # Separator
        printSeparator(True)

        # Log that we are going to collect all dexs for each network
        printSeparator()
        logger.info(f"Gathering Dex Screener Dexs")
        printSeparator()

        # Asynchronously gather each network's dexs
        tasks = [gatherNetworkDexs(dbConnection, networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()]
        allNetworkDexs = await gatherWithConcurrency(maxConcurrency, *tasks)
        finalNetworkDexs = [network for network in allNetworkDexs if network is not None]

        # Count how many dexs we collected
        collectedNetworks = len(finalNetworkDexs)

        if collectedNetworks > 0:

            # Close the tab as we don't need it anymore
            await browser.close()

            # Separator
            printSeparator(True)

            # List which will hold all the data we scraped for all networks
            finalData = {}

            # Log that we are going to collect the (top 100 by liquidity) tokens for each dex
            printSeparator()
            logger.info(f"Gathering Dex Tokens")
            printSeparator()

            # Loop through each network
            for network in finalNetworkDexs:

                # Get the index of the network and form a string that we can use to
                # count how far we are through the list of networks 1/40 etc...
                networkIndex = finalNetworkDexs.index(network) + 1
                networkCountStr = f"{networkIndex}/{collectedNetworks}"

                # Get the networks name and dexs
                networkName = list(network.keys())[0]
                networkDexs = network[networkName]

                # Add network to the final dict
                if networkName not in finalData:
                    finalData[networkName] = {}

                # Log the current network and the progress
                logger.info(f"{networkName.title()} [{networkCountStr}]")

                # Asynchronously gather each dex's tokens
                tasks = [gatherTokensForDex(dbConnection, networkName, dexDetail) for dexDetail in networkDexs]
                results = await gatherWithConcurrency(maxConcurrency, *tasks)

                # Collect the network results and and place them in their respective places
                for result in results:
                    dexName = result[0]["dex"]["dex"]
                    finalData[networkName][dexName] = result

                # Close the tab as we don't need it anymore
                await browser.close()

                # Check if we are on the last network
                if networkIndex == collectedNetworks:
                    printSeparator(True)
                else:
                    printSeparator()

            # Return our final data
            return finalData

        else:

            sys.exit("No Networks Were Scraped!")
