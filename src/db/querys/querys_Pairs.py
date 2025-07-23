"""Database query functions for trading pair operations.

This module provides functions to query trading pair data from the database,
including lookups by contract address and network ID. Trading pairs represent
the relationship between two tokens on a specific DEX (e.g., ETH/USDC on Uniswap).

Each pair is uniquely identified by its contract address and network combination.
The module enforces data integrity by detecting duplicate pair entries.

Typical usage:
    from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId

    pair = getPairForAddressAndNetworkId(
        conn,
        pairAddress="0x1234...",
        networkDbId=1
    )
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
        pairAddress: Blockchain contract address of the trading pair
        networkDbId: Database ID of the network the pair belongs to

    Returns:
        Dictionary containing pair data if found, None if not found

    Raises:
        SystemExit: If multiple pairs are found with the same address
            and network (indicates data integrity issue)

    Note:
        This function exits the application if data integrity is violated
        to prevent corrupt data from propagating through the system.
    """
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


