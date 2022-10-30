import concurrent
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

from dotenv import load_dotenv

load_dotenv()

import os
import sys
import time
from pathlib import Path
from faker import Faker
from playwright.sync_api import sync_playwright, BrowserContext

from src.db.actions.actions_Pairs import clearPairsRankingTable
from src.db.actions.actions_Setup import initDBConnection
from src.playwright.playwright_Hacks import safePageLoad
from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs
from src.utils.aws.aws_S3 import downloadAbisFromS3
from src.utils.env.env_Environment import checkHeadless
from src.utils.misc.misc_Lazy import checkIsLazyMode
from src.utils.time.time_Calculations import getMinSecString

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
        logger.info(f"{amountOfNetworks} available to scrape.")
        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]

        # Print out skipped networks if we have some
        if len(networksToSkip) > 0:
            logger.info(f"Skipping networks: {networksToSkip}")

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

    args = []
    for networkName, networkDetails in networkDictionary.items():

        arg = {
            "networkName": networkName,
            "networkDetails": networkDetails
        }

        args.append(arg)

    # Create A Pool For Recipe Simulation
    recipeSimulationPool = Pool(processes=None)

    # Map Our Recipes To The Pool An Run
    simulationResults = recipeSimulationPool.map(gatherNetworkDexs, args)

    x = 1

    # Asynchronously gather each network's dexs
    # tasks = [gatherNetworkDexs(dbConnection, networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()]
    # allNetworkDexs = gatherWithConcurrency(*tasks)
    # nonEmptyNetworks = [network for network in allNetworkDexs if network is not None]
    # finalNetworkDexs = [item for item in nonEmptyNetworks if item]

    # Count how many dexs we collected
    # collectedNetworks = len(finalNetworkDexs)
    #
    # if collectedNetworks > 0:
    #
    #     # Close the tab as we don't need it anymore
    #     browser.close()
    #
    #     # Separator
    #     printSeparator(True)
    #
    #     # List which will hold all the data we scraped for all networks
    #     finalData = {}
    #
    #     # Log that we are going to collect the (top 100 by liquidity) tokens for each dex
    #     printSeparator()
    #     logger.info(f"Gathering Dex Tokens")
    #     printSeparator()
    #
    #     # Loop through each network
    #     for network in finalNetworkDexs:
    #
    #         # Get the index of the network and form a string that we can use to
    #         # count how far we are through the list of networks 1/40 etc...
    #         networkIndex = finalNetworkDexs.index(network) + 1
    #         networkCountStr = f"{networkIndex}/{collectedNetworks}"
    #
    #         # Get the networks name and dexs
    #         networkName = list(network.keys())[0]
    #         networkDbId = network[networkName][0]["db"]["networkId"]
    #         networkDexs = network[networkName]
    #
    #         if lazyMode:
    #             networkDexs = networkDexs[0:1]
    #
    #         # Add network to the final dict
    #         if networkName not in finalData:
    #             finalData[networkName] = {}
    #
    #         # Log the current network and the progress
    #         logger.info(f"{networkName.title()} [{networkCountStr}]")
    #
    #         # Asynchronously gather each dex's tokens
    #         tasks = [gatherPairsForDex(dbConnection, networkName, dexDetail) for dexDetail in networkDexs]
    #         results = gatherWithConcurrency(*tasks)
    #         results = [x for x in results if x != []]
    #
    #         printSeparator(True)
    #
    #         printSeparator()
    #         logger.info(f"Adding Tokens Addresses To DB")
    #         printSeparator()
    #
    #         dexscreenerRoot = getDexscreenerRoot()
    #
    #         # Combine the list of dictionary lists into one big list
    #         combinedResults = [item for sublist in results for item in sublist]
    #
    #         # Set which will hold all the tokens we collected, its a set so each token will appear once
    #         uniqueTokenSymbols = set()
    #
    #         # List which will hold our unique results set
    #         uniqueResults = []
    #
    #         # Loop through the list of results and find the unique ones
    #         for dict in combinedResults:
    #             if dict["primaryToken"]["symbol"] not in uniqueTokenSymbols:
    #                 uniqueTokenSymbols.add(dict["primaryToken"]["symbol"])
    #                 uniqueResults.append(dict)
    #
    #         rowsToGetMetadataFor = []
    #         for result in uniqueResults:
    #             result["uploadIndex"] = len(rowsToGetMetadataFor) + 1
    #             rowsToGetMetadataFor.append(result)
    #
    #         routerAddress, routerAbi = getDexRouterDetailsByDbId(
    #             dbConnection=dbConnection,
    #             dexDbid=rowsToGetMetadataFor[0]["dex"]["db"]["dbId"]
    #         )
    #
    #         rpcUrl = getNetworkRPCByDbId(
    #             dbConnection=dbConnection,
    #             networkDbId=rowsToGetMetadataFor[0]["network"]["db"]["dbId"]
    #         )
    #
    #         amountOfTokensToUpdate = len(rowsToGetMetadataFor)
    #
    #         tasks = [gatherMetadataForPair(
    #             baseLink=f"{dexscreenerRoot}/{networkName}",
    #             tokenRow=tokenRow,
    #             rpcUrl=rpcUrl,
    #             routerAddress=routerAddress,
    #             routerAbi=routerAbi,
    #             amountOfTokensToUpdate=amountOfTokensToUpdate,
    #             dbConnection=dbConnection
    #
    #         ) for tokenRow in rowsToGetMetadataFor]
    #
    #         gatherWithConcurrency(*tasks)
    #
    #         # Collect the network results and and place them in their respective places
    #         for result in results:
    #
    #             # Collect the dex results
    #             dexName = result[0]["dex"]["dex"]
    #             finalData[networkName][dexName] = result
    #
    #         # Close the tab as we don't need it anymore
    #         browser.close()
    #
    #         # Check if we are on the last network
    #         if networkIndex == collectedNetworks:
    #             printSeparator(True)
    #         else:
    #             printSeparator()
    #
    #     # Set The Blank
    #     updateUnavailableTokensToNull(
    #         dbConnection=dbConnection
    #     )
    #
    #     printSeparator()
    #     logger.info(f"Getting Missing Token Addresses From Dexscreener API")
    #     printSeparator()
    #
    #     fillNullTokenAddresses(dbConnection=dbConnection)
    #
    #     printSeparator(newLine=True)
    #
    #     printSeparator()
    #     logger.info(f"Getting Missing Token Decimals")
    #     printSeparator()
    #
    #     fillTokenDecimals(
    #         dbConnection=dbConnection
    #     )
    #
    #     printSeparator(True)
    #
    #     # Return our final data
    #     return finalData
    #
    #
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
