from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery

def getAllDexsForNetwork(dbConnection, networkDbId):

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

