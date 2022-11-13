import json

from web3 import Web3

from src.db.actions.actions_Tokens import updateTokenByDbId
from src.utils.logging.logging_Setup import printLog

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

        printLog(
            msg=f'Token: {tokenAddress} Decimals Added ✅'
        )

        return True
    else:
        return None
