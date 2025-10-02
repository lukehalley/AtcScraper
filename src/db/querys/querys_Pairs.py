"""Database query functions for trading pair operations.

This module provides functions to query trading pair data from the database,
including lookups by contract address and network ID.
"""
import sys
from typing import Any, Dict, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Exit code for data integrity errors
DATA_INTEGRITY_ERROR_CODE = 1


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
    """
    query = (
        f"SELECT * FROM pairs "
        f"WHERE pairs.address = '{pairAddress}' "
        f"AND pairs.network_id = {networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    pairResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    pairResultsLen = len(pairResults)

    if pairResultsLen > 1:
        error_msg = (
            f"Data integrity error: Multiple pairs found with "
            f"address '{pairAddress}' on network ID {networkDbId}"
        )
        logger.error(error_msg)
        sys.exit(error_msg)

    return pairResults[0] if pairResultsLen == 1 else None


