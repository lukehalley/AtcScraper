from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery

def getNetworkById(dbConnection, networkDbId):
    query = "" \
            f"SELECT * " \
            f"FROM networks " \
            f"WHERE network_id='{networkDbId}'"

    cursor = getCursor(dbConnection=dbConnection)

    return executeReadQuery(
        cursor=cursor,
        query=query
    )[0]

