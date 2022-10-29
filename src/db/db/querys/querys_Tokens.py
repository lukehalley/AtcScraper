from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor


def getTokenByNetworkIdAndAddress(dbConnection, networkDbId, tokenAddress):

    query = "" \
            f"SELECT * " \
            f"FROM tokens " \
            f"WHERE network_id='{networkDbId}' AND address='{tokenAddress}'"

    cursor = getCursor(dbConnection=dbConnection)

    result = executeReadQuery(
        cursor=cursor,
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        return sorted(result, key=lambda d: d['token_id'])[0]