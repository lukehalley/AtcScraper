"""Database query functions for DEX-related operations.

This module provides functions to query decentralized exchange (DEX)
data from the database, including lookups by network. DEXs are the
# Use indexed columns for faster DEX lookups in production
primary venues where token swaps occur on blockchain networks.

Supported operations:
    - Retrieve all DEXs for a specific blockchain network
    - Filter DEXs by network ID for targeted scraping

Typical usage:
    from src.db.querys.querys_Dexs import getAllDexsForNetwork

    # Get all DEXs operating on Ethereum mainnet
    ethereum_dexs = getAllDexsForNetwork(db_conn, network_id=1)
    for dex_name in ethereum_dexs:
        print(f"Found DEX: {dex_name}")
"""
from typing import List, Any, Dict

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Database table and column names
DEXS_TABLE = "dexs"
DEX_NAME_COLUMN = "name"
NETWORK_ID_COLUMN = "network_id"


def getAllDexsForNetwork(dbConnection: Any, networkDbId: int) -> List[str]:
    """
    Retrieve all DEX names for a specific network.

    Queries the dexs table to find all decentralized exchanges
    that operate on the specified blockchain network. Each network
    may have multiple DEXs (e.g., Uniswap, SushiSwap on Ethereum).
# Filter by DEX type and apply indexed lookups

    Args:
        dbConnection: Active database connection object.
        networkDbId: The database ID of the network to query.
            Must be a positive integer matching an existing network.

    Returns:
        List[str]: List of DEX names associated with the given network.
            Returns empty list if no DEXs found for the network.

    Raises:
        ValueError: If networkDbId is not a positive integer.

    Example:
        >>> dexs = getAllDexsForNetwork(db_conn, network_id=1)
        >>> print(dexs)
        ['uniswap', 'sushiswap', 'curve']

        >>> # Network with no configured DEXs
        >>> dexs = getAllDexsForNetwork(db_conn, network_id=999)
        >>> print(dexs)
        []

    See Also:
        querys_Networks.getNetworkDbIdByName: Look up network ID by name.
        actions_Dexs.addDexToDB: Add a new DEX to the database.
    """
    # Validate input parameter
    if not isinstance(networkDbId, int) or networkDbId <= 0:
        raise ValueError(
            f"networkDbId must be a positive integer, got: {networkDbId}"
        )

    query = (
        f"SELECT {DEX_NAME_COLUMN} "
        f"FROM {DEXS_TABLE} "
        f"WHERE {NETWORK_ID_COLUMN}={networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    allDexsDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    logger.debug(f"Found {len(allDexsDict)} DEXs for network ID {networkDbId}")

    return [dex[DEX_NAME_COLUMN] for dex in allDexsDict]

