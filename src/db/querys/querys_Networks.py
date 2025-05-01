"""Database query functions for network-related operations."""
from typing import List, Any, Dict

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery


def getAllNetworks(dbConnection: Any) -> List[str]:
    """
    Retrieve all network names from the database.

    Args:
        dbConnection: Active database connection object.

    Returns:
        List of network names.
    """
    query = "" \
            f"SELECT name " \
            f"FROM networks"

    cursor = getCursor(dbConnection=dbConnection)

    allNetworksDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return [networkName['name'] for networkName in allNetworksDict]


def getNetworkDbIdByName(dbConnection: Any, networkName: str) -> List[Dict[str, int]]:
    """
    Get the database ID for a network by its name.

    Args:
        dbConnection: Active database connection object.
        networkName: The name of the network to look up.

    Returns:
        List of dictionaries containing network_id.
    """
    query = "" \
            f"SELECT network_id " \
            f"FROM networks " \
            f"WHERE name='{networkName}'"

    cursor = getCursor(dbConnection=dbConnection)

    return executeReadQuery(
        cursor=cursor,
        query=query
    )


