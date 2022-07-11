import os

from src.selenium.selenium_Utils import waitAndGetElement


def getDexscreenerRoot():
    return os.getenv('DS_ROOT_URL')

def validateDexscreenerInit(driver):

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