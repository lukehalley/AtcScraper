import asyncio
import json
import time

from dotenv import load_dotenv
from retry import retry

from src.utils.time.time_Calculations import getMinSecString

load_dotenv()

# Import helpers
from src.scrape.dexscreener.dexscreener_Execute import scrapeDexScreener
from src.utils.env.env_Environment import checkIsDocker

# Load the .env file
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging

# Set up logging
logger = setupLogging()

# Get our starting time
startingTime = time.perf_counter()

printSeparator()
logger.info(f"ATC Scraper")
printSeparator(newLine=True)

@retry()
def scrape():

    # Create an async event loop
    loop = asyncio.get_event_loop()

    # Run the Dexscreener scraper
    loop.run_until_complete(scrapeDexScreener())

    # Get our ending time
    timerString = getMinSecString(time.perf_counter() - startingTime)

    # Log that out scraping is done
    printSeparator()
    logger.info(f"Dex Screener Scrape Complete ✅")
    logger.info(f"Took: {timerString}")
    printSeparator()

if __name__ == '__main__':
    scrape()