"""Database actions for DEX (Decentralized Exchange) operations.

This module provides functions to add and manage DEX records in the database.
Each DEX is associated with a specific blockchain network.
"""
from typing import Any

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Database columns for DEX table
DEX_COLUMNS = "network_id, name, factory, router"


async def addDexToDB(
    dbConnection: Any,
    networkDbId: int,
    dexName: str
) -> int:
    """
    Add a new decentralized exchange to the database.

    Inserts a DEX record with the network association. The factory and router
    contract addresses are set to NULL and can be updated later when available.
    Uses INSERT IGNORE to prevent duplicate entries.

    Args:
        dbConnection: Active database connection object
        networkDbId: Database ID of the network the DEX operates on
        dexName: Name of the decentralized exchange (e.g., 'uniswap', 'sushiswap')

    Returns:
        int: The database ID of the newly inserted DEX record
    """
    cursor = getCursor(dbConnection=dbConnection)

    query = (
        f"INSERT IGNORE INTO dexs ({DEX_COLUMNS}) "
        f"VALUES ('{networkDbId}', '{dexName}', NULL, NULL)"
    )

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

