from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery

def getAllNetworks(dbConnection):

    query = "" \
            f"SELECT name " \
            f"FROM networks"

    cursor = getCursor(dbConnection=dbConnection)

    allNetworksDict = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return [networkName['name'] for networkName in allNetworksDict]

def getNetworkDbIdByName(dbConnection, networkName):
    query = "" \
            f"SELECT network_id " \
            f"FROM networks " \
            f"WHERE name='{networkName}'"

    cursor = getCursor(dbConnection=dbConnection)

    return executeReadQuery(
        cursor=cursor,
        query=query
    )


