from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery

def getTokensForChainWithNoAddress(dbConnection, networkDbId):

    query = "" \
            f"SELECT symbol " \
            f"FROM tokens " \
            f"WHERE address='None' AND network_id={networkDbId}"

    cursor = getCursor(dbConnection=dbConnection)

    queryResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    allTokensWithNoAddress = [token['symbol'] for token in queryResults]

    return allTokensWithNoAddress

