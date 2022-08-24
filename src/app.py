import asyncio
import json
import time
from dotenv import load_dotenv

from src.db.db_Query import checkIfRowExistsByValue
from src.db.db_Setup import initDBConnection

load_dotenv()

# Import helpers
from src.scrape.dexscreener.dexscreener_Execute import scrapeDexScreener
from src.utils.env.utils_Env import checkIsDocker

# Load the .env file
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging

# Check if were running in a container - ie. in Production
isDocker = checkIsDocker()

# Set up logging
logger = setupLogging()

# Init MySQL DB
cnx = initDBConnection()
checkIfRowExistsByValue(
    cnx=cnx,
    table="networks",
    column="name",
    value="ethereum"
)

# Function which the Lambda will execute
def lambda_handler(event, context):

    # Gte our starting time
    starting = time.perf_counter()

    printSeparator()
    logger.info(f"ATC Scraper")
    printSeparator(newLine=True)

    # Create an async event loop
    loop = asyncio.get_event_loop()

    # Run the Dexscreener scraper
    results = loop.run_until_complete(
        scrapeDexScreener()
    )

    # Get our ending time
    ending = time.perf_counter()

    # Log that out scraping is done
    printSeparator()
    logger.info(f"Dex Screener Scrape Complete ✅")
    logger.info(f"Took {ending - starting}s")
    printSeparator()

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
    lambda_handler(None, None)