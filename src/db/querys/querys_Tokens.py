import json

from web3 import Web3

from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.sql.sql_Files import executeScriptsFromFile

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor, initDBConnection

logger = getProjectLogger()

def getTokenByNetworkIdAndAddress(dbConnection, networkDbId, tokenAddress):

    query = "" \
            f"SELECT * " \
            f"FROM tokens " \
            f"WHERE network_id='{networkDbId}' AND address='{tokenAddress}'"

    cursor = getCursor(dbConnection=dbConnection)

    result = executeReadQuery(
        cursor=cursor,
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        return sorted(result, key=lambda d: d['token_id'])[0]

def getTokensForChainWithNoAddress(dbConnection, networkDbId):

    query = "" \
            f"SELECT symbol " \
            f"FROM tokens " \
            f"WHERE address='None' AND network_id={networkDbId}"

    cursor = getCursor(dbConnection=dbConnection)

    queryResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    allTokensWithNoAddress = [token['symbol'] for token in queryResults]

    return allTokensWithNoAddress

def getTokensWithMissingDecimals():

    dbConnection = initDBConnection()

    cursor = getCursor(dbConnection=dbConnection)

    tokensWithNoDecimal = executeScriptsFromFile(
        cursor=cursor,
        filename="tokens/getTokensWithNullDecimals.sql"
    )

    return tokensWithNoDecimal

def fillTokenDecimals(token):

    dbConnection = initDBConnection()

    # Reading from file
    ERC20_abi = json.loads(open('src/abis/ERC20.json', "r").read())

    networkRPC = token["chain_rpc"]

    tokenDbId = token["token_id"]
    tokenAddress = token["address"]

    web3 = Web3(Web3.HTTPProvider(networkRPC))

    tokenDecimals = None

    try:
        token_info = web3.eth.contract(web3.toChecksumAddress(tokenAddress), abi=ERC20_abi)
        tokenDecimals = int(token_info.functions.decimals().call())
    except:
        pass

    if tokenDecimals:
        updateTokenByDbId(
            dbConnection=dbConnection,
            tokenDbId=tokenDbId,
            fieldToUpdate="decimals",
            fieldNewValue=tokenDecimals
        )

        return True
    else:
        return None
