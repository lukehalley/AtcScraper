import os
from ast import literal_eval

from src.playwright.playwright_Utils import findAndCheckElement, waitForElementToGoAway


def removeIllegalCharactersFromElements(elementList):
    cleanList = []
    charsToRemove = ["#","$","%","/"]
    for el in elementList:
        for c in charsToRemove:
            el = el.replace(c, "")
        cleanList.append(el)
    return cleanList

def simplest_type(s):
    try:
        return literal_eval(s)
    except:
        return s

def replaceNumberShorthands(text):

    numberShorthands = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000
    }

    hasSymbol = any(n in text for n in numberShorthands.keys())

    if hasSymbol:
        num, magnitude = text[:-1], text[-1]
        return int(float(num) * numberShorthands[magnitude])
    else:
        return text

def smartEval(text):
    return simplest_type(text)

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

async def getRowsPairAddresses(page, networkName):
    hrefs = await page.eval_on_selector_all(f"a[href^='/{networkName}/0x']", "elements => elements.map(element => element.href)")
    pairAddresses = [item.split("/")[-1] for item in hrefs]
    return pairAddresses