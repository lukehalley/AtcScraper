import json
import sys

from web3 import Web3

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Tokens import updateTokenByDbId, updatePairAnalysisByDbId
from src.dexScreener.dexScreener_Querys import getPairs
from src.utils.logging.logging_Setup import getProjectLogger, printLog
from src.utils.sql.sql_Files import executeScriptsFromFile

logger = getProjectLogger()


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

def getPairsWithNullTokenAddresses():

    dbPairs = executeScriptsFromFile(
        filename="pairs/getPairsWithNullTokenAddresses.sql"
    )

    return dbPairs

# def fillNullTokenAddresses(dbPair):
#
#     tokenFilled = False
#
#     try:
#
#         pairInfo = getPairs(chain=dbPair["network_name"], pairAddress=dbPair["pair_address"])
#
#         if pairInfo["pair"]:
#
#             pairObject = pairInfo["pair"]
#
#             primaryTokenIsNull = dbPair["primary_token_address"] is None
#             secondaryTokenIsNull = dbPair["secondary_token_address"] is None
#
#             if primaryTokenIsNull:
#                 updateTokenByDbId(
#                     tokenDbId=dbPair["primary_token_db_id"],
#                     fieldToUpdate="address",
#                     fieldNewValue=pairObject["quoteToken"]["address"]
#                 )
#
#                 updateTokenByDbId(
#                     tokenDbId=dbPair["primary_token_db_id"],
#                     fieldToUpdate="name",
#                     fieldNewValue=pairObject["quoteToken"]["name"]
#                 )
#
#                 printLog(
#                     msg=f'{dbPair["primary_token_symbol"]} Updated ✅'
#                 )
#
#                 tokenFilled = True
#
#             if secondaryTokenIsNull:
#                 updateTokenByDbId(
#                     tokenDbId=dbPair["secondary_token_db_id"],
#                     fieldToUpdate="address",
#                     fieldNewValue=pairObject["quoteToken"]["address"]
#                 )
#
#                 updateTokenByDbId(
#                     tokenDbId=dbPair["secondary_token_db_id"],
#                     fieldToUpdate="name",
#                     fieldNewValue=pairObject["quoteToken"]["name"]
#                 )
#
#                 printLog(
#                     msg=f'{dbPair["secondary_token_symbol"]} Updated ✅'
#                 )
#
#                 tokenFilled = True
#
#         else:
#
#             tokenFilled = False
#             printLog(
#                 msg=f'{dbPair["pair_name"]} Info Unavailable ⚠️'
#             )
#
#     except:
#         tokenFilled = False
#         printLog(
#             msg=f'{dbPair["pair_name"]} API Request Failed ⛔️'
#         )
#
#     if tokenFilled:
#         return True
#     else:
#         return None

def fillPairAddressesDecimals(pairDetails):

    IUniswapV2Pair_abi = json.loads(open('src/abis/IUniswapV2Pair.json', "r").read())["abi"]

    networkRPC = pairDetails["chain_rpc"]

    tokenAddress = pairDetails["pair_address"]

    web3 = Web3(Web3.HTTPProvider(networkRPC))

    try:

        pairContract = web3.eth.contract(web3.toChecksumAddress(tokenAddress), abi=IUniswapV2Pair_abi)

        primaryTokenAddress = pairContract.functions.token0().call()
        secondaryTokenAddress = pairContract.functions.token1().call()

        if primaryTokenAddress:
            updateTokenByDbId(
                tokenDbId=pairDetails["primary_token_db_id"],
                fieldToUpdate="address",
                fieldNewValue=primaryTokenAddress
            )

            printLog(
                msg=f'Pair: {primaryTokenAddress} Primary Token Updated ✅'
            )

        if secondaryTokenAddress:
            updateTokenByDbId(
                tokenDbId=pairDetails["secondary_token_db_id"],
                fieldToUpdate="address",
                fieldNewValue=secondaryTokenAddress
            )

            printLog(
                msg=f'Pair: {secondaryTokenAddress} Secondary Token Updated ✅'
            )

        if primaryTokenAddress or secondaryTokenAddress:
            tokenFilled = True
        else:
            tokenFilled = False
    except:
        tokenFilled = False
        pass

    if tokenFilled:
        return True
    else:
        return None

def getAnalysedPairs():

    query = f"SELECT pairs.pair_id FROM pairs WHERE pairs.analysed"

    analysedPairs = executeReadQuery(
        query=query
    )

    analysedPairIds = [analysedPair['pair_id'] for analysedPair in analysedPairs]

    return analysedPairIds