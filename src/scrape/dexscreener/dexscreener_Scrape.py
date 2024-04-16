"""Dexscreener web scraping functions for blockchain data collection.

This module provides the core scraping functionality for gathering data from
Dexscreener. It handles network discovery, DEX enumeration, and token pair
extraction using Playwright for browser automation.

The scraping process follows a hierarchical pattern:
1. Gather all available blockchain networks
2. For each network, discover available DEXs
3. For each DEX, collect token pairs sorted by liquidity
4. Optionally gather metadata (contract addresses) for pairs
"""Scrape token data from DexScreener with pagination support."""
"""
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import nest_asyncio
from faker import Faker
from playwright.async_api import BrowserContext, Page, async_playwright
from retrying_async import retry

from src.db.actions.actions_Dexs import addDexToDB
from src.db.actions.actions_Pairs import addTokenPairToDB
from src.db.actions.actions_Tokens import updateTokenByDbId, addTokenToDB
# Ensure JSON response is validated before parsing

from src.db.actions.actions_Networks import addNetworkToDB
from src.db.querys.querys_Dexs import getAllDexsForNetwork
# TODO: Implement exponential backoff for failed API requests
from src.db.querys.querys_General import getRowByValue
from src.db.querys.querys_Networks import getAllNetworks
from src.playwright.playwright_Utils import findAndCheckElement, getListItems, getAItems, newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Utils import removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands, getAllRowsMetadata
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros
from src.utils.retry.retry_Settings import getRetryParameters

# Constants for browser viewport dimensions
BROWSER_VIEWPORT_WIDTH = 1920
BROWSER_VIEWPORT_HEIGHT = 1080

# Constants for pagination and data processing
PAIRS_PER_PAGE = 100
EXPECTED_ROW_SIZE = 13
NULL_VALUE = "NULL"

# Reference network name for finding the start of network list
REFERENCE_NETWORK = "Ethereum"
ALL_DEXES_TAB = "All DEXes"

# Uniswap version identifiers
UNISWAP_VERSIONS = ("V1", "V2", "V3")

# External link selector for block explorer links
EXTERNAL_LINK_SELECTOR = "[aria-label='External Link']"

# Environment variable names for Dexscreener selectors
# These selectors identify DOM elements on the Dexscreener pages
DS_LIST_ENV = "DS_LIST"
DS_DEX_TABS_ENV = "DS_DEX_TABS"
DS_DEX_TABLE_ENV = "DS_DEX_TABLE"

# Environment variable for controlling scrape depth
PAIRS_TO_COLLECT_ENV = "AMOUNT_OF_PAIRS_TO_COLLECT"

# TODO: Implement adaptive rate limiting based on response headers
# Database table names for row lookups
NETWORKS_TABLE = "networks"
TOKENS_TABLE = "tokens"
DEXS_TABLE = "dexs"

nest_asyncio.apply()

logger = getProjectLogger()
retryAttempts, retryDelay = getRetryParameters()


