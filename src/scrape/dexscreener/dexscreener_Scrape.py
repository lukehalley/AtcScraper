import os
from pathlib import Path

from faker import Faker
from playwright.sync_api import BrowserContext
from playwright.sync_api import sync_playwright

from src.chain.decode.decode_Tx import decodeTx
from src.db.actions.actions_Dexs import addDexToDB
from src.db.actions.actions_Networks import addNetworkToDB
from src.db.actions.actions_Pairs import addTokenPairToDB
from src.db.actions.actions_Tokens import updateTokenByDbId, addTokenToDB
from src.db.db.querys.querys_Dexs import getDexRouterDetailsByDbId, getDexByNameAndNetworkId
from src.db.querys.querys_Dexs import getAllDexsForNetwork
from src.db.querys.querys_Networks import getAllNetworks, getNetworkRPCByDbId, getNetworkByName
from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId, getPairForNetworkIdAndPairDbId
from src.db.querys.querys_Tokens import getTokenByNetworkIdAndSymbol, \
    getTokenByNetworkIdAndTokenId
from src.playwright.playwright_Hacks import safePageLoad, safeClick
from src.playwright.playwright_Utils import findAndCheckElement, newPage, getListItems, getAItems
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Utils import removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands, getAllRowsMetadata
from src.utils.data.data_Booleans import strToBool
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger, printLog
from src.utils.math.math_Utils import replaceTrailingDigitsWithZeros

# Gather all the available networks from the Dexscreener sidebar
def gatherNetworkList(page):

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

    currentStoredNetworks = getAllNetworks()

    s = set(currentStoredNetworks)
    networksToStore = [x for x in cleanNetworkList if x not in s]

    # Get the urls to each network
    for networkName in cleanNetworkList:

        printLog(f"{networkName.title()} ✅")

        if networkName in networksToStore:
            addNetworkToDB(
                networkName=networkName
            )

        networkDictionary[networkName] = getNetworkByName(
            networkName=networkName
        )

        networkDictionary[networkName]["url"] = f"{baseUrl}/{networkName}"

    # Return the network dictionary
    return networkDictionary

# Gather all dexs for each network
def gatherNetworkDexs(args):

    networkName = args["networkName"]

    networkDetails = args["networkDetails"]
    networkDetails["name"] = networkName

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

        try:

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
                networkDetails=networkDetails,
                page=page
            )

            # Close our page as don't need it anymore
            page.close()

            # Close Browser
            browser.close()

            networksDexs = [network for network in networksDexs if network["db"]["networkId"] == args["networkDetails"]["network_id"]]

            if not networksDexs:
                return None
            else:
                # Create an object with the network and its dexs
                networkDetails = (networkName, networksDexs)

                printLog(
                    msg=f"{networkName.title()} ✅"
                )

                # Return the network details object
                return networkDetails

        except:

            try:
                page.close()
                browser.close()
            except:
                pass

            return None

# Gather The Networks Dexs
def gatherDexListFromTabs(networkDetails, page):

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
        networkDbId=networkDetails["network_id"]
    )

    uniqueCurrentlyStoredDexs = set(currentlyStoredDexs)
    dexsToStore = [x for x in cleanDexList if x not in uniqueCurrentlyStoredDexs]

    # Get the url for each dex in each network
    for dexName in cleanDexList:

        if dexName in dexsToStore:
            addDexToDB(
                networkDbId=networkDetails["network_id"],
                dexName=dexName
            )

        dexRow = getDexByNameAndNetworkId(
            dexName=dexName,
            networkId=networkDetails["network_id"]
        )

        if dexRow["factory"] and dexRow["factory_s3_path"] and dexRow["router"] and dexRow["router_s3_path"]:

            dexObject = {
                "name": dexName,
                "network": networkDetails["name"],
                "url": f"{baseUrl}/{dexName}",
                "db": {
                    "networkId": dexRow["network_id"],
                    "dexId": dexRow["dex_id"],
                },
                "abi": {
                    "factory": dexRow["factory"][0:42],
                    "factory_s3_path": dexRow["factory_s3_path"],
                    "router": dexRow["router"][0:42],
                    "router_s3_path": dexRow["router_s3_path"]
                }
            }

            dexListDictionary.append(dexObject)

    # Return the dex dictionary
    return dexListDictionary

