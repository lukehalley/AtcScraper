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

# Get the address of the pair, primary and secondary token as well as the network explorer url
def getAllRowsMetadata(page, networkName):

    hrefs = page.eval_on_selector_all(f"a[href^='/{networkName}/0x']", "elements => elements.map(element => element.href)")
    pairAddresses = [item.split("/")[-1] for item in hrefs]

    return pairAddresses