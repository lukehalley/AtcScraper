"""Main entry point for ATC Scraper application.

Handles orchestration of scraping tasks and data processing.
"""
"""
ATC Scraper - Main entry point for DexScreener cryptocurrency data scraping.

This module initializes logging, sets up the execution environment, and
orchestrates the scraping process for cryptocurrency trading pair data
from DexScreener.

Typical usage example:
    python main.py

Environment Variables:
    See .env.example for required configuration variables.
"""
import asyncio
import logging
import time
from typing import Final

from dotenv import load_dotenv
from retry import retry

from src.scrape.dexscreener.dexscreener_Execute import scrapeDexScreener
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import setupLogging
from src.utils.time.time_Calculations import getMinSecString

# Load environment variables from .env file
load_dotenv()

# Application name constant
APP_NAME: Final[str] = "ATC Scraper"

# Set up logging
logger: logging.Logger = setupLogging()

# Get our starting time
startingTime: float = time.perf_counter()

printSeparator()
logger.info(APP_NAME)
printSeparator(newLine=True)


@retry()
def scrape() -> None:
    """
    Execute the DexScreener scraping process with automatic retry on failure.

    Creates an async event loop and runs the DexScreener scraper. Logs the
    total execution time upon completion. The @retry decorator provides
    automatic retry functionality if the scraping fails.
    """
    # Create an async event loop
    loop = asyncio.get_event_loop()

    # Run the Dexscreener scraper
    loop.run_until_complete(scrapeDexScreener())

    # Get our ending time
    timerString = getMinSecString(time.perf_counter() - startingTime)

    # Log that scraping is done
    printSeparator()
    logger.info("Dex Screener Scrape Complete")
    logger.info(f"Took: {timerString}")
    printSeparator()


if __name__ == '__main__':
    scrape()