from src.db.actions.actions_General import executeReadQuery

def getAllDexsForNetwork(networkDbId):

    query = "" \
            f"SELECT name " \
            f"FROM dexs " \
            f"WHERE network_id={networkDbId}"

    allDexsDict = executeReadQuery(
        query=query
    )

    return [dexName['name'] for dexName in allDexsDict]

