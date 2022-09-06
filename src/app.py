import json
import time

from dotenv import load_dotenv

from src.scrape.dexscreener.dexscreener_Init import validateDexscreenerInit
from src.scrape.dexscreener.dexscreener_Scrape import getNetworkListFromSidebar, getDexListFromTabs, getTokensFromTable
from src.selenium.selenium_Setup import configureChromeOptions, initDriver
from src.utils.env import checkIsDocker

load_dotenv()
isDocker = checkIsDocker()

# Function that setup the browser parameters and return browser object.
def lambda_handler(event, context):

    # Set Chrome Options
    options = configureChromeOptions()

    # Init Webdriver
    driver = initDriver(
        options=options
    )

    # Dexscreener Scraping ##############
    # Init Dexscreener
    validateDexscreenerInit(
        driver=driver
    )

    # Get Network List
    networkDictionary = getNetworkListFromSidebar(
        driver=driver
    )

    networkData = {}

    for networkName, networkDetails in networkDictionary.items():

        if networkName not in networkData:
            networkData[networkName] = {}

        print(f"Scraping: {networkName}...")
        driver.get(networkDetails["url"])

        dexDictionary = getDexListFromTabs(
            driver=driver
        )

        for dexName, dexDetails in dexDictionary.items():

            if dexName not in networkData[networkName]:
                networkData[networkName][dexName] = {}

            driver.get(dexDetails["url"])

            networkData[networkName][dexName]["tokens"] = getTokensFromTable(
                driver=driver,
                networkName=networkName,
                dexName=dexName
            )

            x = 1

    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps({
            "message": "This is the message in a JSON object."
        })
    }

    return response

if __name__ == "__main__" and not isDocker:
    lambda_handler(None, None)