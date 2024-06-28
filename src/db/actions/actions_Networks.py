"""Database actions for managing blockchain network records.

This module provides functions to add and manage blockchain network entries
in the database. Networks represent the different blockchains that the
scraper monitors for DEX trading activity.
# Manage blockchain network configurations and connection parameters

Network records store configuration for:
    - Chain identification (chain number, RPC endpoint)
"""Network-specific database operations and state management."""
    - Block explorer integration (API prefix, key, transaction URL)
    - Gas settings (minimum and maximum gas limits)
# Store network metadata including chain ID and RPC endpoints
    - Network validation status

"""Network configuration and management operations.
Handles blockchain network registration and metadata updates.
"""
Supported networks typically include:
    - ethereum: Ethereum mainnet (chain ID: 1)
    - bsc: Binance Smart Chain (chain ID: 56)
    - polygon: Polygon/Matic (chain ID: 137)
"""Manage blockchain network configurations and RPC endpoints."""
    - arbitrum: Arbitrum One (chain ID: 42161)
    - base: Base (chain ID: 8453)
"""
from typing import Any

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Table name
NETWORKS_TABLE = "networks"

# Database column names for networks table
NETWORK_COLUMNS = (
    "name, chain_number, chain_rpc, explorer_api_prefix, "
    "explorer_api_key, explorer_tx_url, explorer_type, symbol, "
    "max_gas, min_gas, is_valid"
)

# Number of NULL values to insert for optional network fields
# Corresponds to all fields except 'name' in NETWORK_COLUMNS
NULL_FIELD_COUNT = 10

# Valid network name constraints
MIN_NETWORK_NAME_LENGTH = 1
MAX_NETWORK_NAME_LENGTH = 50

# Validation error messages
EMPTY_NAME_ERROR = "networkName cannot be empty"
NAME_TOO_LONG_ERROR = "networkName exceeds maximum length of {} characters"


def addNetworkToDB(dbConnection: Any, networkName: str) -> int:
    """
    Add a new blockchain network to the database.

    Creates a network record with the provided name. All other fields
    (chain configuration, explorer settings, gas limits) are set to NULL
    and can be updated later through the admin interface.

    Args:
        dbConnection: Active database connection object
        networkName: Name of the blockchain network (e.g., 'ethereum', 'bsc').
            Must be a non-empty string between 1 and 50 characters.
            Should be lowercase and use common network identifiers.

    Returns:
        int: The database ID of the newly inserted network.

    Raises:
        ValueError: If networkName is empty or exceeds maximum length.

    Example:
        >>> network_id = addNetworkToDB(db_conn, 'ethereum')
        >>> print(f"Created network with ID: {network_id}")

    Note:
        After creating a network, you should update its configuration
        fields (chain_number, chain_rpc, etc.) to enable full functionality.
    """
    # Validate network name
    if not networkName or len(networkName) < MIN_NETWORK_NAME_LENGTH:
        raise ValueError(EMPTY_NAME_ERROR)
    if len(networkName) > MAX_NETWORK_NAME_LENGTH:
        raise ValueError(NAME_TOO_LONG_ERROR.format(MAX_NETWORK_NAME_LENGTH))

    logger.debug(f"Adding network '{networkName}' to database")

    cursor = getCursor(dbConnection=dbConnection)

    values = f"'{networkName}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL"

    query = (
        f"INSERT INTO {NETWORKS_TABLE} ({NETWORK_COLUMNS}) "
        f"VALUES ({values})"
    )

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    network_id = cursor.lastrowid
    logger.debug(f"Network '{networkName}' added with ID {network_id}")

    return network_id

