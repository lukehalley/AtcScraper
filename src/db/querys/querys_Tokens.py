import json

from web3 import Web3

from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.sql.sql_Files import executeScriptsFromFile

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor


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

def fillTokenDecimals(dbConnection):

    cursor = getCursor(dbConnection=dbConnection)

    tokensWithNoDecimal = executeScriptsFromFile(
        cursor=cursor,
        filename="tokens/getTokensWithNullDecimals.sql"
    )

    amountOfTokens = len(tokensWithNoDecimal)

    # Reading from file
    ERC20_abi = json.loads(open('src/abis/ERC20.json', "r").read())

    for token in tokensWithNoDecimal:

        networkName = (token["name"]).title()
        networkRPC = token["chain_rpc"]

        tokenIndex = tokensWithNoDecimal.index(token) + 1
        tokenCount = f"[{tokenIndex}/{amountOfTokens}]"
        tokenDbId = token["token_id"]
        tokenSymbol = token["symbol"]
        tokenAddress = token["address"]

        web3 = Web3(Web3.HTTPProvider(networkRPC))

        tokenDecimals = None

        try:
            token_info = web3.eth.contract(web3.toChecksumAddress(tokenAddress), abi=ERC20_abi)
            tokenDecimals = int(token_info.functions.decimals().call())
        except:
            logger.info(f"{tokenCount} {tokenSymbol} On {networkName} ⛔️")

        if tokenDecimals:

            updateTokenByDbId(
                dbConnection=dbConnection,
                tokenDbId=tokenDbId,
                fieldToUpdate="decimals",
                fieldNewValue=tokenDecimals
            )

            logger.info(f"{tokenCount} {tokenSymbol} On {networkName} [{tokenDecimals}] ✅")
