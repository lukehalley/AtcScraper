from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def addNetworkToDB(dbConnection, networkName):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT INTO networks (name) " \
            f"VALUES ('{networkName}')"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

async def addDexToDB(dbConnection, networkDbId, dexName):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT INTO dexs (network_id, name) " \
            f"VALUES ('{networkDbId}', '{dexName}')"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

async def addTokenToDB(dbConnection, networkDbId, dexDbId, tokenName, tokenSymbol, tokenAddress=None):

    cursor = getCursor(dbConnection=dbConnection)

    networkDbId = int(networkDbId)
    dexDbId = int(dexDbId)
    tokenName = tokenName
    tokenSymbol = tokenSymbol
    tokenAddress = tokenAddress

    keys = f"(network_id, dex_id, name, symbol, address)"
    selectStatement = f"(SELECT {networkDbId} AS network_id, {dexDbId} AS dex_id, '{tokenName}' AS name, '{tokenSymbol}' AS symbol, '{tokenAddress}' AS address)"
    compareStatement = f"tokens.symbol = '{tokenSymbol}' AND tokens.network_id = {networkDbId} AND tokens.dex_id = {dexDbId}"

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

async def addTokenPairToDB(dbConnection, networkDbId, dexDbId, primaryTokenDbId, secondaryTokenDbId, pairName, pairAddress, dexRanking, dexPrice, pairLiquidity, pairVolume, pairFdv):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT INTO pairs " \
            f"(primary_token_id, secondary_token_id, network_id, dex_id, name, address, ranking, price, liquidity, volume, fdv) " \
            f"VALUES " \
            f"('{networkDbId}', '{dexDbId}', '{primaryTokenDbId}', '{secondaryTokenDbId}', " \
            f"'{pairName}', '{pairAddress}', '{dexRanking}', '{dexPrice}', '{pairLiquidity}', '{pairVolume}', '{pairFdv}'" \
            f")"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

