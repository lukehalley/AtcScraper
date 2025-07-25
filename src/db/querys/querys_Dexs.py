"""Database query functions for DEX-related operations.

This module provides functions to query decentralized exchange (DEX)
data from the database, including lookups by network.
"""
from typing import List, Any, Dict

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Database table and column names
DEXS_TABLE = "dexs"
DEX_NAME_COLUMN = "name"


def getAllDexsForNetwork(dbConnection: Any, networkDbId: int) -> List[str]:
    """
    Retrieve all DEX names for a specific network.

    Queries the dexs table to find all decentralized exchanges
    that operate on the specified blockchain network.

    Args:
        dbConnection: Active database connection object.
        networkDbId: The database ID of the network to query.

    Returns:
        List[str]: List of DEX names associated with the given network.
            Returns empty list if no DEXs found for the network.

    Example:
        >>> dexs = getAllDexsForNetwork(db_conn, network_id=1)
        >>> print(dexs)
        ['uniswap', 'sushiswap', 'curve']
    """
    query = (
        f"SELECT {DEX_NAME_COLUMN} "
        f"FROM {DEXS_TABLE} "
        f"WHERE network_id={networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    allDexsDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    logger.debug(f"Found {len(allDexsDict)} DEXs for network ID {networkDbId}")

    return [dex[DEX_NAME_COLUMN] for dex in allDexsDict]

