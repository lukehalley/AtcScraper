import sys

from src.db.actions.actions_Setup import getCursor, initDBConnection
from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Tokens import updateTokenByDbId, updatePairAnalysisByDbId
from src.dexScreener.dexScreener_Querys import getPairs
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.sql.sql_Files import executeScriptsFromFile

logger = getProjectLogger()


def getPairForAddressAndNetworkId(dbConnection, pairAddress, networkDbId):
    compareStatement = f"pairs.address = '{pairAddress}' AND pairs.network_id = {networkDbId}"

    query = f"SELECT * FROM pairs WHERE {compareStatement}"

    cursor = getCursor(dbConnection=dbConnection)

    pairResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    pairResultsLen = len(pairResults)

    if pairResultsLen > 1:
        sys.exit(f"More Than One Pair Found With Same Address ({pairAddress}) and Network DB Id ({networkDbId})")
    if pairResultsLen == 1:
        return pairResults[0]
    else:
        return None

def getPairsWithNullTokenAddresses():

    # Init MySQL DB
    dbConnection = initDBConnection()

    cursor = getCursor(dbConnection=dbConnection)

    dbPairs = executeScriptsFromFile(
        cursor=cursor,
        filename="pairs/getPairsWithNullTokenAddresses.sql"
    )

    return dbPairs

def fillNullTokenAddresses(dbPair):

    # Init MySQL DB
    dbConnection = initDBConnection()

    pairDbId = dbPair["pair_db_id"]
    tokenFilled = False

    try:

        pairInfo = getPairs(chain=dbPair["network_name"], pairAddress=dbPair["pair_address"])

        if pairInfo["pair"]:

            pairObject = pairInfo["pair"]

            primaryTokenIsNull = dbPair["primary_token_address"] is None
            secondaryTokenIsNull = dbPair["secondary_token_address"] is None

            if primaryTokenIsNull:
                updateTokenByDbId(
                    dbConnection=dbConnection,
                    tokenDbId=dbPair["primary_token_db_id"],
                    fieldToUpdate="address",
                    fieldNewValue=pairObject["quoteToken"]["address"]
                )

                updateTokenByDbId(
                    dbConnection=dbConnection,
                    tokenDbId=dbPair["primary_token_db_id"],
                    fieldToUpdate="name",
                    fieldNewValue=pairObject["quoteToken"]["name"]
                )

                logger.info("  Primary Token ✅")

                tokenFilled = True

            if secondaryTokenIsNull:
                updateTokenByDbId(
                    dbConnection=dbConnection,
                    tokenDbId=dbPair["secondary_token_db_id"],
                    fieldToUpdate="address",
                    fieldNewValue=pairObject["quoteToken"]["address"]
                )

                updateTokenByDbId(
                    dbConnection=dbConnection,
                    tokenDbId=dbPair["secondary_token_db_id"],
                    fieldToUpdate="name",
                    fieldNewValue=pairObject["quoteToken"]["name"]
                )

                logger.info("  Secondary Token ✅")

                tokenFilled = True

        else:

            tokenFilled = False
            logger.info("  Pair Info Unavailable ⚠️")

    except:
        tokenFilled = False
        logger.info("  API Request Failed ⛔️")

    updatePairAnalysisByDbId(
        dbConnection=dbConnection,
        pairDbId=pairDbId,
        analysisStatus=True
    )

    if tokenFilled:
        return True
    else:
        return None

def getAnalysedPairs(dbConnection):

    query = f"SELECT pairs.pair_id FROM pairs WHERE pairs.analysed"

    cursor = getCursor(dbConnection=dbConnection)

    analysedPairs = executeReadQuery(
        cursor=cursor,
        query=query
    )

    analysedPairIds = [analysedPair['pair_id'] for analysedPair in analysedPairs]

    return analysedPairIds