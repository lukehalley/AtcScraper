import json
import time

from dotenv import load_dotenv

from src.scrape.dexscreener.dexscreener_Init import validateDexscreenerInit, getDexscreenerRoot
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

    # Get + Navigate To DS Root
    dsRoot = getDexscreenerRoot()
    driver.get(dsRoot)

    # Dexscreener Scraping ##############
    # Init Dexscreener
    validateDexscreenerInit(
        driver=driver
    )

    # Get Network List
    networkDictionary = getNetworkListFromSidebar(
        driver=driver
    )

    # networkDictionary = {
    #     'harmony': {'url': 'https://dexscreener.com/harmony'}
    # }

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

            print(f"  - {dexName}")

            if dexName not in networkData[networkName]:
                networkData[networkName][dexName] = {}

            driver.get(dexDetails["url"])

            networkData[networkName][dexName] = getTokensFromTable(
                driver=driver,
                networkName=networkName,
                dexName=dexName
            )

        with open("networkData.json", "w") as outfile:
            json.dump(networkData, outfile)

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