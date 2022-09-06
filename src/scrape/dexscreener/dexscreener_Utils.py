import os
from ast import literal_eval

from src.selenium.selenium_Utils import waitAndGetElement, waitAndClickText, getChildItemsByClass


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

def openTimespan(driver, timeToSelect):

    menuParent = waitAndGetElement(
        driver=driver,
        selector=os.getenv("DS_DEX_TABLE_TIMEFRAME_MENU")
    )

    menuParent.find_elements_by_css_selector("*")[0].click()

    if timeToSelect == "5M":
        waitAndClickText(
            driver=driver,
            text="Last 5 minutes"
        )
    elif timeToSelect == "1H":
        waitAndClickText(
            driver=driver,
            text="Last hour"
        )
    elif timeToSelect == "6H":
        waitAndClickText(
            driver=driver,
            text="Last 6 hours"
        )
    else:
        waitAndClickText(
            driver=driver,
            text="Last 24 hours"
        )

def getDexTableRows(driver):

    # Get All The Rows
    dexTableRows = []
    dexTableElement = None
    while len(dexTableRows) <= 0:
        dexTableElement = waitAndGetElement(
            driver=driver,
            selector=os.getenv("DS_DEX_TABLE"),
            useSelector=True
        )
        dexTableRows = getChildItemsByClass(
            parentElement=dexTableElement,
            className=os.getenv("DS_DEX_ROW_CLASS")
        )
    return dexTableElement, dexTableRows