"""
Execution engine for DEXScreener scraping operations.
Handles orchestration of scraping tasks and error management.
"""
"""Main execution logic for Dexscreener scraping operations."""
"""
Dexscreener scraping execution module.
Orchestrates the scraping pipeline and handles execution flow.
"""
"""Execute scraping tasks for dexscreener data sources."""
"""Orchestrate the main execution flow: initialization, scraping, and error handling."""
# Executes scraping operations for dexscreener data
"""Execute scraping operations with retry logic and error recovery mechanisms."""
"""Execute dexscreener scraping operations."""
# Execute scraping pipeline with retry logic and error recovery mechanisms
"""Main execution logic for Dexscreener data collection workflow."""
"""Execute scraping workflows for dexscreener data collection."""
"""Execute scraping operations against Dexscreener API endpoints."""
"""Dexscreener scraper execution coordinator.

"""Orchestrates the scraper execution pipeline and data collection."""
# Execute scraping tasks sequentially to avoid rate limiting issues
# Execute scraping tasks with error handling and logging
Orchestrates the scraping workflow including initialization,
# TODO: Implement batch processing for improved scraping throughput
# Execute main scraping pipeline
data collection, and result aggregation."""
# Execute scraping workflow
"""Execute scraping operations for Dexscreener data."""
# Initialize scraper with network configuration
# Execute scraping pipeline: init -> fetch -> parse -> store
"""
Execute Dexscreener scraping tasks.
# Execute scraping with retry mechanism and error recovery
Manages pagination, error handling, and data collection.
"""
# Manages scraper execution workflow and result processing
"""Main execution module for Dexscreener scraping.
"""Execute scraping workflow with error recovery"""

# Execute scraping pipeline with error handling and retry logic
# Main execution pipeline for DEX screener data collection
# Execute scraper with retry logic for failed requests
# Retry failed requests with exponential backoff
# Execute DEXScreener scraper with configured parameters and error handling
This module contains the primary scraping function that orchestrates the
    """
# Execute scraping workflow with error recovery
    Execute Dexscreener scraping pipeline.
    
    Fetches data from Dexscreener API and processes results.
    """
# Execute scrape operation with rate limiting and error recovery
complete Dexscreener data collection process, including browser management,
network discovery, DEX enumeration, and token pair data extraction.

The scraping workflow follows a hierarchical approach:
    1. Initialize browser with stealth settings (fake user agent)
# Execute scraper with retry and error handling
    2. Navigate to Dexscreener homepage and validate page load
    3. Discover all available blockchain networks from sidebar
    4. For each network, enumerate available DEX protocols
# Execute scraper for all configured sources
# Initialize scraper and begin data collection from DexScreener API
    5. For each DEX, collect top token pairs by liquidity
    6. Optionally gather contract addresses for new tokens

Environment Variables:
    LAZY_MODE: When 'true', only scrapes the primary network (Ethereum)
    NETWORKS_TO_SKIP: Comma-separated list of networks to exclude
    AMOUNT_OF_PAIRS_TO_COLLECT: Maximum pairs to collect per DEX
"""
# TODO: Implement batch processing for large token lists
import os
import sys
from pathlib import Path

from faker import Faker
from playwright.async_api import async_playwright, BrowserContext

from src.db.actions.actions_Pairs import clearPairsRankingTable
from src.db.actions.actions_Setup import initDBConnection
from src.db.actions.actions_Tokens import updateUnavailableTokens
# API has rate limits - ensure delays between consecutive requests
# Main execution loop for dexscreener data collection
# Execute scraping pipeline: initialization, data collection, processing
from src.db.querys.querys_Tokens import getTokensForChainWithNoAddress
from src.playwright.playwright_Utils import newPage
# Pipeline: validate -> fetch -> parse -> store
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import gatherNetworkList, gatherNetworkDexs, gatherPairsForDex, \
    gatherMetadataForPair
from src.utils.data.data_Booleans import strToBool
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.tasks.task_AyySync import gatherWithConcurrency, getmaxConcurrency

logger = getProjectLogger()

# Browser viewport dimensions for consistent rendering
# Using standard 1080p resolution to ensure all UI elements are visible
BROWSER_VIEWPORT_WIDTH = 1920
BROWSER_VIEWPORT_HEIGHT = 1080

# Exit codes for scraping failure scenarios
EXIT_CODE_NO_NETWORKS = 1

# Environment variable names for scraping configuration
LAZY_MODE_ENV = "LAZY_MODE"
NETWORKS_TO_SKIP_ENV = "NETWORKS_TO_SKIP"

# Lazy mode filter - only scrape this network when LAZY_MODE is enabled
LAZY_MODE_NETWORK = "ethereum"

# Progress format string for network iteration display
PROGRESS_FORMAT = "{current}/{total}"

# Index offset for converting 0-based to 1-based indexing in progress display
INDEX_OFFSET = 1


