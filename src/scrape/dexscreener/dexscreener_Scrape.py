import os
from pathlib import Path

import nest_asyncio
from faker import Faker
from playwright.async_api import BrowserContext, async_playwright
from playwright.sync_api import sync_playwright

from src.chain.decode.decode_Tx import decodeTx
from src.db.actions.actions_Dexs import addDexToDB
from src.db.actions.actions_Pairs import addTokenPairToDB
from src.db.actions.actions_Routes import addRouteToDB
from src.db.actions.actions_Setup import initDBConnection
from src.db.actions.actions_Tokens import updateTokenByDbId, addTokenToDB

from src.db.actions.actions_Networks import addNetworkToDB
from src.db.querys.querys_Dexs import getAllDexsForNetwork
from src.db.querys.querys_General import getRowByValue
from src.db.querys.querys_Networks import getAllNetworks
from src.playwright.playwright_Hacks import safePageLoad, safeClick
from src.playwright.playwright_Utils import findAndCheckElement, newPage, getListItems, getAItems
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Utils import removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands, getAllRowsMetadata
from src.utils.data.data_Booleans import strToBool
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros

nest_asyncio.apply()

logger = getProjectLogger()

# Gather all the available networks from the Dexscreener sidebar
def gatherNetworkList(dbConnection, page):
    # Get the sidebar list element
    dsNetworkList = os.getenv('DS_LIST')
    networkList = findAndCheckElement(
        page=page,
        selector=dsNetworkList
    )

    # Get all the 'li' items
    allLists = networkList.locator(selector='li')
    sidebarListItems = allLists.all_text_contents()

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
def gatherNetworkDexs(args):

    # Init MySQL DB
    dbConnection = initDBConnection()
    networkName = args["networkName"]
    networkDetails = args["networkDetails"]

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

        # Create a new page
        page = newPage(browser=browser)

        # Load URL
        safePageLoad(
            page=page,
            url=networkDetails["url"]
        )

        # Init dexscreener
        validateDexscreenerInit(
            page=page
        )

        # Gather the list of dexs for the tabs at the top of the screen
        networksDexs = gatherDexListFromTabs(
            dbConnection=dbConnection,
            networkDetails=networkDetails,
            page=page
        )

        browser.close()

        if not networksDexs:
            return {}

        # Count dexs
        amountOfDexs = len(networksDexs)

        # Close our page as don't need it anymore
        page.close()

        # Create an object with the network and its dexs
        networkDetails = {
            networkName: networksDexs
        }

        # Log out hwo many dexs we got for this network
        logger.info(f"{networkName.title()}: {amountOfDexs}")

        dbConnection.close()

        # Return the network details object
        return networksDexs


