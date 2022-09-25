import re

from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery
from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId
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

async def addPairRankToDB(dbConnection, cursor, pairDbId, networkDbId, dexDbId, pairRanking, pairLiquidity, pairVolume, pairFdv):

    keys = f"pair_id, network_id, dex_id, ranking, liquidity, volume, fdv"

    selectStatement = f"SELECT " \
                      f"{pairDbId} AS pair_id, " \
                      f"{networkDbId} AS network_id, " \
                      f"{dexDbId} AS dex_id, " \
                      f"{pairRanking} AS ranking, " \
                      f"{pairLiquidity} AS liquidity, " \
                      f"{pairVolume} AS volume, " \
                      f"{pairFdv} AS fdv"

    compareStatement = f"pair_market_data.pair_id = '{pairDbId}' AND pair_market_data.network_id = '{networkDbId}' AND pair_market_data.dex_id = '{dexDbId}'"

    query = f"INSERT INTO pair_market_data({keys}) " \
            f"SELECT * FROM ({selectStatement}) AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM pair_market_data WHERE {compareStatement}) " \
            f"LIMIT 1"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

async def addTokenPairToDB(dbConnection, networkDbId, dexDbId, primaryTokenDbId, secondaryTokenDbId, pairName, pairAddress, pairRanking, pairLiquidity, pairVolume, pairFdv):

    # DB Ids
    primaryTokenDbId = int(primaryTokenDbId)
    secondaryTokenDbId = int(secondaryTokenDbId)
    networkDbId = int(networkDbId)
    dexDbId = int(dexDbId)

    # Strings
    pairName = str(pairName)
    pairAddress = str(pairAddress)

    # DexScreener Metadata
    pairRanking = int(pairRanking)

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

    keys = f"primary_token_id, secondary_token_id, network_id, dex_id, name, address"

    selectStatement = f"SELECT " \
                      f"{primaryTokenDbId} AS primary_token_id, " \
                      f"{secondaryTokenDbId} AS secondary_token_id, " \
                      f"{networkDbId} AS network_id, " \
                      f"{dexDbId} AS dex_id, " \
                      f"'{pairName}' AS name, " \
                      f"'{pairAddress}' AS address"

    compareStatement = f"pairs.address = '{pairAddress}' AND pairs.network_id = {networkDbId}"

    existingPairDetails = getPairForAddressAndNetworkId(
        dbConnection=dbConnection,
        pairAddress=pairAddress,
        networkDbId=networkDbId
    )

    if not existingPairDetails:

        query = f"INSERT INTO pairs({keys}) " \
                f"SELECT * FROM ({selectStatement}) AS tmp " \
                f"WHERE NOT EXISTS " \
                f"(SELECT * FROM pairs WHERE {compareStatement}) " \
                f"LIMIT 1"

        executeWriteQuery(
            dbConnection=dbConnection,
            cursor=cursor,
            query=query
        )

        pairDbId = cursor.lastrowid

    else:

        pairDbId = existingPairDetails["pair_id"]

    await addPairRankToDB(
        dbConnection=dbConnection,
        cursor=cursor,
        pairDbId=pairDbId,
        networkDbId=networkDbId,
        dexDbId=dexDbId,
        pairRanking=pairRanking,
        pairLiquidity=pairLiquidity,
        pairVolume=pairVolume,
        pairFdv=pairFdv,
    )

