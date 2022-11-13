import json

from web3 import Web3

from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import printLog


def fillPairAddresses(pairDetails):

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