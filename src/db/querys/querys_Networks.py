from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery

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

def getNetworkRPCByDbId(dbConnection, networkDbId):

    query = f"SELECT networks.chain_rpc " \
            f"FROM networks " \
            f"WHERE networks.network_id = '{networkDbId}'"

    cursor = getCursor(dbConnection=dbConnection)

    result = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return result[0]["chain_rpc"]


