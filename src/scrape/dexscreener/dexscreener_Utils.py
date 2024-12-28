"""Utility functions for Dexscreener data processing.

This module provides helper functions for cleaning and transforming
scraped data from Dexscreener, including text sanitization and
number format conversion.
"""
import re
from ast import literal_eval
from typing import List, Union

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Characters to remove from scraped HTML elements
ILLEGAL_CHARACTERS = ["#", "$", "%", "/", ",", "-", "<", ">"]

# Number magnitude shorthands and their multipliers
NUMBER_SHORTHANDS = {
    'K': 1000,
    'M': 1000000,
    'B': 1000000000
}

# Default value for failed number conversions
DEFAULT_NUMBER_VALUE = "0.0"


def removeIllegalCharactersFromElements(elementList: List[str]) -> List[str]:
    """
    Remove illegal characters from a list of scraped HTML elements.

    Cleans the raw text content extracted from token list rows by removing
    special characters that interfere with data parsing.

    Args:
        elementList: List of raw text strings from scraped HTML

    Returns:
        List[str]: Cleaned strings with illegal characters removed
    """
    cleanList = []
    for el in elementList:
        for char in ILLEGAL_CHARACTERS:
            el = el.replace(char, "")
        cleanList.append(el)
    return cleanList


def replaceNumberShorthands(text: str) -> str:
    """
    Convert shorthand number notation to full numeric strings.

    Transforms numbers with K/M/B suffixes (e.g., '1.5M', '200K', '3B')
    into their full numeric representation as strings.

    Args:
        text: String potentially containing shorthand notation

    Returns:
        str: Full numeric string or original text if no shorthand found
    """
    # Check if the string has a magnitude symbol
    hasSymbol = any(n in text for n in NUMBER_SHORTHANDS.keys())

    if hasSymbol:
        num, magnitude = text[:-1], text[-1]
        num = num.replace(" ", "")
        num = re.sub('[^0-9.]', '', replaceNumberShorthands(num))

        try:
            finalNum = str(float(num) * NUMBER_SHORTHANDS[magnitude])
        except (ValueError, KeyError) as e:
            logger.debug(f"Number conversion failed for '{text}': {e}")
            finalNum = DEFAULT_NUMBER_VALUE
        return finalNum
    else:
        return text


def smartEval(text: str) -> Union[int, float, str]:
    """
    Safely evaluate a string to its Python literal type.

    Attempts to convert string representations of numbers, lists,
    or other literals to their native Python types.

    Args:
        text: String to evaluate

    Returns:
        The evaluated Python literal, or original string if evaluation fails
    """
    try:
        return literal_eval(text)
    except (ValueError, SyntaxError):
        return text

# Timespan display text mapping
TIMESPAN_LABELS = {
    "5M": "Last 5 minutes",
    "1H": "Last hour",
    "6H": "Last 6 hours",
    "24H": "Last 24 hours"
}
DEFAULT_TIMESPAN = "Last 24 hours"

# JavaScript expression for extracting href attributes from elements
# Used in eval_on_selector_all to map anchor elements to their URLs
JS_EXTRACT_HREF = "elements => elements.map(element => element.href)"

# URL path separator for parsing contract addresses from hrefs
URL_PATH_SEPARATOR = "/"
ADDRESS_INDEX_FROM_END = -1


async def openTimespan(page, timeToSelect: str) -> None:
    """
    Open the timespan filter menu and select a time range.

    Args:
        page: Playwright page object
        timeToSelect: Shorthand for time range ('5M', '1H', '6H', '24H')

    Example:
        >>> await openTimespan(page, '24H')  # Select last 24 hours
        >>> await openTimespan(page, '1H')   # Select last hour
    """
    text = TIMESPAN_LABELS.get(timeToSelect, DEFAULT_TIMESPAN)
    await page.locator(f'text={text}').first.click()


async def getAllRowsMetadata(page, networkName: str) -> List[str]:
    """
    Extract pair contract addresses from all token rows on the page.

    Finds all anchor elements linking to pair pages and extracts the
    contract addresses from their href attributes.

    Args:
        page: Playwright page object
        networkName: Name of the blockchain network (e.g., 'ethereum')

    Returns:
        List[str]: List of pair contract addresses

    Example:
        >>> addresses = await getAllRowsMetadata(page, 'ethereum')
        >>> print(addresses)
        ['0x1234...abcd', '0x5678...efgh', ...]
    """
    selector = f"a[href^='/{networkName}/0x']"

    hrefs = await page.eval_on_selector_all(selector, JS_EXTRACT_HREF)
    return [item.split(URL_PATH_SEPARATOR)[ADDRESS_INDEX_FROM_END] for item in hrefs]