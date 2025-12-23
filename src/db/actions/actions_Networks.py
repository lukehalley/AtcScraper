"""Database actions for managing blockchain network records.

This module provides functions to add and manage blockchain network entries
in the database. Networks represent the different blockchains that the
scraper monitors for DEX trading activity.
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


def addNetworkToDB(dbConnection: Any, networkName: str) -> int:
    """
    Add a new blockchain network to the database.

    Creates a network record with the provided name. All other fields
    (chain configuration, explorer settings, gas limits) are set to NULL
    and can be updated later.

    Args:
        dbConnection: Active database connection object
        networkName: Name of the blockchain network (e.g., 'ethereum', 'bsc')

    Returns:
        int: The database ID of the newly inserted network
    """
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