# For a dex - get the top 100 tokens by liquidity
def gatherPairsForDex(dexDetails):

    networkName = dexDetails["network"]

    # Get Project Logger
    logger = getProjectLogger()

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
        collectedPairs = []

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

                # Get the pair address for this row
                pairAddress = pairAddresses[tokenIndex - 1]

                # Primary Token
                primaryTokenSymbol = row[1]

                # Secondary Token
                secondaryTokenSymbol = row[2]

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
                        "dex": dexDetails,
                    },
                    "primaryToken": {
                        "name": row[3],
                        "symbol": primaryTokenSymbol
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
                primaryTokenDetails = getTokenByNetworkIdAndSymbol(
                    networkDbId=dexDetails["db"]["networkId"],
                    tokenSymbol=primaryTokenSymbol
                )

                # If it doesn't - add it
                if not primaryTokenDetails:
                    # Add primary token to database
                    primaryTokenDbId = addTokenToDB(
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenName=tokenDetails["primaryToken"]["name"],
                        tokenSymbol=tokenDetails["primaryToken"]["symbol"]
                    )

                    primaryTokenDetails = getTokenByNetworkIdAndTokenId(
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenDbId=primaryTokenDbId
                    )
                else:
                    primaryTokenDbId = primaryTokenDetails["token_id"]

                tokenDetails["primaryToken"] = primaryTokenDetails

                # Check if secondary token already exists
                secondaryTokenDetails = getTokenByNetworkIdAndSymbol(
                    networkDbId=dexDetails["db"]["networkId"],
                    tokenSymbol=secondaryTokenSymbol
                )

                if not secondaryTokenDetails:
                    # Add secondary token to database
                    secondaryTokenDbId = addTokenToDB(
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenName=None,
                        tokenSymbol=tokenDetails["secondaryToken"]["symbol"]
                    )

                    secondaryTokenDetails = getTokenByNetworkIdAndTokenId(
                        networkDbId=dexDetails["db"]["networkId"],
                        tokenDbId=secondaryTokenDbId
                    )
                else:
                    secondaryTokenDbId = secondaryTokenDetails["token_id"]

                tokenDetails["primaryToken"] = primaryTokenDetails

                tokenDetails["network"]["db"] = {}
                tokenDetails["network"]["db"]["dbId"] = dexDetails["db"]["networkId"]

                tokenDetails["dex"]["db"] = {}
                tokenDetails["dex"]["db"]["dbId"] = dexDetails["db"]["dexId"]

                tokenDetails["secondaryToken"] = secondaryTokenDetails

                if tokenRank not in addedRanks:

                    addedRanks.append(tokenRank)

                    pairDbId = addTokenPairToDB(
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

                    if not pairDbId:
                        tokenDetails["pair"] = getPairForAddressAndNetworkId(
                            pairAddress=tokenDetails["pair"]["address"],
                            networkDbId=dexDetails["db"]["networkId"]
                        )
                    else:
                        tokenDetails["pair"] = getPairForNetworkIdAndPairDbId(
                            pairDbId=pairDbId,
                            networkDbId=dexDetails["db"]["networkId"]
                        )

                    # Add the uniswap version back in if we have it
                    if hasUniswapBadge:
                        tokenDetails["dex"]["uniswapVersion"] = uniswapVersion

                    # Finally, append the token to the final list
                    collectedPairs.append(tokenDetails)

        # Close the page and browser as we are done
        page.close()
        browser.close()

        # Count how many tokens we collected and log it
        printLog(f"{dexName.title()} On {networkName.title()} ✅")

        # Return our collected tokens
        return collectedPairs

        # try:
        #
        #
        #
        # except:
        #
        #     try:
        #         page.close()
        #         browser.close()
        #     except:
        #         pass
        #
        #     return None

