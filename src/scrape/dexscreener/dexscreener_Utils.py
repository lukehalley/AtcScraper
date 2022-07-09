import os
from ast import literal_eval

from src.selenium.selenium_Utils import waitAndGetElement


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