def gatherDexListFromTabs(dbConnection, networkDetails, page):

    try:
        # Get the sidebar list element
        dexTabs = os.getenv('DS_DEX_TABS')
        dexTabElement = findAndCheckElement(
            page=page,
            selector=dexTabs
        )
    except:
        return {}

    # Get all the 'li' items
    dexTabItems = getListItems(
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
            addDexToDB(
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
def gatherPairsForDex(dbConnection, networkName, dexDetails):

    # Get the current dexs name and url
    dexName = dexDetails["name"]
    dexURL = dexDetails["url"]

    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    # Check if we want to start our browser in headless
    runHeadless = checkHeadless()

    # Create async instance of playwright
    with sync_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = playwright.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = newPage(browser=browser)

        # Navigate to the dexs url
        safePageLoad(
            page=page,
            url=dexURL
        )

        safeClick(
            page=page,
            selector='text=Liquidity'
        )

        # Get total amount of pairs

        pairCountElement = page.locator("span", has_text="Showing pairs")
        pairCountText = pairCountElement.all_inner_texts()

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

        lazyMode = strToBool(os.getenv("LAZY_MODE"))
        if lazyMode:
            pairsPagesToIterate = 1

        loopRange = pairsPagesToIterate + 1

        for pageNumber in range(1, loopRange):

            if pageNumber > 1:
                # Navigate to the next pair page
                nextPageURL = f"{dexURL}/page-{pageNumber}"

                safePageLoad(
                    page=page,
                    url=nextPageURL
                )

                safeClick(
                    page=page,
                    selector='text=Liquidity'
                )

            # Get the sidebar list element
            dexTable = os.getenv('DS_DEX_TABLE')
            dexTableElement = findAndCheckElement(
                page=page,
                selector=dexTable
            )

            # Get all the 'li' items
            dexTabItems = getAItems(
                page=page,
                listElement=dexTableElement
            )

            # Get the pair address for each token in the list
            pairAddresses = getAllRowsMetadata(
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

            # List for keeping track of added ranks
            addedRanks = []

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

                try:

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
                        primaryTokenDbId = addTokenToDB(
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
                        secondaryTokenDbId = addTokenToDB(
                            dbConnection=dbConnection,
                            networkDbId=dexDetails["db"]["networkId"],
                            tokenName=None,
                            tokenSymbol=tokenDetails["secondaryToken"]["symbol"]
                        )
                    else:
                        secondaryTokenDbId = secondaryTokenDetails["token_id"]

                    tokenDetails["network"]["db"] = {}
                    tokenDetails["network"]["db"]["dbId"] = dexDetails["db"]["networkId"]

                    tokenDetails["dex"]["db"] = {}
                    tokenDetails["dex"]["db"]["dbId"] = dexDetails["db"]["dexId"]

                    tokenDetails["secondaryToken"]["db"] = {}
                    tokenDetails["secondaryToken"]["db"]["dbId"] = secondaryTokenDbId

                    if tokenRank not in addedRanks:

                        addedRanks.append(tokenRank)

                        addTokenPairToDB(
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

                    else:

                        logger.info(f"Already added pair ranked {tokenRank} - skipping")

                except:

                    continue

        # Close the page and browser as we are done
        page.close()
        browser.close()

        # Count how many tokens we collected and log it
        amountOfTokens = len(collectedTokens)
        logger.info(f"- {dexName.title()}: {amountOfTokens}")

        # Return our collected tokens
        return collectedTokens

# @retry(attempts=retryAttempts, delay=retryDelay)
def gatherMetadataForPair(baseLink, tokenRow, rpcUrl, routerAddress, routerAbi, amountOfTokensToUpdate,
                      dbConnection):

    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    # Check if we want to start our browser in headless
    runHeadless = checkHeadless()

    # Create async instance of playwright
    with sync_playwright() as playwright:

        # Setup browser
        browser: BrowserContext = playwright.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        # Open a new tab
        page = newPage(browser=browser)

        # Get row data
        pairAddress = tokenRow["pair"]["address"]

        uploadIndex = tokenRow["uploadIndex"]
        primaryTokenDbId = tokenRow["primaryToken"]["db"]["dbId"]
        primaryTokenDbSymbol = tokenRow["primaryToken"]["symbol"]

        logger.info(f"[{uploadIndex}/{amountOfTokensToUpdate}] {primaryTokenDbSymbol} [{pairAddress}]")

        # Calculate our pair address
        pairUrl = f"{baseLink}/{pairAddress}"

        # Go the pair graph page
        safePageLoad(
            page=page,
            url=pairUrl
        )

        # Get all elements with the external link label
        allBlockExplorerLinks = page.locator(selector="[aria-label='External Link']")

        # Get the second element on the page which is the address of the primary token
        tokenExplorerLink = allBlockExplorerLinks.nth(1).get_attribute("href")
        primaryTokenAddress = tokenExplorerLink.split("/")[-1]

        # Update Token Address In DB
        updateTokenByDbId(
            dbConnection=dbConnection,
            tokenDbId=primaryTokenDbId,
            fieldToUpdate="address",
            fieldNewValue=primaryTokenAddress
        )

        # Get Pair Routes
        collectedLinks = []
        while len(collectedLinks) < 100:
            txTab = page.locator("text=TXN")
            txTab.first.hover()
            linksOnPage = page.eval_on_selector_all("a[href^='https']",
                                                    "elements => elements.map(element => element.href)")
            txsOnPage = [link for link in linksOnPage if "0x" in link]
            collectedLinks.extend(txsOnPage)
            page.mouse.wheel(0, 700)
            collectedLinks = list(set(collectedLinks))
            collectedLinks = ["0x" + address for address in list(map(lambda x: x.split('0x')[1], collectedLinks))]

        validTransactions = [x for x in collectedLinks if len(x) == 66]

        logger.info(f"- Decoding {len(validTransactions)} Route Transactions...")

        len(validTransactions)

        # Create the dict of decode tasks
        decodedTransactions = [
            decodeTx(contractAddress=routerAddress, rpcUrl=rpcUrl, transactionHash=transaction, abi=routerAbi) for
            transaction in validTransactions]

        successfullyDecodedTransactions = [decodedTransaction for decodedTransaction in decodedTransactions if
                                           decodedTransaction]

        logger.info(f"- Decoded {len(successfullyDecodedTransactions)} Route Transactions!")

        # Filter out the invalid results
        finalDecodedTransactions = [decodedTransaction for decodedTransaction in decodedTransactions if
                                    isinstance(decodedTransaction, dict) and "path" in decodedTransaction["params"]]

        collectedRoutes = {}

        logger.info(f"- Uploading {len(successfullyDecodedTransactions)} Route Transactions...")

        for finalDecodedTransaction in finalDecodedTransactions:

            routeUsed = finalDecodedTransaction["params"]["path"]

            tokenInAddress = routeUsed[0]
            tokenOutAddress = routeUsed[-1]

            routeName = f"{tokenInAddress}-{tokenOutAddress}"

            isLoopRoute = tokenInAddress == tokenOutAddress

            if not isLoopRoute:

                if routeName not in collectedRoutes:
                    collectedRoutes[routeName] = []

                routeObject = {
                    "method": finalDecodedTransaction["name"],
                    "route": "-".join(routeUsed),
                    "blockNumber": finalDecodedTransaction["blockNumber"]
                }

                if "amountIn" in finalDecodedTransaction["params"]:
                    routeObject["amountIn"] = finalDecodedTransaction["params"]["amountIn"]
                else:
                    routeObject["amountIn"] = None

                if "amountOutMin" in finalDecodedTransaction["params"]:
                    routeObject["amountOutMin"] = finalDecodedTransaction["params"]["amountOutMin"]
                else:
                    routeObject["amountOutMin"] = None

                if routeObject not in collectedRoutes[routeName]:
                    collectedRoutes[routeName].append(routeObject)

                addRouteToDB(
                    dbConnection=dbConnection,
                    networkDbId=tokenRow["network"]["db"]["dbId"],
                    dexDbId=tokenRow["dex"]["db"]["dbId"],
                    tokenInAddress=tokenInAddress,
                    tokenOutAddress=tokenOutAddress,
                    route=routeObject["route"],
                    method=routeObject["method"],
                    transactionHash=finalDecodedTransaction["txHash"],
                    txTimestamp=finalDecodedTransaction["timestamp"],
                    blockNumber=finalDecodedTransaction["blockNumber"],
                    amountIn=routeObject["amountIn"],
                    amountOut=routeObject["amountOutMin"]
                )

        logger.info(f"- Uploaded {len(successfullyDecodedTransactions)} Route Transactions!")
