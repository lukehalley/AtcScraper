import sys

from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery

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


