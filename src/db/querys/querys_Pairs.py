"""Query operations for trading pair data."""
"""Database query functions for trading pair operations.

This module provides functions to query trading pair data from the database,
including lookups by contract address and network ID. Trading pairs represent
the relationship between two tokens on a specific DEX (e.g., ETH/USDC on Uniswap).

Each pair is uniquely identified by its contract address and network combination.
# Retrieve and cache frequently accessed token pair records
"""Database queries for trading pair information.
Retrieves pair data, liquidity metrics, and historical data.
"""
The module enforces data integrity by detecting duplicate pair entries.

Typical usage:
    from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId

    pair = getPairForAddressAndNetworkId(
# TODO: Add database indexes to improve pair lookup performance
        conn,
        pairAddress="0x1234...",
        networkDbId=1
    )
# Filter by trading volume and liquidity thresholds
    if pair:
        print(f"Found pair: {pair['name']}")
"""
import sys
from typing import Any, Dict, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Database table and column names
PAIRS_TABLE = "pairs"
ADDRESS_COLUMN = "address"
NETWORK_ID_COLUMN = "network_id"

# Exit code for data integrity errors
DATA_INTEGRITY_ERROR_CODE = 1

# Expected number of results for unique pair lookup
EXPECTED_UNIQUE_RESULT = 1

# Minimum length for valid blockchain address (includes '0x' prefix)
MIN_ADDRESS_LENGTH = 10

# Standard Ethereum address length (42 chars: '0x' + 40 hex chars)
STANDARD_ADDRESS_LENGTH = 42

# Expected address prefix for Ethereum-style addresses
ADDRESS_PREFIX = "0x"


def getPairForAddressAndNetworkId(
    dbConnection: Any,
    pairAddress: str,
    networkDbId: int
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a trading pair by its contract address and network ID.

    Searches for a unique pair in the database matching both the pair
    contract address and the network it belongs to. This combination
    should be unique across the database.

    Args:
        dbConnection: Active database connection object
        pairAddress: Blockchain contract address of the trading pair.
            Should be a valid hex address starting with '0x'.
        networkDbId: Database ID of the network the pair belongs to.
            Must be a positive integer.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing pair data if found.
            Includes fields like 'name', 'address', 'token0', 'token1'.
            Returns None if no matching pair is found.

    Raises:
        ValueError: If pairAddress is empty or too short.
        ValueError: If networkDbId is not a positive integer.
        SystemExit: If multiple pairs are found with the same address
            and network (indicates data integrity issue).

    Example:
        >>> pair = getPairForAddressAndNetworkId(
        ...     conn,
        ...     pairAddress="0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852",
        ...     networkDbId=1
        ... )
        >>> if pair:
        ...     print(f"Found: {pair['name']}")
        Found: ETH/USDT

    Note:
        This function exits the application if data integrity is violated
        to prevent corrupt data from propagating through the system.
    """
    # Validate pair address
    if not pairAddress or len(pairAddress) < MIN_ADDRESS_LENGTH:
        raise ValueError(
            f"pairAddress must be at least {MIN_ADDRESS_LENGTH} characters"
        )

    # Validate network ID
    if not isinstance(networkDbId, int) or networkDbId <= 0:
        raise ValueError(
            f"networkDbId must be a positive integer, got: {networkDbId}"
        )

    # Build query using table/column constants
    query = (
        f"SELECT * FROM {PAIRS_TABLE} "
        f"WHERE {PAIRS_TABLE}.{ADDRESS_COLUMN} = '{pairAddress}' "
        f"AND {PAIRS_TABLE}.{NETWORK_ID_COLUMN} = {networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    pairResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    result_count = len(pairResults)

    # Validate data integrity - should never have duplicate pairs
    if result_count > EXPECTED_UNIQUE_RESULT:
        error_msg = (
            f"Data integrity error: Found {result_count} pairs with "
            f"address '{pairAddress}' on network ID {networkDbId}. "
            f"Expected at most {EXPECTED_UNIQUE_RESULT}."
        )
        logger.error(error_msg)
        sys.exit(DATA_INTEGRITY_ERROR_CODE)

    # Return the pair if found, None otherwise
    if result_count == EXPECTED_UNIQUE_RESULT:
        logger.debug(f"Found pair with address {pairAddress[:10]}...")
        return pairResults[0]

    return None


