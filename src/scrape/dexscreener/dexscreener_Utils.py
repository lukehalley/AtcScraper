import os
import re
from ast import literal_eval

# Remove any illegal characters from the raw HTML we scrape
# when getting the rows from the token lists for a dex
def removeIllegalCharactersFromElements(elementList):
    cleanList = []
    charsToRemove = ["#", "$", "%", "/", ",", "-", "<", ">"]
    for el in elementList:
        for c in charsToRemove:
            el = el.replace(c, "")
        cleanList.append(el)
    return cleanList

# Turn 1L, 13M, 211B into ints
def replaceNumberShorthands(text):

    # Convert dict
    numberShorthands = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000
    }

    # Check if the string has this symbol
    hasSymbol = any(n in text for n in numberShorthands.keys())

    # If it does, turn it back into a number
    if hasSymbol:

        num, magnitude = text[:-1], text[-1]
        num = num.replace(" ", "")
        num = re.sub('[^0-9.]', '', replaceNumberShorthands(num))

        try:
            finalNum = str(float(num) * numberShorthands[magnitude])
        except:
            finalNum = "0.0"
        return finalNum
    else:
        return text

# Automatically convert a string into its normal format
def smartEval(text):
    try:
        return literal_eval(text)
    except:
        return text

# Open the timespan menu on the token list page and click the time we want
async def openTimespan(page, timeToSelect):

    if timeToSelect == "5M":
        text="Last 5 minutes"

    elif timeToSelect == "1H":
        text="Last hour"

    elif timeToSelect == "6H":
        text="Last 6 hours"
    else:
        text="Last 24 hours"

    await page.locator(f'text={text}').first.click()

# Get the address of the pair, primary and secondary token as well as the network explorer url
async def getAllRowsMetadata(page, networkName):

    rowMetadata = {}

    hrefs = await page.eval_on_selector_all(f"a[href^='/{networkName}/0x']", "elements => elements.map(element => element.href)")
    pairAddresses = [item.split("/")[-1] for item in hrefs]

    x = 1

    baseLink = '/'.join(hrefs[0].split("/")[0:4])

    allRowMetadata = []

    for pair in pairAddresses:

        metadataObject = {

        }

        pairUrl = f"{baseLink}/{pair}"

        metadataObject["pairAddress"] = pair

        # Go the pair graph page
        await page.goto(pairUrl)

        # Get all elements with the external link label
        allBlockExplorerLinks = page.locator(selector="[aria-label='External Link']")

        # Get the second element on the page which is the address of the primary token
        tokenExplorerLink = await allBlockExplorerLinks.nth(1).get_attribute("href")
        metadataObject["primaryTokenAddress"] = tokenExplorerLink.split("/")[-1]

        # Get the network explorer while were at it
        metadataObject["networkExplorer"] = '/'.join(tokenExplorerLink.split("/")[0:4])

        # # Open up the menu that allows us to invert the pair
        # swapMenuOpenBtnXpath = os.getenv("DS_SWAP_MENU_OPEN_BTN")
        # await page.locator(f"xpath={swapMenuOpenBtnXpath}").click()
        #
        # # Click the invert pair button
        # await page.locator(f'text=Invert Pair').first.click()
        # tokenExplorerLink = await allBlockExplorerLinks.nth(1).get_attribute("href")
        #
        # # Get the secondary token address
        # metadataObject["secondaryTokenAddress"] = tokenExplorerLink.split("/")[-1]

        x = 1

    return allRowMetadata