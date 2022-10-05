import os
import time
from pathlib import Path

import nest_asyncio
from faker import Faker
from playwright.async_api import BrowserContext, async_playwright
from retrying_async import retry

from src.db.actions.actions_Dexs import addDexToDB
from src.db.actions.actions_Pairs import addTokenPairToDB
from src.db.actions.actions_Tokens import updateTokenByDbId, addTokenToDB

from src.db.actions.actions_Networks import addNetworkToDB
from src.db.querys.querys_Dexs import getAllDexsForNetwork
from src.db.querys.querys_General import getRowByValue
from src.db.querys.querys_Networks import getAllNetworks
from src.playwright.playwright_Hacks import safeClick, safePageLoad
from src.playwright.playwright_Utils import findAndCheckElement, getListItems, getAItems, newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Utils import removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands, getAllRowsMetadata
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros
from src.utils.retry.retry_Settings import getRetryParameters

nest_asyncio.apply()

logger = getProjectLogger()
# retryAttempts, retryDelay = getRetryParameters()

# Gather all the available networks from the Dexscreener sidebar
# @retry(attempts=retryAttempts, delay=retryDelay)
async def gatherNetworkList(dbConnection, page):

    # Get the sidebar list element
    dsNetworkList = os.getenv('DS_LIST')
    networkList = await findAndCheckElement(
        page=page,
        selector=dsNetworkList
    )

    # Get all the 'li' items
    allLists = networkList.locator(selector='li')
    sidebarListItems = await allLists.all_text_contents()

    # Get index of ethereum - always the first
    ethereumIndex = next((i for i, item in enumerate(sidebarListItems) if item == 'Ethereum'), -1)

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
            table="networks",
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
        except:
            x = 1

    # Return the network dictionary
    return networkDictionary

# Gather all dexs for each network
# @retry(attempts=retryAttempts, delay=retryDelay)
async def gatherNetworkDexs(dbConnection, networkName, networkDetails, browser):

    # Create a new page
    page = await newPage(browser=browser)

    # Go to the networks url
    await safePageLoad(
        page=page,
        url=networkDetails["url"]
    )

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

    # Log out hwo many dexs we got for this network
    logger.info(f"{networkName.title()}: {amountOfDexs}")

    # Return the network details object
    return networkDetails

# Gather the list of dexs from the top of each network page of dexscreener
# @retry(attempts=retryAttempts, delay=retryDelay)
async def gatherDexListFromTabs(dbConnection, networkDetails, page):

    try:
        # Get the sidebar list element
        dexTabs = os.getenv('DS_DEX_TABS')
        dexTabElement = await findAndCheckElement(
            page=page,
            selector=dexTabs
        )
    except:
        return {}

    # Get all the 'li' items
    dexTabItems = await getListItems(
        page=page,
        listElement=dexTabElement
    )

    # Get index of ethereum - always the first
    allDexsIndex = next((i for i, item in enumerate(dexTabItems) if item == 'All DEXes'), -1)

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
            table="dexs",
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

# For a dex - get the top 100 tokens by liquidity
# @retry(attempts=retryAttempts, delay=retryDelay)
async def gatherPairsForDex(dbConnection, networkName, dexDetails):

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
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = await newPage(browser=browser)

        # Navigate to the dexs url
        await safePageLoad(
            page=page,
            url=dexURL
        )

        await safeClick(
            page=page,
            selector='text=Liquidity'
        )

        # Get total amount of pairs
        pairCountElement = page.locator("span", has_text="Showing pairs")
        pairCountText = await pairCountElement.all_inner_texts()

        # Amount of pairs to get
        pairsToCollect = int(os.getenv("AMOUNT_OF_PAIRS_TO_COLLECT"))

        if pairCountText:

            pairCount = int(pairCountText[0].split(" ")[-1].replace(",", ""))
            roundCount = replaceTrailingDigitsWithZeros(number=pairCount)

            if pairCount <= 100:
                pairsPagesToIterate = 1
            elif pairCount >= pairsToCollect:
                pairsPagesToIterate = int(pairsToCollect / 100)
            else:
                pairsPagesToIterate = int((roundCount / 100) + 1)

        else:

            pairsPagesToIterate = 1

        # List which will store our token objects
        collectedTokens = []

        for pageNumber in range(pairsPagesToIterate + 1):

            if pageNumber > 1:
                # Navigate to the next pair page
                nextPageURL = f"{dexURL}/page-{pageNumber}"

                await safePageLoad(
                    page=page,
                    url=nextPageURL
                )

                await safeClick(
                    page=page,
                    selector='text=Liquidity'
                )

            # Get the sidebar list element
            dexTable = os.getenv('DS_DEX_TABLE')
            dexTableElement = await findAndCheckElement(
                page=page,
                selector=dexTable
            )

            # Get all the 'li' items
            dexTabItems = await getAItems(
                page=page,
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
                hasUniswapBadge = row[1] == "V1" or row[1] == "V2" or row[1] == "V3"
                uniswapVersion = "NULL"

                # If it does, remove it - we can add it back later if it exists
                if hasUniswapBadge:
                    uniswapVersion = row.pop(1)

                # Fix some rows coming back with missing data
                # Sometimes data is missing so we just fill the list with blanks
                # or cut it short
                expectedListSize = 13
                rowLength = len(row)
                if rowLength != 13:
                    if rowLength > expectedListSize:
                        row = row[0:13]
                    else:
                        slotsToFill = abs(13 - len(row))
                        for _ in range(slotsToFill):
                            row.append("NULL")

                tokenRank = smartEval(row[0])

                # Get the token rank
                if pageNumber <= 1:
                    tokenIndex = smartEval(row[0])
                else:
                    tokenIndex = (tokenRank - ((pageNumber - 1) * 100))

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
                    table="tokens",
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
                    table="tokens",
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

# @retry(attempts=retryAttempts, delay=retryDelay)
async def gatherMetadataForPair(baseLink, tokenRow, amountOfTokensToUpdate, dbConnection):

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
                "width": 1920,
                "height": 1080
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
        await safePageLoad(
            page=page,
            url=pairUrl
        )

        # Get all elements with the external link label
        allBlockExplorerLinks = page.locator(selector="[aria-label='External Link']")

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