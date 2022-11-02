import re

from src.db.actions.actions_General import executeWriteQuery
from src.utils.data.data_Clean import cleanString


def addTokenToDB(networkDbId, tokenName, tokenSymbol, tokenAddress=None):

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

    lastRowID = executeWriteQuery(
        query=query
    )

    return lastRowID

def updateTokenByDbId(tokenDbId, fieldToUpdate, fieldNewValue):

    isStr = isinstance(fieldNewValue, str)

    if isStr:
        insertValue = f"'{cleanString(fieldNewValue)}'"
    else:
        insertValue = fieldNewValue


    query = "" \
            f"UPDATE tokens " \
            f"SET {cleanString(fieldToUpdate)}={insertValue} " \
            f"WHERE token_id={tokenDbId}"

    return executeWriteQuery(
        query=query
    )

def updatePairAnalysisByDbId(pairDbId, analysisStatus):

    query = "" \
            f"UPDATE pairs " \
            f"SET analysed={analysisStatus} " \
            f"WHERE pair_id={pairDbId}"

    return executeWriteQuery(
        query=query
    )

def updateUnavailableTokensToNull():

    query = "" \
            f"UPDATE tokens " \
            f"SET address = NULL " \
            f"WHERE address = 'None'"

    return executeWriteQuery(
        query=query
    )