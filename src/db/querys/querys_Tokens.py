import json
from functools import lru_cache

from web3 import Web3

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor, initDBConnection
from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import getProjectLogger, printLog
from src.utils.sql.sql_Files import executeScriptsFromFile

logger = getProjectLogger()

@lru_cache()
def getTokenByNetworkIdAndTokenId(networkDbId, tokenDbId):

    query = "" \
            f"SELECT * " \
            f"FROM tokens " \
            f"WHERE network_id='{networkDbId}' AND token_id='{tokenDbId}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        return sorted(result, key=lambda d: d['token_id'])[0]

@lru_cache()
def getTokenByNetworkIdAndAddress(networkDbId, tokenAddress):

    query = "" \
            f"SELECT * " \
            f"FROM tokens " \
            f"WHERE network_id='{networkDbId}' AND address='{tokenAddress}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Token Matches!")

@lru_cache()
def getTokenByNetworkIdAndSymbol(networkDbId, tokenSymbol):

    query = "" \
            f"SELECT * " \
            f"FROM tokens " \
            f"WHERE network_id='{networkDbId}' AND symbol='{tokenSymbol}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Token Matches!")

@lru_cache()
def getTokensWithMissingDecimals():

    tokensWithNoDecimal = executeScriptsFromFile(
        filename="tokens/getTokensWithNullDecimals.sql"
    )

    return tokensWithNoDecimal