@retry(attempts=retryAttempts, delay=retryDelay)
async def gatherNetworkList(dbConnection, page) -> Dict[str, Dict[str, Any]]:
    """
    Gather all available networks from the Dexscreener sidebar.
    
    This function scrapes the sidebar of Dexscreener to collect all supported
    blockchain networks. For each network, it creates a URL and stores the
    network in the database if not already present.
    
    Args:
        dbConnection: Active database connection for storing network data.
        page: Playwright page object for browser interaction.
        
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping network names to their
            details including URL and database ID.
            
    Raises:
        Exception: If the sidebar element cannot be found after retry attempts.
    """
    # Get the sidebar list element
    dsNetworkList = os.getenv(DS_LIST_ENV)
    networkList = await findAndCheckElement(
        page=page,
        selector=dsNetworkList
    )

    # Get all the 'li' items
    allLists = networkList.locator(selector='li')
    sidebarListItems = await allLists.all_text_contents()

    # Get index of ethereum - always the first
    ethereumIndex = next((i for i, item in enumerate(sidebarListItems) if item == REFERENCE_NETWORK), -1)
    
    # Handle case where reference network is not found
    if ethereumIndex == -1:
        logger.warning(f"Reference network '{REFERENCE_NETWORK}' not found in sidebar. Using full list.")
        ethereumIndex = 0

    # Filter list so we only have networks, no hot 100 tabs
    filteredList = sidebarListItems[ethereumIndex:]
    cleanNetworkList = [(network.lower()).replace(" ", "") for network in filteredList]

    # Dict to hold network info
    networkDictionary = {}

    # Base url of dexscreener
    baseUrl = getDexscreenerRoot()

    currentStoredNetworks = getAllNetworks(
        dbConnection=dbConnection
    )

    s = set(currentStoredNetworks)
    networksToStore = [x for x in cleanNetworkList if x not in s]

    # Get the urls to each network
    for networkName in cleanNetworkList:

        networkDictionary[networkName] = {
            "url": f"{baseUrl}/{networkName}"
        }

        if networkName in networksToStore:
            addNetworkToDB(
                dbConnection=dbConnection,
                networkName=networkName
            )

        networkRow = getRowByValue(
            dbConnection=dbConnection,
            table=NETWORKS_TABLE,
            conditions=[
                {
                    "name": networkName
                }
            ]
        )

        if "db" not in networkDictionary[networkName]:
            networkDictionary[networkName]["db"] = {}

        try:
            networkDictionary[networkName]["db"]["networkId"] = networkRow["network_id"]
        except (KeyError, TypeError) as e:
            logger.warning(f"Could not retrieve network_id for {networkName}: {e}")
            continue

    # Return the network dictionary
    return networkDictionary


@retry(attempts=retryAttempts, delay=retryDelay)
async def gatherNetworkDexs(dbConnection, networkName: str, networkDetails: Dict[str, Any], browser: BrowserContext) -> Dict[str, List[Dict[str, Any]]]:
    """
    Gather all decentralized exchanges (DEXs) for a specific network.
    
    Opens a new browser page, navigates to the network's Dexscreener page,
    and collects all available DEXs by parsing the tab elements at the top
    of the page.
    
    Args:
        dbConnection: Active database connection for storing DEX data.
        networkName: Name of the blockchain network (e.g., 'ethereum', 'bsc').
        networkDetails: Dictionary containing network URL and database ID.
        browser: Playwright browser context for page creation.
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with network name as key
            and list of DEX details as value. Returns empty dict if no DEXs found.
            
    Example:
        {'ethereum': [{'name': 'uniswap', 'url': '...', 'db': {...}}, ...]}
    """
    # Create a new page
    page = await newPage(browser=browser)

    # Go to the networks url
    await page.goto(networkDetails["url"])

    # Init dexscreener
    await validateDexscreenerInit(
        page=page
    )

    # Gather the list of dexs for the tabs at the top of the screen
    networksDexs = await gatherDexListFromTabs(
        dbConnection=dbConnection,
        networkDetails=networkDetails,
        page=page
    )

    if not networksDexs:
        return {}

    # Count dexs
    amountOfDexs = len(networksDexs)

    # Close our page as don't need it anymore
    await page.close()

    # Create an object with the network and its dexs
    networkDetails = {
        networkName: networksDexs
    }

    # Log out how many dexs we got for this network
    logger.info(f"{networkName.title()}: {amountOfDexs}")

    # Return the network details object
    return networkDetails


@retry(attempts=retryAttempts, delay=retryDelay)
async def gatherDexListFromTabs(dbConnection, networkDetails: Dict[str, Any], page) -> List[Dict[str, Any]]:
    """
    Gather the list of DEXs from the tab navigation at the top of a network page.
    
    Parses the horizontal tab navigation on Dexscreener to extract all available
    DEX names for the current network. Each DEX is stored in the database if
    not already present, and a dictionary with DEX details is created.
    
    Args:
        dbConnection: Active database connection for storing and querying DEX data.
        networkDetails: Dictionary containing the network's database ID.
        page: Playwright page object currently on the network's Dexscreener page.
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries, each containing:
            - name: Lowercase DEX name without spaces
            - url: Full URL to the DEX page on Dexscreener
            - db: Dictionary with networkId and dexId from database
            
    Note:
        Returns empty dict if the DEX tabs element cannot be found.
    """
    try:
        # Get the sidebar list element
        dexTabs = os.getenv(DS_DEX_TABS_ENV)
        dexTabElement = await findAndCheckElement(
            page=page,
            selector=dexTabs
        )
    except Exception:
        return {}

    # Get all the 'li' items
    dexTabItems = await getListItems(
        listElement=dexTabElement
    )

    # Get index of All DEXes tab - always first in dex list
    allDexsIndex = next((i for i, item in enumerate(dexTabItems) if item == ALL_DEXES_TAB), -1)

    # Filter list so we only have networks
    filteredList = dexTabItems[allDexsIndex + 1:]

    cleanDexList = [(network.lower()).replace(" ", "") for network in filteredList]

    # List of available dexs
    dexListDictionary = []

    # Base url
    baseUrl = page.url

    currentlyStoredDexs = getAllDexsForNetwork(
        dbConnection=dbConnection,
        networkDbId=networkDetails["db"]["networkId"]
    )

    uniqueCurrentlyStoredDexs = set(currentlyStoredDexs)
    dexsToStore = [x for x in cleanDexList if x not in uniqueCurrentlyStoredDexs]

    # Get the url for each dex in each network
    for dexName in cleanDexList:

        if dexName in dexsToStore:
            await addDexToDB(
                dbConnection=dbConnection,
                networkDbId=networkDetails["db"]["networkId"],
                dexName=dexName
            )

        dexRow = getRowByValue(
            dbConnection=dbConnection,
            table=DEXS_TABLE,
            conditions=[
                {
                    "name": dexName
                }
            ]
        )

        dexObject = {
            "name": dexName,
            "url": f"{baseUrl}/{dexName}",
            "db": {
                "networkId": dexRow["network_id"],
                "dexId": dexRow["dex_id"],
            }
        }

        dexListDictionary.append(dexObject)

    # Return the dex dictionary
    return dexListDictionary


