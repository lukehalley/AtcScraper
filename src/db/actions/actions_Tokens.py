import re

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.data.data_Clean import cleanString


async def addTokenToDB(dbConnection, networkDbId, tokenName, tokenSymbol, tokenAddress=None):

    cursor = getCursor(dbConnection=dbConnection)

    networkDbId = int(networkDbId)
    tokenName = cleanString(re.sub('[^A-Za-z0-9 ]+', '', str(tokenName)))
    tokenSymbol = cleanString(tokenSymbol)
    tokenAddress = cleanString(tokenAddress)

    keys = f"(network_id, name, symbol, address)"
    selectStatement = f"(SELECT {networkDbId} AS network_id, '{tokenName}' AS name, '{tokenSymbol}' AS symbol, '{tokenAddress}' AS address)"
    compareStatement = f"tokens.symbol = '{tokenSymbol}' AND tokens.network_id = {networkDbId}"

    query = f"INSERT INTO tokens{keys} " \
            f"SELECT * FROM {selectStatement} AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM tokens WHERE {compareStatement}) " \
            f"LIMIT 1"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

def updateTokenByDbId(dbConnection, tokenDbId, fieldToUpdate, fieldNewValue):

    query = "" \
            f"UPDATE tokens " \
            f"SET {cleanString(fieldToUpdate)}='{cleanString(fieldNewValue)}' " \
            f"WHERE token_id={tokenDbId}"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def updateUnavailableTokensToNull(dbConnection):

    query = "" \
            f"UPDATE tokens " \
            f"SET address = NULL " \
            f"WHERE address = 'None'"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )