import re

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

    query = f"INSERT IGNORE INTO dexs (network_id, name) " \
            f"VALUES ('{networkDbId}', '{dexName}')"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

async def addTokenToDB(dbConnection, networkDbId, tokenName, tokenSymbol, tokenAddress=None):

    cursor = getCursor(dbConnection=dbConnection)

    networkDbId = int(networkDbId)
    tokenName = re.sub('[^A-Za-z0-9 ]+', '', str(tokenName))
    tokenSymbol = tokenSymbol
    tokenAddress = tokenAddress

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

async def addTokenPairToDB(dbConnection, networkDbId, dexDbId, primaryTokenDbId, secondaryTokenDbId, pairName, pairAddress, dexRanking, pairLiquidity, pairVolume, pairFdv):

    # DB Ids
    primaryTokenDbId = int(primaryTokenDbId)
    secondaryTokenDbId = int(secondaryTokenDbId)
    networkDbId = int(networkDbId)
    dexDbId = int(dexDbId)

    # Strings
    pairName = str(pairName)
    pairAddress = str(pairAddress)

    # DexScreener Metadata
    dexRanking = int(dexRanking)

    try:
        pairLiquidity = int(pairLiquidity)
    except:
        pairLiquidity = 0

    try:
        pairVolume = int(pairVolume)
    except:
        pairVolume = 0

    try:
        pairFdv = int(pairFdv)
    except:
        pairFdv = 0

    cursor = getCursor(dbConnection=dbConnection)

    keys = f"(primary_token_id, secondary_token_id, network_id, dex_id, name, address, ranking, liquidity, volume, fdv)"

    selectStatement = f"(SELECT " \
                      f"{primaryTokenDbId} AS primary_token_id, " \
                      f"{secondaryTokenDbId} AS secondary_token_id, " \
                      f"{networkDbId} AS network_id, " \
                      f"{dexDbId} AS dex_id, " \
                      f"'{pairName}' AS name, " \
                      f"'{pairAddress}' AS address, " \
                      f"{dexRanking} AS ranking, " \
                      f"{pairLiquidity} AS liquidity, " \
                      f"{pairVolume} AS volume, " \
                      f"{pairFdv} AS fdv)"

    compareStatement = f"pairs.address = '{pairAddress}' AND pairs.network_id = {networkDbId}"

    query = f"INSERT INTO pairs{keys} " \
            f"SELECT * FROM {selectStatement} AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM pairs WHERE {compareStatement}) " \
            f"LIMIT 1"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

