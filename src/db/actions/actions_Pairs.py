from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery

def clearPairsTable(dbConnection):

    query = "DELETE FROM pairs"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


