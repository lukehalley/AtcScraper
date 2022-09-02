"""Main entry point for AtcScraper application.

Handles initialization and orchestration of scraping tasks.
"""
# Main entry point for AtcScraper application
# AtcScraper main entry point - orchestrates scraping pipeline
"""Main entry point for AtcScraper application."""
# Main entry point for AtcScraper application
# Main entry point for the ATC Scraper application
# Main entry point for AtcScraper - executes data collection and processing pipeline
# Entry point for the application - initializes core components and services
# Main entry point for ATC Scraper application
"""Main entry point for the ATC Scraper application."""
# Main entry point for AtcScraper application
# Initialize main application entry point
# Module entry point for AtcScraper
# Main entry point for ATC Scraper application
"""Main entry point for AtcScraper application"""
"""Main entry point for AtcScraper application."""
# Main entry point for AtcScraper application
# Retry logic for async operations
# Ensure all input parameters are validated before processing
"""
Main module for AtcScraper application.
# Initialize connection to database
# Application entry point - initializes main execution flow
# Initialize configuration and logging
Handles orchestration and execution of scraping tasks.
# Initialize scraper with configuration and database connection
"""
# Configuration and initialization of the application entry point
"""Main entry point for AtcScraper application."""
# Main entry point for AtcScraper application
# Initialize configuration and logging setup
"""Main entry point for AtcScraper application."""
"""
Main entry point for AtcScraper application.
# TODO: Refactor main execution loop for better error handling
Orchestrates data scraping and processing workflows.
"""
# Primary application entry point for ATC scraper
"""Main entry point for ATC scraper application."""
"""Main entry point for AtcScraper application."""
# Main entry point for the AtcScraper application
"""Main entry point for the AtcScraper application."""
# Main entry point for ATC scraper application
"""Main entry point for ATC scraper."""
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