from multiprocessing import Pool

from dotenv import load_dotenv

from src.db.actions.actions_Tokens import updateUnavailableTokensToNull
from src.db.querys.querys_Tokens import fillTokenDecimals

load_dotenv()

import os
import time
from pathlib import Path
from faker import Faker
from playwright.sync_api import sync_playwright, BrowserContext

from src.db.actions.actions_Pairs import clearPairsRankingTable
from src.db.actions.actions_Setup import initDBConnection
from src.playwright.playwright_Hacks import safePageLoad
from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs, gatherPairsForDex, \
    gatherMetadataForPair
from src.utils.aws.aws_S3 import downloadAbisFromS3
from src.utils.env.env_Environment import checkHeadless
from src.utils.misc.misc_Lazy import checkIsLazyMode
from src.utils.time.time_Calculations import getNicePerfTime
from src.db.querys.querys_Pairs import getAnalysedPairs, fillNullTokenAddresses

# Import helpers

# Load the .env file
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging

def scrape():

    # Set up logging
    logger = setupLogging()

    printSeparator()
    logger.info(f"ATC Scraper")
    printSeparator(newLine=True)

    # Init MySQL DB
    dbConnection = initDBConnection()

    # Wipe the ranking the table
    clearPairsRankingTable(
        dbConnection=dbConnection
    )

    # Download All Out Abis From S3
    printSeparator()
    logger.info(f"Syncing Abis From S3")
    printSeparator()
    downloadAbisFromS3()
    printSeparator(newLine=True)

    # Log setup message
    printSeparator()
    logger.info(f"Dex Screener Setup")
    logger.info(f"Collecting Max Pairs: {os.getenv('AMOUNT_OF_PAIRS_TO_COLLECT')}")
    printSeparator()

    # Check if we want to run in headless mode or not
    if checkHeadless():
        logger.info(f"Starting headless Chromium...")
    else:
        logger.info(f"Starting Chromium...")

    with sync_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = playwright.chromium.launch_persistent_context(
            headless=checkHeadless(),
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=Faker().user_agent(),
        )

        # Create new tab/page
        page = newPage(browser=browser)

        # Log that chromium started
        logger.info(f"Chromium started.")
        printSeparator()

        # Navigate to the Dexscreener Home
        dexScreenerHome = getDexscreenerRoot()
        logger.info(f"Navigating to {dexScreenerHome}...")

        # Wait for it to load
        safePageLoad(
            page=page,
            url=dexScreenerHome
        )

        # Confirm were there
        logger.info(f"Navigated to Dexscreener.")
        printSeparator()

        # Check some key elements exist so we know we loaded correctly
        logger.info(f"Validating Dexscreener has loaded...")
        validateDexscreenerInit(
            page=page
        )

        # Confirm validation
        logger.info(f"Dexscreener validated.")
        printSeparator(True)

        # Gather all the networks from the sidebar
        printSeparator()
        logger.info(f"Gathering Dex Screener Networks")
        printSeparator()

        # Get a dictionary of networks we can scrape
        networkDictionary = gatherNetworkList(
            dbConnection=dbConnection,
            page=page
        )

        # Count how many networks we got
        amountOfNetworks = len(networkDictionary.keys())

        # Delete any networks we have declared to be skipped
        networksToSkip = os.getenv('NETWORKS_TO_SKIP').split(",")
        logger.info(f"{amountOfNetworks} Networks Gathered")
        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]

        # Print out skipped networks if we have some
        if len(networksToSkip) > 0:
            logger.info(f"Skipping Networks: {networksToSkip}")

        if checkIsLazyMode():
            firstNetwork = next(iter(networkDictionary))
            networkDictionary = {
                f"{firstNetwork}":
                    [networkDictionary.pop(k) for k in list(networkDictionary.keys()) if k == f'{firstNetwork}'][0]
            }

        # Close the tab as we don't need it anymore
        page.close()

    # Separator
    printSeparator(True)

    # Log that we are going to collect all dexs for each network
    printSeparator()
    logger.info(f"Gathering Dex Screener Dexs")
    printSeparator()

    # Create A Pool For Dex Gather
    networksToCollect = []
    for networkName, networkDetails in networkDictionary.items():

        arg = {
            "networkName": networkName,
            "networkDetails": networkDetails
        }

        networksToCollect.append(arg)

    # Start Timer
    gatherNetworkDexsStart = time.perf_counter()

    # Create A Pool For Recipe Simulation
    # Map Our Recipes To The Pool An Run
    recipeSimulationPool = Pool(processes=None)
    collectedNetworkDexs = recipeSimulationPool.map(gatherNetworkDexs, networksToCollect)
    recipeSimulationPool.close()

    # Stop Timer
    gatherNetworkDexsEnd = time.perf_counter()

    # Build Timer Str
    gatherNetworkDexsTimerStr = getNicePerfTime(timeDiff=gatherNetworkDexsEnd - gatherNetworkDexsStart)

    # Parse Collected Data
    nonEmptyNetworks = [network for network in collectedNetworkDexs if network is not None]
    finalNetworkDexs = [item for item in nonEmptyNetworks if item]

    combinedDexs = [item for sublist in [i for sub in finalNetworkDexs for i in sub if not isinstance(i, str)] for item in sublist]

    # Count how many networks and dexs we collected
    collectedNetworks = len(finalNetworkDexs)
    collectedDexs = len(combinedDexs)

    logger.info(f"Collected {collectedDexs} Dexs Across {collectedNetworks} Networks")
    logger.info(f"Took {gatherNetworkDexsTimerStr}")

    printSeparator()

    for networkDexs in finalNetworkDexs:
        logger.info(f"{(networkDexs[0]).upper()}: {len(networkDexs[0])} Dex(s)")

    if collectedNetworks > 0 and collectedDexs > 0:

        # Separator
        printSeparator(True)

        # List which will hold all the data we scraped for all networks
        finalData = {}

        # Log that we are going to collect the (top 100 by liquidity) tokens for each dex
        printSeparator()
        logger.info(f"Gathering Dex Tokens")
        printSeparator()

        # Start Timer
        gatherDexPairsStart = time.perf_counter()

        # Collect all dex pairs
        recipeSimulationPool = Pool(processes=None)
        collectedDexPairs = recipeSimulationPool.map(gatherPairsForDex, combinedDexs)
        recipeSimulationPool.close()

        # Stop Timer
        gatherDexPairsEnd = time.perf_counter()

        # Build Timer Str
        gatherDexPairsTimerStr = getNicePerfTime(timeDiff=gatherDexPairsEnd - gatherDexPairsStart)

        # Process Data
        nonEmptyDexPairs = [x for x in collectedDexPairs if x != []]
        combinedDexPairs = [p for pair in nonEmptyDexPairs for p in pair]

        # Print Outcome
        logger.info(f"Collected {len(combinedDexPairs)} Pairs Across {len(nonEmptyDexPairs)} Dexs")
        logger.info(f"Took {gatherDexPairsTimerStr}")
        printSeparator()

        # Log Count
        for dexPairs in nonEmptyDexPairs:
            networkName = dexPairs[0]["network"]["network"]
            dexName = dexPairs[0]["dex"]["dex"]
            logger.info(f"{dexName.upper()} On {networkName.upper()}: {len(dexPairs)} Pairs(s)")

        analysedPairs = getAnalysedPairs(dbConnection=dbConnection)

        unanalysedPairs = [pair for pair in combinedDexPairs if pair["pair"]["db"]["dbId"] not in analysedPairs]

        pairMetadataPool = Pool(processes=1)
        collectedPairMetadata = pairMetadataPool.map(gatherMetadataForPair, unanalysedPairs)
        pairMetadataPool.close()

        # Set The Blank
        updateUnavailableTokensToNull(
            dbConnection=dbConnection
        )

        printSeparator()
        logger.info(f"Getting Missing Token Addresses From Dexscreener API")
        printSeparator()

        fillNullTokenAddresses(dbConnection=dbConnection)

        printSeparator(newLine=True)

        printSeparator()
        logger.info(f"Getting Missing Token Decimals")
        printSeparator()

        fillTokenDecimals(
            dbConnection=dbConnection
        )

        printSeparator(True)

        # Return our final data
        return finalData


        # # Get our ending time
        # timerString = getMinSecString(time.perf_counter() - startingTime)
        #
        # # Log that out scraping is done
        # printSeparator()
        # logger.info(f"Dex Screener Scrape Complete ✅")
        # logger.info(f"Took: {timerString}")
        # printSeparator()

if __name__ == '__main__':
    # Get our starting time
    startingTime = time.perf_counter()

    scrape()
