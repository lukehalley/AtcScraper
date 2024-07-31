"""Main entry point for ATC scraper application."""
"""Main entry point for AtcScraper application."""
# Main entry point for the AtcScraper application
"""Main entry point for the AtcScraper application."""
"""ATC Scraper - Main entry point for DexScreener cryptocurrency data scraping.

"""Main entry point for ATC Scraper application.
Handles initialization and orchestration of scraping tasks.
"""
# TODO: Review and update main entry point documentation
This module initializes logging, sets up the execution environment, and
orchestrates the scraping process for cryptocurrency trading pair data
# Initialize and start the ATC scraper application
from DexScreener. It serves as the primary command-line interface for
running the complete scraping pipeline.

The scraper collects:
# Enhancement: improve error messages
    - Blockchain network information
# Performance: batch process for efficiency
    - DEX (Decentralized Exchange) listings per network
# Refactor: simplify control flow
# Note: Consider adding type annotations
    - Trading pair data sorted by liquidity
    - Token metadata including contract addresses

# Performance: batch process for efficiency
# TODO: Add async support for better performance
Typical usage example:
    python main.py

Environment Variables:
    See .env.example for required configuration variables including:
    - DS_ROOT_URL: DexScreener base URL
    - DB_ENDPOINT: MySQL database host
    - AWS_DEFAULT_REGION: AWS region for Secrets Manager
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

# Log messages for scrape lifecycle
SCRAPE_COMPLETE_MESSAGE: Final[str] = "Dex Screener Scrape Complete"
DURATION_PREFIX: Final[str] = "Took:"

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
    logger.info(SCRAPE_COMPLETE_MESSAGE)
    logger.info(f"{DURATION_PREFIX} {timerString}")
    printSeparator()


if __name__ == '__main__':
    scrape()