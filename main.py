import itertools
from multiprocessing import Pool

from dotenv import load_dotenv

from src.chain.decode.decode_Tx import decodeTx
from src.db.actions.actions_Tokens import updateUnavailableTokensToNull
from src.db.querys.querys_Tokens import fillTokenDecimals, getTokensWithMissingDecimals

load_dotenv()

import os
import time
from pathlib import Path
from faker import Faker
from playwright.sync_api import sync_playwright, BrowserContext

from src.db.actions.actions_Pairs import clearPairsRankingTable
from src.playwright.playwright_Hacks import safePageLoad
from src.playwright.playwright_Utils import newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs, gatherPairsForDex, \
    gatherMetadataForPair
from src.utils.aws.aws_S3 import downloadAbisFromS3
from src.utils.env.env_Environment import checkHeadless
from src.utils.misc.misc_Lazy import checkIsLazyMode
from src.utils.time.time_Calculations import getNicePerfTime
from src.db.querys.querys_Pairs import getAnalysedPairs, getPairsWithNullTokenAddresses, \
    fillPairAddressesDecimals

# Import helpers

# Load the .env file
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging


def scrape():
    masterStartTime = time.perf_counter()

    # Set up logging
    logger = setupLogging()

    printSeparator()
    logger.info(f"ATC Scraper")
    printSeparator(newLine=True)

    # Wipe the ranking the table
    clearPairsRankingTable()

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

    combinedDexs = [item for sublist in [i for sub in finalNetworkDexs for i in sub if not isinstance(i, str)] for item
                    in sublist]

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

        #################################################################################
        # Gather Pairs
        #################################################################################

        # Log that we are going to collect the (top 100 by liquidity) tokens for each dex
        printSeparator()
        logger.info(f"Gathering Dex Pairs")
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
            dexName = dexPairs[0]["dex"]["dex"]["name"]
            logger.info(f"{dexName.upper()} On {networkName.upper()}: {len(dexPairs)} Pairs(s)")

        printSeparator(newLine=True)

        #################################################################################
        # Gather Pair Metadata + Transactions
        #################################################################################

        # Get Analysed Pairs
        analysedPairs = getAnalysedPairs()
        unanalysedPairs = [pair for pair in combinedDexPairs if pair["pair"]["db"]["dbId"] not in analysedPairs]

        printSeparator()
        logger.info(f"Gathering Unprocessed Pair Metadata + Transactions")
        printSeparator()

        logger.info(f"Getting {len(unanalysedPairs)} Pair's Metadata")

        printSeparator()

        if checkIsLazyMode():
            unanalysedPairs = unanalysedPairs[0:99]

        # Start Timer
        gatherPairRoutesStart = time.perf_counter()

        pairMetadataPool = Pool(processes=None)
        transactionsToDecode = pairMetadataPool.map(gatherMetadataForPair, unanalysedPairs)
        pairMetadataPool.close()

        # Stop Timer
        gatherPairRoutesEnd = time.perf_counter()

        # Build Timer Str
        gatherPairRoutesTimerStr = getNicePerfTime(timeDiff=gatherPairRoutesEnd - gatherPairRoutesStart)

        validTransactionsToDecode = [transactionToDecode for transactionToDecode in transactionsToDecode if
                                     transactionToDecode]
        combinedTransactions = list(itertools.chain(*validTransactionsToDecode))

        # Print Outcome
        printSeparator()
        logger.info(f"Took {gatherPairRoutesTimerStr}")
        printSeparator(newLine=True)

        #################################################################################
        # Decode Transactions For Routes
        #################################################################################

        printSeparator()
        logger.info(f"Decoding Transactions For Routes")
        printSeparator()

        if combinedTransactions:

            logger.info(f"Decoding {len(combinedTransactions)} Pair Transactions")

            printSeparator()

            # Start Timer
            decodeTransactionsStart = time.perf_counter()

            decodeTransactionsPool = Pool(processes=None)
            decodedRoutes = decodeTransactionsPool.map(decodeTx, combinedTransactions)
            decodeTransactionsPool.close()

            # Stop Timer
            decodeTransactionsEnd = time.perf_counter()

            # Build Timer Str
            decodeTransactionsTimerStr = getNicePerfTime(timeDiff=decodeTransactionsEnd - decodeTransactionsStart)

            validRoutes = [decodedRoute for decodedRoute in decodedRoutes if decodedRoute]
            combinedRoutes = list(itertools.chain(*validRoutes))

            printSeparator()

            # Print Outcome
            logger.info(f"Collected {len(combinedRoutes)} Routes")
            logger.info(f"Took {decodeTransactionsTimerStr}")
            printSeparator(newLine=True)

        else:

            # Print Outcome
            logger.info(f"No Routes To Collect!")
            printSeparator(newLine=True)

        #################################################################################
        # Set Unavailable Tokens To Null
        #################################################################################

        printSeparator()
        logger.info(f"Setting Unavailable Tokens To Null")
        printSeparator()

        # Set The Blank
        updateUnavailableTokensToNull()

        logger.info(f"All Unavailable Tokens Set To Null")
        printSeparator(newLine=True)

        #################################################################################
        # Getting Missing Token Decimals
        #################################################################################

        printSeparator()
        logger.info(f"Getting Missing Token Decimals")
        printSeparator()

        tokensToGetDecimalsFor = getTokensWithMissingDecimals()

        if tokensToGetDecimalsFor:

            # Start Timer
            missingTokenDecimalsStart = time.perf_counter()

            missingTokenDecimalsPool = Pool(processes=None)
            decimalsRetrieved = missingTokenDecimalsPool.map(fillTokenDecimals, tokensToGetDecimalsFor)
            missingTokenDecimalsPool.close()

            updatedDecimals = [decimalRetrieved for decimalRetrieved in decimalsRetrieved if decimalRetrieved]

            # Stop Timer
            missingTokenDecimalsEnd = time.perf_counter()

            # Build Timer Str
            missingTokenDecimalsTimerStr = getNicePerfTime(timeDiff=missingTokenDecimalsEnd - missingTokenDecimalsStart)

            # Print Outcome
            logger.info(f"Added {len(updatedDecimals)} Token Decimals")
            logger.info(f"Took {missingTokenDecimalsTimerStr}")
            printSeparator(newLine=True)

        else:

            # Print Outcome
            logger.info(f"No Tokens Decimals To Retrieve")
            printSeparator(newLine=True)

        #################################################################################
        # Get Missing Token Addresses From Dexscreener API
        #################################################################################

        printSeparator()
        logger.info(f"Getting Missing Token Addresses From Dexscreener API")
        printSeparator()

        dbPairs = getPairsWithNullTokenAddresses()

        if dbPairs:

            logger.info(f"Getting Addresses For {len(dbPairs)} Pairs")

            # Start Timer
            missingTokenRetrievalStart = time.perf_counter()

            missingTokenRetrievalPool = Pool(processes=None)
            updateResults = missingTokenRetrievalPool.map(fillPairAddressesDecimals, dbPairs)
            missingTokenRetrievalPool.close()

            updatedTokens = [updateResult for updateResult in updateResults if updateResult]

            # Stop Timer
            missingTokenRetrievalEnd = time.perf_counter()

            # Build Timer Str
            missingTokenRetrievalTimerStr = getNicePerfTime(
                timeDiff=missingTokenRetrievalEnd - missingTokenRetrievalStart)

            # Print Outcome
            printSeparator()
            logger.info(f"Updated {len(updatedTokens)} Pairs")
            logger.info(f"Took {missingTokenRetrievalTimerStr}")
            printSeparator(newLine=True)

        else:

            # Print Outcome
            logger.info(f"No Pairs To Update!")
            printSeparator(newLine=True)

        #################################################################################
        # End
        #################################################################################

        # Get Final End Timer
        masterEndTime = time.perf_counter()

        # Build Timer Str
        masterTimerStr = getNicePerfTime(timeDiff=masterEndTime - masterStartTime)

        # Log that out scraping is done
        printSeparator()
        logger.info(f"Dex Screener Scrape Complete ✅")
        logger.info(f"Took: {masterTimerStr}")
        printSeparator()


if __name__ == '__main__':
    scrape()
