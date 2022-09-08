import os
import time
from pathlib import Path

from faker import Faker
from playwright.async_api import BrowserContext, expect, async_playwright

from src.playwright.playwright_Utils import findAndCheckElement, getListItems, getAItems, newPage
from src.scrape.dexscreener.dexscreener_Init import getDexscreenerRoot
from src.scrape.dexscreener.dexscreener_Utils import openTimespan, removeIllegalCharactersFromElements, smartEval, \
    replaceNumberShorthands

import nest_asyncio
nest_asyncio.apply()
# __import__('IPython').embed()

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


async def getTokensForDex(networkName, dexDetails):

    async with async_playwright() as p:

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=True,
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
        print(dexName)
        await page.goto(dexURL)

        # isLoading = await page.locator("text=Loading...").count() > 0
        #
        # while isLoading:
        #     print("Loading...")
        #
        #     isLoading = await page.locator("text=Loading...").count() > 0

        # cantConnect = await page.locator("text=Failed connecting to server").count() > 0
        #
        # while cantConnect:
        #     print("Trying again...")
        #     time.sleep(5)
        #     await page.reload()
        #     cantConnect = await page.locator("text=Failed connecting to server").count() > 0
        #
        # await expect(page.locator("text=Failed connecting to server")).to_have_count(0)

        await page.locator('text=Liquidity').first.click()

        tokenResults = {}

        # First selector is '#menu-list-18-menuitem-13' - so iterate up to 16 to get the four buttons
        allTimeframes = {
            "5M": 13,
            "1H": 14,
            "6H": 15,
            "24H": 16,
        }

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
                "token": {
                    "name": row[3],
                    "primaryToken": row[1],
                    "secondaryToken": row[2],
                    "tokenPair": f"{row[1]}/{row[2]}",
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

        return results
