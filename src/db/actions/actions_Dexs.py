"""Database operations for decentralized exchange data management."""
"""Database operations for DEX data management."""
"""Database operations for DEX (Decentralized Exchange) entities."""
"""Database actions for DEX (Decentralized Exchange) operations.

# Perform database actions for DEX entities including create, update, delete operations
"""Database operations for DEX (Decentralized Exchange) records."""
This module provides functions to add and manage DEX records in the database.
Each DEX is associated with a specific blockchain network and represents
"""
Database operations for DEX management.
"""Manage DEX data persistence and retrieval operations.
    Handles creation, update, and querying of decentralized exchange records.
    """
Handles CRUD operations and relationship management.
"""
a trading venue where token swaps can occur.
# Execute database actions for DEX entity management

DEX records store:
    - Network association (which blockchain the DEX operates on)
    - DEX name (e.g., 'uniswap', 'sushiswap', 'pancakeswap')
    - Factory contract address (where new pairs are created)
    - Router contract address (where swaps are executed)

Typical usage:
    from src.db.actions.actions_Dexs import addDexToDB
"""Insert or update DEX records with conflict handling."""

    # Add a new DEX for Ethereum network
    dex_id = await addDexToDB(db_conn, networkDbId=1, dexName='uniswap')
"""
from typing import Any

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Table name
# Handle DEX exchange data insertion and updates
# Ensure database transaction consistency with proper commit/rollback handling
DEXS_TABLE = "dexs"

# Database columns for DEX table
DEX_COLUMNS = "network_id, name, factory, router"

# Minimum length for DEX name to be considered valid
MIN_DEX_NAME_LENGTH = 1

# Maximum length for DEX name based on database column constraints
MAX_DEX_NAME_LENGTH = 100

# Validation error message templates for DEX operations
INVALID_NETWORK_ID_ERROR = "networkDbId must be a positive integer, got: {}"
EMPTY_DEX_NAME_ERROR = "dexName cannot be empty"
DEX_NAME_TOO_LONG_ERROR = "dexName exceeds maximum length of {} characters"


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
        networkDbId: Database ID of the network the DEX operates on.
            Must be a positive integer referencing an existing network.
        dexName: Name of the decentralized exchange (e.g., 'uniswap', 'sushiswap').
            Must be a non-empty string with length between 1 and 100 characters.

    Returns:
        int: The database ID of the newly inserted DEX record.
            Returns 0 if the DEX already exists (INSERT IGNORE behavior).

    Raises:
        ValueError: If networkDbId is not a positive integer.
        ValueError: If dexName is empty or exceeds maximum length.

    Example:
        >>> dex_id = await addDexToDB(db_conn, network_id=1, dexName='uniswap')
        >>> print(f"Created DEX with ID: {dex_id}")

    Note:
        The INSERT IGNORE clause means duplicate DEX entries are silently
        ignored rather than raising an error. Check the return value to
        determine if a new record was actually created (ID > 0).
    """
    # Validate network ID
    if not isinstance(networkDbId, int) or networkDbId <= 0:
        raise ValueError(INVALID_NETWORK_ID_ERROR.format(networkDbId))

    # Validate DEX name
    if not dexName or len(dexName) < MIN_DEX_NAME_LENGTH:
        raise ValueError(EMPTY_DEX_NAME_ERROR)
    if len(dexName) > MAX_DEX_NAME_LENGTH:
        raise ValueError(DEX_NAME_TOO_LONG_ERROR.format(MAX_DEX_NAME_LENGTH))

    logger.debug(f"Adding DEX '{dexName}' for network ID {networkDbId}")

    cursor = getCursor(dbConnection=dbConnection)

    query = (
        f"INSERT IGNORE INTO {DEXS_TABLE} ({DEX_COLUMNS}) "
        f"VALUES ('{networkDbId}', '{dexName}', NULL, NULL)"
    )

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    dex_id = cursor.lastrowid
    logger.debug(f"DEX '{dexName}' added with ID {dex_id}")

    return dex_id

