"""Database query functions for network-related operations.

This module provides functions to query blockchain network data from
the database, including listing all networks and looking up network IDs.
"""
from typing import List, Any, Dict, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Database table and column names
NETWORKS_TABLE = "networks"
NETWORK_NAME_COLUMN = "name"
NETWORK_ID_COLUMN = "network_id"


def getAllNetworks(dbConnection: Any) -> List[str]:
    """
    Retrieve all network names from the database.

    Fetches the complete list of blockchain networks that have been
    configured in the system (e.g., 'ethereum', 'polygon', 'bsc').

    Args:
        dbConnection: Active database connection object.

    Returns:
        List[str]: List of all network names in the database.
    """
    query = (
        f"SELECT {NETWORK_NAME_COLUMN} "
        f"FROM {NETWORKS_TABLE}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    allNetworksDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return [network[NETWORK_NAME_COLUMN] for network in allNetworksDict]


def getNetworkDbIdByName(dbConnection: Any, networkName: str) -> Optional[int]:
    """
    Get the database ID for a network by its name.

    Looks up a network by its human-readable name and returns
    its internal database identifier.

    Args:
        dbConnection: Active database connection object.
        networkName: The name of the network to look up (e.g., 'ethereum').

    Returns:
        Optional[int]: The network's database ID, or None if not found.
    """
    query = (
        f"SELECT {NETWORK_ID_COLUMN} "
        f"FROM {NETWORKS_TABLE} "
        f"WHERE {NETWORK_NAME_COLUMN}='{networkName}'"
    )

    cursor = getCursor(dbConnection=dbConnection)

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    if results:
        return results[0][NETWORK_ID_COLUMN]
    return None


