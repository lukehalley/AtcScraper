import json

from web3 import Web3

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor, initDBConnection
from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.sql.sql_Files import executeScriptsFromFile

logger = getProjectLogger()

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
        return sorted(result, key=lambda d: d['token_id'])[0]

def getTokensForChainWithNoAddress(networkDbId):

    query = "" \
            f"SELECT symbol " \
            f"FROM tokens " \
            f"WHERE address='None' AND network_id={networkDbId}"

    queryResults = executeReadQuery(
        query=query
    )

    allTokensWithNoAddress = [token['symbol'] for token in queryResults]

    return allTokensWithNoAddress

def getTokensWithMissingDecimals():

    tokensWithNoDecimal = executeScriptsFromFile(
        filename="tokens/getTokensWithNullDecimals.sql"
    )

    return tokensWithNoDecimal

def fillTokenDecimals(token):

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
            tokenDbId=tokenDbId,
            fieldToUpdate="decimals",
            fieldNewValue=tokenDecimals
        )

        return True
    else:
        return None
