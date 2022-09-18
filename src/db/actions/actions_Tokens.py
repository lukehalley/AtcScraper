from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery

def updateTokenByDbId(dbConnection, tokenDbId, fieldToUpdate, fieldNewValue):

    query = "" \
            f"UPDATE tokens " \
            f"SET {fieldToUpdate}='{fieldNewValue}' " \
            f"WHERE token_id={tokenDbId}"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def updateUnavailableTokens(dbConnection):

    query = "" \
            f"UPDATE tokens " \
            f"SET address = 'N/A' " \
            f"WHERE address = 'None'"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )