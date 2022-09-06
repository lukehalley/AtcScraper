import os
import time

from src.selenium.selenium_Utils import waitAndGetElement, getListItems, getCurrentURL


def getDexscreenerRoot():
    return os.getenv('DS_ROOT_URL')

def validateDexscreenerInit(driver):

    # Get + Navigate To DS Root
    dsRoot = getDexscreenerRoot()
    driver.get(dsRoot)

    # Wait For Sidebar
    sidebar = os.getenv('DS_SIDEBAR')
    waitAndGetElement(
        driver=driver,
        selector=sidebar
    )

    # Wait For Panel
    panel = os.getenv('DS_PANEL')
    waitAndGetElement(
        driver=driver,
        selector=panel
    )