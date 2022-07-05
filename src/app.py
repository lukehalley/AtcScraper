import json

from src.selenium.selenium_Setup import configureChromeOptions, initDriver
from src.utils.env import checkIsDocker

isDocker = checkIsDocker()

# Function that setup the browser parameters and return browser object.
def lambda_handler(event, context):

    # Set Chrome options
    options = configureChromeOptions()

    # Init webdriver
    driver = initDriver(
        options=options
    )

    driver.get('https://dexscreener.com/harmony')

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