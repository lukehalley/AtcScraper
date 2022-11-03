from src.db.actions.actions_General import executeReadQuery

def getNetworkById(networkDbId):
    query = "" \
            f"SELECT * " \
            f"FROM networks " \
            f"WHERE network_id='{networkDbId}'"

    result = executeReadQuery(
        query=query
    )[0]

    return result

def getNetworkByName(networkName):
    query = "" \
            f"SELECT * " \
            f"FROM networks " \
            f"WHERE name='{networkName}'"

    result = executeReadQuery(
        query=query
    )[0]

    return result

