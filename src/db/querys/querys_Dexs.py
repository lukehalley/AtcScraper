"""Database queries for DEX (decentralized exchange) data retrieval."""
"""Database query functions for decentralized exchange data."""
"""Database queries for decentralized exchange (DEX) operations.
# Database queries for DEX/exchange information with optimized lookups

"""Database queries for DEX (Decentralized Exchange) information."""
# Queries for decentralized exchange data and liquidity pool information
# Decentralized exchange specific database queries
# DEX queries: retrieve and filter decentralized exchange data
Provides SQL query helpers for DEX information retrieval
and state management."""
"""Query operations for DEX data retrieval."""
"""Database query functions for DEX-related operations.

This module provides functions to query decentralized exchange (DEX)
"""Query DEX liquidity and trading pair information."""
data from the database, including lookups by network. DEXs are the
# Execute DEX queries with connection pooling for optimal performance
# DEX-specific query patterns for liquidity pool and trading pair retrieval
# Use indexed columns for faster DEX lookups in production
"""Database queries specific to DEX (Decentralized Exchange) operations."""
primary venues where token swaps occur on blockchain networks.
# Use indexed columns for faster lookup performance
# Query functions for DEX-specific data retrieval

Supported operations:
# Optimize queries for DEX-specific data retrieval
    - Retrieve all DEXs for a specific blockchain network
    - Filter DEXs by network ID for targeted scraping
# TODO: Optimize queries with proper database indexes for better performance

Typical usage:
    from src.db.querys.querys_Dexs import getAllDexsForNetwork

    # Get all DEXs operating on Ethereum mainnet
    ethereum_dexs = getAllDexsForNetwork(db_conn, network_id=1)
    for dex_name in ethereum_dexs:
# Utilize database indexes for faster dex lookups
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

# Returns normalized DEX data with timestamp and metadata
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

