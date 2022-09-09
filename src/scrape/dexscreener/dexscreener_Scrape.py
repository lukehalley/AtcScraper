import os
import time
from pathlib import Path

from faker import Faker
from playwright.async_api import BrowserContext, expect, async_playwright

from src.playwright.playwright_Utils import findAndCheckElement, getListItems, getAItems, newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot, validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Utils import removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands, getRowsPairAddresses

import nest_asyncio

from src.utils.env.utils_Env import checkHeadless
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger

nest_asyncio.apply()

logger = getProjectLogger()

async def gatherNetworkList(page):

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

    # filteredList = filteredList[0:5]

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

async def gatherDexListFromTabs(page):

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

async def gatherNetworkDexs(networkName, networkDetails, browser: BrowserContext):

    page = await newPage(browser=browser)

    await page.goto(networkDetails["url"])

    # Init Dexscreener
    await validateDexscreenerInit(
        page=page
    )

    networksDexs = await gatherDexListFromTabs(
        page=page
    )
    amountOfDexs = len(networksDexs)

    await page.close()

    obj = {
        networkName: networksDexs
    }

    logger.info(f"{networkName.title()}: {amountOfDexs}")

    return obj

async def gatherTokensForDex(networkName, dexDetails):

    async with async_playwright() as p:

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        runHeadless = checkHeadless()

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=runHeadless,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=fakeUserAgent
        )

        dexName = dexDetails["name"]
        dexURL = dexDetails["url"]

        page = await newPage(browser=browser)

        await page.goto(dexURL)

        await page.locator('text=Liquidity').first.click()

        # Get The Sidebar List Element
        dexTable = os.getenv('DS_DEX_TABLE')
        dexTableElement = await findAndCheckElement(
            page=page,
            selector=dexTable
        )

        # Get All The 'li' Items
        dexTabItems = await getAItems(
            listElement=dexTableElement
        )

        # Get Hrefs
        pairAddresses = await getRowsPairAddresses(
            page=page,
            networkName=networkName
        )

        rows = [i for i in dexTabItems if i.startswith('#')]
        rowsSplit = [l.split("\n") for l in rows]
        cleanRows = [removeIllegalCharactersFromElements(item) for item in rowsSplit]
        finalRows = [list(filter(None, item)) for item in cleanRows]

        results = []

        for row in finalRows:

            hasUniswapBadge = row[1] == "V1" or row[1] == "V2" or row[1] == "V3"

            uniswapVersion = "N/A"
            if hasUniswapBadge:
                uniswapVersion = row.pop(1)

            # Fix Some Rows Coming Back With Missing Data
            expectedListSize = 13
            rowLength = len(row)
            if rowLength != 13:
                if rowLength > expectedListSize:
                    row = row[0:13]
                else:
                    slotsToFill = abs(13 - len(row))

                    for _ in range(slotsToFill):
                        row.append("N/A")

            tokenRank = smartEval(row[0])
            pairAddress = pairAddresses[tokenRank - 1]

            tokenDetails = {
                "rank": tokenRank,
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

            results.append(tokenDetails)

        await page.close()

        await browser.close()

        amountOfTokens = len(results)
        logger.info(f"- {dexName.title()}: {amountOfTokens}")

        return results