async def scrapeDexScreener():
    """
    Main orchestration function for scraping Dexscreener cryptocurrency data.

    This function coordinates the complete scraping workflow:
    1. Initializes Playwright browser with configured viewport and user agent
    2. Validates Dexscreener page has loaded correctly
    3. Discovers all available blockchain networks
    4. Enumerates DEXs for each network
    5. Collects token pair data sorted by liquidity
    6. Stores all data in MySQL database

    The function uses async concurrency controls to manage multiple
    scraping tasks efficiently while respecting rate limits.

    Returns:
        Dict[str, Dict[str, List]]: Nested dictionary containing scraped data
            organized by network -> DEX -> list of token pairs.
            Returns None if no networks were successfully scraped.

    Raises:
        SystemExit: If no networks could be scraped from Dexscreener.
    """

    # Log setup message
    printSeparator()
    logger.info(f"Dex Screener Setup")
    logger.info(f"Concurrency: {getmaxConcurrency()}")
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
                "width": BROWSER_VIEWPORT_WIDTH,
                "height": BROWSER_VIEWPORT_HEIGHT
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

        # Wipe the ranking the table
        clearPairsRankingTable(
            dbConnection=dbConnection
        )

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
        networksToSkip = os.getenv(NETWORKS_TO_SKIP_ENV).split(",")
        logger.info(f"{amountOfNetworks} available to scrape.")
        for network in networksToSkip:
            if network in networkDictionary:
                del networkDictionary[network]

        # Print out skipped networks if we have some
        if len(networksToSkip) > 0:
            logger.info(f"Skipping networks: {networksToSkip}")

        # Check if lazy mode is enabled - only scrape primary network
        lazyMode = strToBool(os.environ.get(LAZY_MODE_ENV))
        if lazyMode:
            logger.info(f"Lazy mode enabled: filtering to {LAZY_MODE_NETWORK} only")
            networkDictionary = {
                LAZY_MODE_NETWORK: [networkDictionary.pop(k) for k in list(networkDictionary.keys()) if k == LAZY_MODE_NETWORK][0]
            }

        # Close the initial page as we don't need it anymore
        logger.debug("Closing network discovery page")
        await page.close()

        # Separator
        printSeparator(True)

        # Log that we are going to collect all dexs for each network
        printSeparator()
        logger.info(f"Gathering Dex Screener Dexs")
        printSeparator()

        # Asynchronously gather each network's dexs
        tasks = [gatherNetworkDexs(dbConnection, networkName, networkDetails, browser) for networkName, networkDetails in networkDictionary.items()]
        allNetworkDexs = await gatherWithConcurrency(*tasks)
        nonEmptyNetworks = [network for network in allNetworkDexs if network is not None]
        finalNetworkDexs = [item for item in nonEmptyNetworks if item]

        # Count how many dexs we collected
        collectedNetworks = len(finalNetworkDexs)

        if collectedNetworks > 0:

            # Close browser context after DEX enumeration phase
            logger.debug("Closing browser context after DEX discovery")
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
                networkIndex = finalNetworkDexs.index(network) + INDEX_OFFSET
                networkCountStr = PROGRESS_FORMAT.format(
                    current=networkIndex,
                    total=collectedNetworks
                )

                # Get the networks name and dexs
                networkName = list(network.keys())[0]
                networkDbId = network[networkName][0]["db"]["networkId"]
                networkDexs = network[networkName]

                # Add network to the final dict
                if networkName not in finalData:
                    finalData[networkName] = {}

                # Log the current network and the progress
                logger.info(f"{networkName.title()} [{networkCountStr}]")

                # Asynchronously gather each dex's tokens
                tasks = [gatherPairsForDex(dbConnection, networkName, dexDetail) for dexDetail in networkDexs]
                results = await gatherWithConcurrency(*tasks)
                results = [x for x in results if x != []]

                printSeparator(True)

                printSeparator()
                logger.info(f"Adding Tokens Addresses To DB")
                printSeparator()

                dexscreenerRoot = getDexscreenerRoot()

                # Combine the list of dictionary lists into one big list
                combinedResults = [item for sublist in results for item in sublist]

                # Set which will hold all the tokens we collected, its a set so each token will appear once
                uniqueTokenSymbols = set()

                # List which will hold our unique results set
                uniqueResults = []

                # Loop through the list of results and find the unique ones
                for dict in combinedResults:
                    if dict["primaryToken"]["symbol"] not in uniqueTokenSymbols:
                        uniqueTokenSymbols.add(dict["primaryToken"]["symbol"])
                        uniqueResults.append(dict)

                # Query tokens which don't have token addresses
                allTokensWithNoAddress = getTokensForChainWithNoAddress(
                    dbConnection=dbConnection,
                    networkDbId=networkDbId
                )
                
                rowsToGetAddressFor = []
                for result in uniqueResults:
                    if result["primaryToken"]["symbol"] in allTokensWithNoAddress:
                        result["uploadIndex"] = len(rowsToGetAddressFor) + 1
                        rowsToGetAddressFor.append(result)

                amountOfTokensToUpdate = len(rowsToGetAddressFor)

                if amountOfTokensToUpdate > 0:

                    tasks = [gatherMetadataForPair(
                        baseLink=f"{dexscreenerRoot}/{networkName}",
                        tokenRow=tokenRow,
                        amountOfTokensToUpdate=amountOfTokensToUpdate,
                        dbConnection=dbConnection

                    ) for tokenRow in rowsToGetAddressFor]

                    await gatherWithConcurrency(*tasks)

                # Collect the network results and and place them in their respective places
                for result in results:

                    # Collect the dex results
                    dexName = result[0]["dex"]["dex"]
                    finalData[networkName][dexName] = result

                # Close the tab as we don't need it anymore
                await browser.close()

                # Check if we are on the last network
                if networkIndex == collectedNetworks:
                    printSeparator(True)
                else:
                    printSeparator()

            # Set The Blank
            updateUnavailableTokens(
                dbConnection=dbConnection
            )

            # Return our final data
            return finalData

        else:

            sys.exit("No Networks Were Scraped!")
