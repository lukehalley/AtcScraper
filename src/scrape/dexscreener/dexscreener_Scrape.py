import os

from playwright.async_api import BrowserContext

from src.playwright.playwright_Utils import findAndCheckElement, getListItems
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot


async def getNetworkList(page):

    # Get The Sidebar List Element
    dsNetworkList = os.getenv('DS_LIST')
    networkList = await findAndCheckElement(
        page=page,
        selector=dsNetworkList
    )

    allLists = networkList.locator(selector='li')
    sidebarListItems = await allLists.all_text_contents()

    # Get Index Of Ethereum - Always The First
    ethereumIndex = next((i for i, item in enumerate(sidebarListItems) if item == 'Ethereum'), -1)

    # Filter List So We Only Have Networks
    filteredList = sidebarListItems[ethereumIndex:]

    filteredList = filteredList[0:5]

    # Dict To Hold Network Info
    networkDictionary = {}

    # Base URL
    baseUrl = getDexscreenerRoot()

    for network in filteredList:
        networkName = (network.lower()).replace(" ", "")
        networkDictionary[networkName] = {
            "url": f"{baseUrl}/{networkName}"
        }

    return networkDictionary


async def getDexListFromTabs(page):

    # Get The Sidebar List Element
    dexTabs = os.getenv('DS_DEX_TABS')
    dexTabElement = await findAndCheckElement(
        page=page,
        selector=dexTabs
    )

    # Get All The 'li' Items
    dexTabItems = await getListItems(
        listElement=dexTabElement
    )

    # Get Index Of Ethereum - Always The First
    allDexsIndex = next((i for i, item in enumerate(dexTabItems) if item == 'All DEXes'), -1)

    # Filter List So We Only Have Networks
    filteredList = dexTabItems[allDexsIndex + 1:]

    # List Of Available Dexs
    dexs = []

    # Base URL
    baseUrl = page.url

    for dex in filteredList:
        dexName = (dex.lower()).replace(" ", "")
        dexObject = {
            "name": dexName,
            "url": f"{baseUrl}/{dexName}"
        }
        dexs.append(dexObject)

    return dexs


async def getTokensForDex(dexDetails, browser: BrowserContext):

    dexName = dexDetails["name"]
    dexURL = dexDetails["url"]

    page = await browser.new_page()
    print(dexName)
    await page.goto(dexURL)

    # await waitForElementToGoAway(
    #     page=page,
    #     selector=os.getenv("DS_LOADER")
    # )

    await page.locator('text=Liquidity').click()

    x = 1

    # tokenResults = {}
    #
    # # First selector is '#menu-list-18-menuitem-13' - so iterate up to 16 to get the four buttons
    # allTimeframes = {
    #     "5M": 13,
    #     "1H": 14,
    #     "6H": 15,
    #     "24H": 16,
    # }
    #
    # validateDexscreenerInit(driver=driver)
    #
    # txCountElement = waitAndGetElement(
    #     driver=driver,
    #     selector=os.getenv("DS_TX_COUNT")
    # )
    #
    # txCount = int(txCountElement.text.replace(",", ""))
    # txFloor = int(os.getenv("DS_TX_COUNT_FLOOR"))
    #
    # if txCount > txFloor:
    #
    #     # Sort By Liquidity
    #     waitAndClickText(
    #         driver=driver,
    #         text="Liquidity"
    #     )
    #
    #     activeTimeframes = os.getenv("DS_TIMEFRAMES").split(",")
    #
    #     for timeframeName, timeframeIndex in allTimeframes.items():
    #
    #         if timeframeName in activeTimeframes:
    #
    #             timeframeResults = []
    #
    #             openTimespan(
    #                 driver=driver,
    #                 timeToSelect=timeframeName
    #             )
    #
    #             # Get All The Rows
    #             dexTableElement, dexTableRows = getDexTableRows(driver=driver)
    #
    #             bigList = dexTableElement.get_attribute("innerText").splitlines()
    #             splitList = [l.split(',') for l in ','.join(bigList).split('#')][1:]
    #             row = [removeIllegalCharactersFromElements(item) for item in splitList]
    #             finalRows = [list(filter(None, item)) for item in row]
    #
    #             for row in finalRows:
    #
    #                 index = finalRows.index(row)
    #
    #                 dexTableElement, dexTableRows = getDexTableRows(driver=driver)
    #
    #                 if index >= len(dexTableRows):
    #                     index = -1
    #
    #                 pairAddress = dexTableRows[index].get_attribute("href").split("/")[-1]
    #
    #                 dexTableElement, dexTableRows = getDexTableRows(driver=driver)
    #
    #                 hasUniswapBadge = len(getChildItemsByClass(
    #                     parentElement=dexTableRows[index],
    #                     className=os.getenv("DS_DEX_UNISWAP_BADGE_CLASS")
    #                 )) > 0
    #
    #                 uniswapVersion = "N/A"
    #                 if hasUniswapBadge:
    #                     uniswapVersion = row.pop(1)
    #
    #                 tokenDetails = {
    #                     "rank": smartEval(row[0]),
    #                     "market": {
    #                         "volume": replaceNumberShorthands(row[6]),
    #                         "liquidity": replaceNumberShorthands(row[11]),
    #                         "fdv": replaceNumberShorthands(row[12])
    #                     },
    #                     "network": {
    #                         "network": networkName,
    #                         "txCount": smartEval(row[5]),
    #                     },
    #                     "dex": {
    #                         "dex": dexName,
    #                     },
    #                     "token": {
    #                         "name": row[3],
    #                         "primaryToken": row[1],
    #                         "secondaryToken": row[2],
    #                         "tokenPair": f"{row[1]}/{row[2]}",
    #                         "pairAddress": f"{pairAddress}"
    #                     },
    #                     "price": {
    #                         "currentPrice": smartEval(row[4]),
    #                         "priceChange": {
    #                             "5M": smartEval(row[7]),
    #                             "1H": smartEval(row[8]),
    #                             "6H": smartEval(row[9]),
    #                             "24M": smartEval(row[10])
    #                         },
    #                     }
    #                 }
    #
    #                 if hasUniswapBadge:
    #                     tokenDetails["dex"]["uniswapVersion"] = uniswapVersion
    #
    #                 timeframeResults.append(tokenDetails)
    #
    #             tokenResults[timeframeName] = timeframeResults
    #
    #         else:
    #
    #             x = 1
    #
    # return tokenResults
