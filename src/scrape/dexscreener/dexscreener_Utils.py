from ast import literal_eval

# Remove any illegal characters from the raw HTML we scrape
# when getting the rows from the token lists for a dex
def removeIllegalCharactersFromElements(elementList):
    cleanList = []
    charsToRemove = ["#","$","%","/"]
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
        return int(float(num) * numberShorthands[magnitude])
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

# Get the pair address for a given page
async def getRowsPairAddresses(page, networkName):
    hrefs = await page.eval_on_selector_all(f"a[href^='/{networkName}/0x']", "elements => elements.map(element => element.href)")
    pairAddresses = [item.split("/")[-1] for item in hrefs]
    return pairAddresses