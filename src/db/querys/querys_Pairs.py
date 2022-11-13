import json
import sys
from functools import lru_cache

from web3 import Web3

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import getProjectLogger, printLog
from src.utils.sql.sql_Files import executeScriptsFromFile

logger = getProjectLogger()

@lru_cache()
def getPairByDbId(pairDbId):

    query = f"SELECT pairs.* " \
            f"FROM pairs " \
            f"WHERE pairs.pair_id = '{pairDbId}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Pair Matches!")

@lru_cache()
def getPairForNetworkIdAndPairDbId(networkDbId, pairDbId):
    compareStatement = f"pairs.pair_id = '{pairDbId}' AND pairs.network_id = {networkDbId}"

    query = f"SELECT * FROM pairs WHERE {compareStatement}"

    pairResults = executeReadQuery(
        query=query
    )

    pairResultsLen = len(pairResults)

    if pairResultsLen > 1:
        logger.error(f"More Than One Pair Found With Same Id ({pairDbId}) and Network DB Id ({networkDbId})")
    if pairResultsLen == 1:
        return pairResults[0]
    else:
        return None

@lru_cache()
def getPairForAddressAndNetworkId(pairAddress, networkDbId):
    compareStatement = f"pairs.address = '{pairAddress}' AND pairs.network_id = {networkDbId}"

    query = f"SELECT * FROM pairs WHERE {compareStatement}"

    pairResults = executeReadQuery(
        query=query
    )

    pairResultsLen = len(pairResults)

    if pairResultsLen > 1:
        sys.exit(f"More Than One Pair Found With Same Address ({pairAddress}) and Network DB Id ({networkDbId})")
    if pairResultsLen == 1:
        return pairResults[0]
    else:
        return None

@lru_cache()
def getPairsWithNullTokenAddresses():

    dbPairs = executeScriptsFromFile(
        filename="pairs/getPairsWithNullTokenAddresses.sql"
    )

    return dbPairs

@lru_cache()
def getAnalysedPairs():

    query = f"SELECT pairs.pair_id FROM pairs WHERE pairs.analysed"

    analysedPairs = executeReadQuery(
        query=query
    )

    analysedPairIds = [analysedPair['pair_id'] for analysedPair in analysedPairs]

    return analysedPairIds