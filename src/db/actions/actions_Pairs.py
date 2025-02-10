from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeWriteQuery
from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId


async def addTokenPairToDB(dbConnection, networkDbId, dexDbId, primaryTokenDbId, secondaryTokenDbId, pairName, pairAddress, pairRanking, pairLiquidity, pairVolume, pairFdv):
    """
    Add a token pair to the database or retrieve existing pair ID.
    
    This function handles the insertion of a new token pair into the database,
    including validation and type conversion of input parameters. If the pair
    already exists, it retrieves the existing pair ID instead of creating a duplicate.
    
    Args:
        dbConnection: Active database connection object
        networkDbId: Database ID of the network
        dexDbId: Database ID of the decentralized exchange
        primaryTokenDbId: Database ID of the primary token in the pair
        secondaryTokenDbId: Database ID of the secondary token in the pair
        pairName: Human-readable name of the trading pair
        pairAddress: Blockchain address of the pair contract
        pairRanking: Ranking position from DexScreener
        pairLiquidity: Liquidity value in USD
        pairVolume: Trading volume in USD
        pairFdv: Fully diluted valuation
    
    Returns:
        None (implicitly calls addPairRankToDB to store market data)
    """

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
    except (ValueError, TypeError):
        pairLiquidity = 0

    try:
        pairVolume = int(pairVolume)
    except (ValueError, TypeError):
        pairVolume = 0

    try:
        pairFdv = int(pairFdv)
    except (ValueError, TypeError):
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

def clearPairsRankingTable(dbConnection):

    query = "DELETE FROM pair_market_data"

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )
