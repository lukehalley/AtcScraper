from src.db.actions.actions_General import executeReadQuery

def getAllNetworks():

    query = "" \
            f"SELECT name " \
            f"FROM networks"

    allNetworksDict = executeReadQuery(
        query=query
    )

    return [networkName['name'] for networkName in allNetworksDict]

def getNetworkDbIdByName(networkName):
    query = "" \
            f"SELECT network_id " \
            f"FROM networks " \
            f"WHERE name='{networkName}'"

    return executeReadQuery(
        query=query
    )

def getNetworkRPCByDbId(networkDbId):

    query = f"SELECT networks.chain_rpc " \
            f"FROM networks " \
            f"WHERE networks.network_id = '{networkDbId}'"

    result = executeReadQuery(
        query=query
    )

    if result:

        return result[0]["chain_rpc"]

    else:

        return None


