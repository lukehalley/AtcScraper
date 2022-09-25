from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery

def clearPairsRankingTable(dbConnection):

    query = "DELETE FROM pair_market_data"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


