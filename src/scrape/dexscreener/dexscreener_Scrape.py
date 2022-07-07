import os
import time
from decimal import Decimal

from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot
from src.scrape.dexscreener.dexscreener_Utils import replaceNumberShorthands, \
    smartEval, removeIllegalCharactersFromElements
from src.selenium.selenium_Utils import getElementBySelector, getListItems, getCurrentURL, getTableItems, \
    getChildItemsByClass, getElementByValue


def getNetworkListFromSidebar(driver):
    # Get The Sidebar List Element
    sidebarElement = getElementBySelector(
        driver=driver,
        selector=os.getenv('DS_LIST')
    )

    # Get All The 'li' Items
    sidebarListItems = getListItems(
        listElement=sidebarElement
    )

    # Get Index Of Ethereum - Always The First
    ethereumIndex = next((i for i, item in enumerate(sidebarListItems) if item.text == 'Ethereum'), -1)

    # Filter List So We Only Have Networks
    filteredList = sidebarListItems[ethereumIndex:]

    # Dict To Hold Network Info
    networkDictionary = {}

    # Base URL
    baseUrl = getDexscreenerRoot()

    for network in filteredList:
        networkName = (network.text.lower()).replace(" ", "")
        networkDictionary[networkName] = {
            "url": f"{baseUrl}/{networkName}"
        }

    return networkDictionary


def getDexListFromTabs(driver):

    # Get The Sidebar List Element
    dexTabElement = getElementBySelector(
        driver=driver,
        selector=os.getenv('DS_DEX_TABS')
    )

    # Get All The 'li' Items
    dexTabItems = getListItems(
        listElement=dexTabElement
    )

    # Get Index Of Ethereum - Always The First
    allDexsIndex = next((i for i, item in enumerate(dexTabItems) if item.text == 'All DEXes'), -1)

    # Filter List So We Only Have Networks
    filteredList = dexTabItems[allDexsIndex + 1:]

    # List Of Available Dexs
    dexDictionary = {}

    # Base URL
    baseUrl = getCurrentURL(driver=driver)

    for dex in filteredList:
        dexName = (dex.text.lower()).replace(" ", "")
        dexDictionary[dexName] = {
            "url": f"{baseUrl}/{dexName}"
        }

    return dexDictionary


def getTokensFromTable(driver, networkName, dexName):

    allTokens = []

    # First selector is '#menu-list-18-menuitem-13' - so iterate up to 16 to get the four buttons
    timeframesToRetrieve = {
        "5M": 13,
        "1H": 14,
        "6H": 15,
        "24H": 16,
    }

    for timeframeName, timeframeIndex in timeframesToRetrieve.items():

        # Button which will open timeframe menu
        # timeframeMenu = getElementBySelector(
        #     driver=driver,
        #     selector=os.getenv("DS_DEX_TABLE_TIMEFRAME_MENU")
        # )

        # Open menu
        # timeframeMenu.click()
        #
        # timeButton = os.getenv("DS_DEX_TABLE_TIMEFRAME_OPTIONS").replace("{STARTING_NUM}", f"{timeframeIndex}")
        # timeframeButton = getElementBySelector(
        #     driver=driver,
        #     selector=timeButton
        # )
        #
        # timeframeButton.click()

        # Get The Dex Table Element
        dexTableElement = getElementBySelector(
            driver=driver,
            selector=os.getenv("DS_DEX_TABLE")
        )

        # Get All The Rows
        dexTableRows = getChildItemsByClass(
            parentElement=dexTableElement,
            className=os.getenv("DS_DEX_ROW_CLASS")
        )

        bigList = dexTableElement.get_attribute("innerText").splitlines()
        splitList = [l.split(',') for l in ','.join(bigList).split('#')][1:]
        row = [removeIllegalCharactersFromElements(item) for item in splitList]
        finalRows = [list(filter(None, item)) for item in row]

        for row in finalRows:

            index = finalRows.index(row)
            pairAddress = dexTableRows[index].get_attribute("href").split("/")[-1]

            hasUniswapBadge = len(getChildItemsByClass(
                parentElement=dexTableRows[index],
                className=os.getenv("DS_DEX_UNISWAP_BADGE_CLASS")
            )) > 0

            uniswapVersion = "N/A"
            if hasUniswapBadge:
                uniswapVersion = row.pop(1)

            tokenDetails = {
                "rank": smartEval(row[0]),
                "market": {
                    "volume": replaceNumberShorthands(row[6]),
                    "liquidity": replaceNumberShorthands(row[11]),
                    "fdv": replaceNumberShorthands(row[12])
                },
                "network": {
                    "network": networkName,
                    "txCount": smartEval(row[5]),
                },
                "dex": {
                    "dex": dexName,
                },
                "token" : {
                    "name": row[3],
                    "primaryToken": row[1],
                    "secondaryToken": row[2],
                    "tokenPair": f"{row[1]}/{row[2]}",
                    "pairAddress": f"{pairAddress}"
                },
                "price": {
                    "currentPrice": smartEval(row[4]),
                    "priceChange": {
                        "5M": smartEval(row[7]),
                        "1H": smartEval(row[8]),
                        "6H": smartEval(row[9]),
                        "24M": smartEval(row[10])
                    },
                }
            }

            if hasUniswapBadge:
                tokenDetails["dex"]["uniswapVersion"] = uniswapVersion

            allTokens.append({
                timeframeName: tokenDetails
            })

            print(tokenDetails)

    return allTokens
