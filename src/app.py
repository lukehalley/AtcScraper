import asyncio
import json
import time
from dotenv import load_dotenv

# Import helpers
from src.scrape.dexscreener.dexscreener_Execute import scrapeDexScreener
from src.utils.env.utils_Env import checkIsDocker

# Load the .env file
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging

load_dotenv()

# Check if were running in a container - ie. in Production
isDocker = checkIsDocker()

# Set up logging
logger = setupLogging()

# Function which the Lambda will execute
def lambda_handler(event, context):

    printSeparator()
    logger.info(f"ATC Scraper")
    printSeparator(newLine=True)

    # Create an async event loop
    loop = asyncio.get_event_loop()

    # Run the Dexscreener scraper
    loop.run_until_complete(
        scrapeDexScreener()
    )

    # Send our response
    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps({
            "message": "This is the message in a JSON object."
        })
    }

    return response

# Function for running locally
if __name__ == "__main__" and not isDocker:
    starting = time.perf_counter()
    lambda_handler(None, None)
    ending = time.perf_counter()
    print(f"Took: {ending - starting}")