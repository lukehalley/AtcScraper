from src.db.actions.actions_General import executeReadQuery

def getLatestProcessedBlockNetworkIdAndDexId(networkDbId, dexDbId):

    query = f"SELECT block_number " \
        f"FROM routes " \
        f"WHERE network_id='{networkDbId}' AND " \
        f"dex_id='{dexDbId}' " \
        f"ORDER BY block_number ASC " \
        f"LIMIT 1"

    result = executeReadQuery(
        query=query
    )

    if result:
        return int(result[0]["block_number"])
    else:
        return None

def getFirstProcessedBlockNetworkIdAndDexId(networkDbId, dexDbId):

    query = f"SELECT block_number " \
        f"FROM routes " \
        f"WHERE network_id='{networkDbId}' AND " \
        f"dex_id='{dexDbId}' " \
        f"ORDER BY block_number DESC " \
        f"LIMIT 1"

    result = executeReadQuery(
        query=query
    )

    if result:
        return result[0]
    else:
        return None