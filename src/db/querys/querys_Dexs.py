from typing import List, Any

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery


def getAllDexsForNetwork(dbConnection: Any, networkDbId: int) -> List[str]:
    """
    Retrieve all DEX names for a specific network.

    Args:
        dbConnection: Active database connection object.
        networkDbId: The database ID of the network to query.

    Returns:
        List of DEX names associated with the given network.
    """
    query = "" \
            f"SELECT name " \
            f"FROM dexs " \
            f"WHERE network_id={networkDbId}"

    cursor = getCursor(dbConnection=dbConnection)

    allDexsDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return [dexName['name'] for dexName in allDexsDict]