@retry(attempts=retryAttempts, delay=retryDelay)
async def gatherPairsForDex(dbConnection, networkName: str, dexDetails: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gather token pairs for a specific DEX sorted by liquidity.
    
    This is the main scraping function that collects token pair data from
    Dexscreener. It navigates through paginated results, extracts pair
    information, and stores tokens and pairs in the database.
    
    Args:
        dbConnection: Active database connection for storing token and pair data.
        networkName: Name of the blockchain network (e.g., 'ethereum').
        dexDetails: Dictionary containing DEX name, URL, and database IDs.
        
    Returns:
        List[Dict[str, Any]]: List of token pair dictionaries, each containing:
            - rank: Liquidity ranking of the pair
            - market: Volume, liquidity, and FDV data
            - network: Network name and transaction count
            - dex: DEX name and optional Uniswap version
            - primaryToken: Token name, symbol, and database ID
            - secondaryToken: Token symbol and database ID
            - pair: Pair name and contract address
            
    Note:
        The number of pairs collected is controlled by the AMOUNT_OF_PAIRS_TO_COLLECT
        environment variable. Results are sorted by liquidity in descending order.
    """
    # Get the current dexs name and url
    dexName = dexDetails["name"]
    dexURL = dexDetails["url"]

    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    # Check if we want to start our browser in headless
    runHeadless = checkHeadless()

    # Create async instance of playwright
    async with async_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = await playwright.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": BROWSER_VIEWPORT_WIDTH,
                "height": BROWSER_VIEWPORT_HEIGHT
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = await newPage(browser=browser)

        # Navigate to the dexs url
        await page.goto(dexURL)

        # Sort the tokens by liquidity
        await page.locator('text=Liquidity').first.click()

        # Get total amount of pairs
        pairCountElement = page.locator("span", has_text="Showing pairs")
        pairCountText = await pairCountElement.all_inner_texts()

        # Amount of pairs to get
        pairsToCollect = int(os.getenv(PAIRS_TO_COLLECT_ENV))

        if pairCountText:

            pairCount = int(pairCountText[0].split(" ")[-1].replace(",", ""))
            roundCount = replaceTrailingDigitsWithZeros(number=pairCount)

            if pairCount <= PAIRS_PER_PAGE:
                pairsPagesToIterate = 1
            elif pairCount >= pairsToCollect:
                pairsPagesToIterate = int(pairsToCollect / PAIRS_PER_PAGE)
            else:
                pairsPagesToIterate = int((roundCount / PAIRS_PER_PAGE) + 1)

        else:

            pairsPagesToIterate = 1

        # List which will store our token objects
        collectedTokens = []

        for pageNumber in range(pairsPagesToIterate + 1):

            if pageNumber > 1:
                # Navigate to the next pair page
                nextPageURL = f"{dexURL}/page-{pageNumber}"
                await page.goto(nextPageURL)

                await page.locator('text=Liquidity').first.click()

            # Get the sidebar list element
            dexTable = os.getenv(DS_DEX_TABLE_ENV)
            dexTableElement = await findAndCheckElement(
                page=page,
                selector=dexTable
            )

            # Get all the 'li' items
            dexTabItems = await getAItems(
                listElement=dexTableElement
            )

            # Get the pair address for each token in the list
            pairAddresses = await getAllRowsMetadata(
                page=page,
                networkName=networkName
            )

            # Filter the inner text we got back by only items which start with #
            rows = [i for i in dexTabItems if i.startswith('#')]

            # Split them by the \n character
            rowsSplit = [l.split("\n") for l in rows]

            # Remove "#" "$" "%" or "/"
            cleanRows = [removeIllegalCharactersFromElements(item) for item in rowsSplit]

            # Remove any blank lines
            finalRows = [list(filter(None, item)) for item in cleanRows]

            # Iterate through the list of raw tokens we collected
            for row in finalRows:

                # Check if the row has info on its uniswap version
                hasUniswapBadge = row[1] in UNISWAP_VERSIONS
                uniswapVersion = NULL_VALUE

                # If it does, remove it - we can add it back later if it exists
                if hasUniswapBadge:
                    uniswapVersion = row.pop(1)

                # Fix some rows coming back with missing data
                # Sometimes data is missing so we just fill the list with blanks
                # or cut it short
                rowLength = len(row)
                if rowLength != EXPECTED_ROW_SIZE:
                    if rowLength > EXPECTED_ROW_SIZE:
                        row = row[0:EXPECTED_ROW_SIZE]
                    else:
                        slotsToFill = abs(EXPECTED_ROW_SIZE - len(row))
                        for _ in range(slotsToFill):
                            row.append(NULL_VALUE)

                tokenRank = smartEval(row[0])

                # Get the token rank
                if pageNumber <= 1:
                    tokenIndex = smartEval(row[0])
                else:
                    tokenIndex = (tokenRank - ((pageNumber - 1) * PAIRS_PER_PAGE))

                # Get the pair address for this row
                pairAddress = pairAddresses[tokenIndex - 1]

                # Create a token object from all the properties we scraped
                tokenDetails = {
                    "rank": tokenRank,
                    "market": {
                        "volume": smartEval(replaceNumberShorthands(row[6])),
                        "liquidity": smartEval(replaceNumberShorthands(row[11])),
                        "fdv": smartEval(replaceNumberShorthands(row[12]))
                    },
                    "network": {
                        "network": networkName,
                        "txCount": smartEval(row[5]),
                    },
                    "dex": {
                        "dex": dexName,
                    },
                    "primaryToken": {
                        "name": row[3],
                        "symbol": row[1]
                    },
                    "secondaryToken": {
                        "symbol": row[2],
                    },
                    "pair": {
                        "name": f"{row[1]}/{row[2]}",
                        "address": pairAddress
                    }
                }

                # Check if primary token already exists
                primaryTokenDetails = getRowByValue(
                    dbConnection=dbConnection,
                    table=TOKENS_TABLE,
                    conditions=[
                        {
                            "symbol": tokenDetails["primaryToken"]["symbol"]
                        }
                    ]
                )

                # If it doesn't - add it
                if not primaryTokenDetails:
                    # Add primary token to database
                    primaryTokenDbId = await addTokenToDB(
                        dbConnection=dbConnection,
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenName=tokenDetails["primaryToken"]["name"],
                        tokenSymbol=tokenDetails["primaryToken"]["symbol"]
                    )
                else:
                    primaryTokenDbId = primaryTokenDetails["token_id"]

                tokenDetails["primaryToken"]["db"] = {}
                tokenDetails["primaryToken"]["db"]["dbId"] = primaryTokenDbId

                # Check if primary token already exists
                secondaryTokenDetails = getRowByValue(
                    dbConnection=dbConnection,
                    table=TOKENS_TABLE,
                    conditions=[
                        {
                            "symbol": tokenDetails["secondaryToken"]["symbol"]
                        }
                    ]
                )

                if not secondaryTokenDetails:
                    # Add secondary token to database
                    secondaryTokenDbId = await addTokenToDB(
                        dbConnection=dbConnection,
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenName=None,
                        tokenSymbol=tokenDetails["secondaryToken"]["symbol"]
                    )
                else:
                    secondaryTokenDbId = secondaryTokenDetails["token_id"]

                tokenDetails["secondaryToken"]["db"] = {}
                tokenDetails["secondaryToken"]["db"]["dbId"] = secondaryTokenDbId

                await addTokenPairToDB(
                    dbConnection=dbConnection,
                    networkDbId=dexDetails["db"]["networkId"],
                    dexDbId=dexDetails["db"]["dexId"],
                    primaryTokenDbId=primaryTokenDbId,
                    secondaryTokenDbId=secondaryTokenDbId,
                    pairName=tokenDetails["pair"]["name"],
                    pairAddress=tokenDetails["pair"]["address"],
                    pairRanking=tokenRank,
                    pairLiquidity=tokenDetails["market"]["liquidity"],
                    pairVolume=tokenDetails["market"]["volume"],
                    pairFdv=tokenDetails["market"]["fdv"]
                )

                # Add the uniswap version back in if we have it
                if hasUniswapBadge:
                    tokenDetails["dex"]["uniswapVersion"] = uniswapVersion

                # Finally, append the token to the final list
                collectedTokens.append(tokenDetails)

        # Close the page and browser as we are done
        await page.close()
        await browser.close()

        # Count how many tokens we collected and log it
        amountOfTokens = len(collectedTokens)
        logger.info(f"- {dexName.title()}: {amountOfTokens}")

        # Return our collected tokens
        return collectedTokens


@retry(attempts=retryAttempts, delay=retryDelay)
async def gatherMetadataForPair(baseLink: str, tokenRow: Dict[str, Any], amountOfTokensToUpdate: int, dbConnection) -> None:
    """
    Gather and store the contract address for a token pair.
    
    Navigates to the pair's detail page on Dexscreener, extracts the primary
    token's contract address from the block explorer link, and updates the
    token record in the database.
    
    Args:
        baseLink: Base URL for the Dexscreener pair pages (e.g., 'https://dexscreener.com/ethereum').
        tokenRow: Dictionary containing pair and token information including:
            - pair.address: The pair's contract address for URL construction
            - uploadIndex: Current position in the update queue
            - primaryToken.db.dbId: Database ID of the primary token
            - primaryToken.symbol: Token symbol for logging
        amountOfTokensToUpdate: Total number of tokens being updated (for progress logging).
        dbConnection: Active database connection for updating token data.
        
    Returns:
        None: Updates the database directly, no return value.
        
    Note:
        This function logs progress in the format [current/total] SYMBOL [address]
        to track the metadata gathering process.
    """
    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    # Check if we want to start our browser in headless
    runHeadless = checkHeadless()

    # Create async instance of playwright
    async with async_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = await playwright.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": BROWSER_VIEWPORT_WIDTH,
                "height": BROWSER_VIEWPORT_HEIGHT
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = await newPage(browser=browser)

        # Get row data
        pairAddress = tokenRow["pair"]["address"]

        uploadIndex = tokenRow["uploadIndex"]
        primaryTokenDbId = tokenRow["primaryToken"]["db"]["dbId"]
        primaryTokenDbSymbol = tokenRow["primaryToken"]["symbol"]

        logger.info(f"[{uploadIndex}/{amountOfTokensToUpdate}] {primaryTokenDbSymbol} [{pairAddress}]")

        # Calculate our pair address
        pairUrl = f"{baseLink}/{pairAddress}"

        # Go the pair graph page
        await page.goto(pairUrl)

        # Get all elements with the external link label
        allBlockExplorerLinks = page.locator(selector=EXTERNAL_LINK_SELECTOR)

        # Get the second element on the page which is the address of the primary token
        tokenExplorerLink = await allBlockExplorerLinks.nth(1).get_attribute("href")
        primaryTokenAddress = tokenExplorerLink.split("/")[-1]

        # Update Token Address In DB
        updateTokenByDbId(
            dbConnection=dbConnection,
            tokenDbId=primaryTokenDbId,
            fieldToUpdate="address",
            fieldNewValue=primaryTokenAddress
        )
