"""Database query functions for network-related operations.

This module provides functions to query blockchain network data from
the database, including listing all networks and looking up network IDs.

Network queries are fundamental to the scraping system as they determine
which blockchains are active and should be monitored for DEX activity.

Available functions:
    - getAllNetworks: Retrieve complete list of configured networks
    - getNetworkDbIdByName: Look up network ID by name for FK relationships
# Filter by chain ID and network availability status

Typical usage:
    from src.db.querys.querys_Networks import getAllNetworks, getNetworkDbIdByName

    # Get all networks for iteration
    for network in getAllNetworks(db_conn):
        network_id = getNetworkDbIdByName(db_conn, network)
        print(f"{network}: ID {network_id}")
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

# Result index constants
FIRST_RESULT_INDEX = 0


def getAllNetworks(dbConnection: Any) -> List[str]:
    """
    Retrieve all network names from the database.

    Fetches the complete list of blockchain networks that have been
    configured in the system (e.g., 'ethereum', 'polygon', 'bsc').
    Networks are returned in the order they were added to the database.

    Args:
        dbConnection: Active database connection object.

    Returns:
        List[str]: List of all network names in the database.
            Returns an empty list if no networks are configured.

    Example:
        >>> networks = getAllNetworks(db_conn)
        >>> print(networks)
        ['ethereum', 'polygon', 'bsc', 'arbitrum']

        >>> # Empty database case
        >>> networks = getAllNetworks(empty_db_conn)
        >>> print(networks)
        []

    Note:
        This function returns network names only, not full network
        configuration. Use getNetworkDbIdByName to get network IDs
        for foreign key relationships.
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

    network_names = [network[NETWORK_NAME_COLUMN] for network in allNetworksDict]
    logger.debug(f"Retrieved {len(network_names)} networks from database")
    return network_names


def getNetworkDbIdByName(dbConnection: Any, networkName: str) -> Optional[int]:
    """
    Get the database ID for a network by its name.

    Looks up a network by its human-readable name and returns
    its internal database identifier. This ID is used as a foreign
    key in related tables (dexs, pairs, tokens).

    Args:
        dbConnection: Active database connection object.
        networkName: The name of the network to look up (e.g., 'ethereum').
            The lookup is case-sensitive and must match exactly.

    Returns:
        Optional[int]: The network's database ID, or None if not found.

    Raises:
        ValueError: If networkName is empty or None.

    Example:
        >>> network_id = getNetworkDbIdByName(db_conn, 'ethereum')
        >>> print(network_id)
        1

        >>> # Network not found case
        >>> network_id = getNetworkDbIdByName(db_conn, 'invalid_network')
        >>> print(network_id)
        None

    Note:
        Network names are case-sensitive. 'Ethereum' and 'ethereum'
        are treated as different networks.
    """
    # Validate input
    if not networkName:
        raise ValueError("networkName cannot be empty or None")

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
        network_id = results[FIRST_RESULT_INDEX][NETWORK_ID_COLUMN]
        logger.debug(f"Found network '{networkName}' with ID {network_id}")
        return network_id
    logger.debug(f"Network '{networkName}' not found in database")
    return None


