from web3 import Web3
from web3.middleware import geth_poa_middleware

from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex
from src.db.actions.actions_Routes import addRouteToDB
from src.db.actions.actions_Tokens import updatePairAnalysisByDbId
from src.utils.logging.logging_Setup import printLog


def decodeTx(transactionDetails):

    pairName = transactionDetails["pairDetails"]["pair"]["name"]
    networkName = transactionDetails["pairDetails"]["network"]["network"]
    dexName = transactionDetails["pairDetails"]["dex"]["dex"]["name"]

    networkDbId = transactionDetails["pairDetails"]["network"]["db"]["dbId"]
    dexDbId = transactionDetails["pairDetails"]["dex"]["db"]["dbId"]
    contractAddress = transactionDetails["contractAddress"]
    rpcUrl = transactionDetails["rpcUrl"]
    transactionHash = transactionDetails["transactionHash"]
    abi = transactionDetails["abi"]

    try:

        web3 = Web3(Web3.HTTPProvider(rpcUrl))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        transaction = web3.eth.get_transaction(transactionHash)

        if transaction["to"] == contractAddress:

            inputData = transaction["input"]
            blockNumber = int(transaction["blockNumber"])

            (contract, abi) = getContract(contractAddress, abi)
            func_obj, func_params = contract.decode_function_input(inputData)
            target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
            decoded_func_params = convertToHex(func_params, target_schema)

            timestamp = web3.eth.getBlock(blockNumber).timestamp

            decodedTransaction = {
                "name": func_obj.fn_name,
                "params": decoded_func_params,
                "schema": target_schema,
                "blockNumber": blockNumber,
                "txHash": transaction["hash"],
                "timestamp": timestamp
            }

            routeUsed = decodedTransaction["params"]["path"]

            tokenInAddress = routeUsed[0]
            tokenOutAddress = routeUsed[-1]

            isLoopRoute = tokenInAddress == tokenOutAddress

            if not isLoopRoute:

                routeObject = {
                    "method": decodedTransaction["name"],
                    "route": "-".join(routeUsed),
                    "blockNumber": decodedTransaction["blockNumber"]
                }

                if "amountIn" in decodedTransaction["params"]:
                    routeObject["amountIn"] = decodedTransaction["params"]["amountIn"]
                else:
                    routeObject["amountIn"] = None

                if "amountOutMin" in decodedTransaction["params"]:
                    routeObject["amountOutMin"] = decodedTransaction["params"]["amountOutMin"]
                else:
                    routeObject["amountOutMin"] = None

                routeId = addRouteToDB(
                    networkDbId=networkDbId,
                    dexDbId=dexDbId,
                    tokenInAddress=tokenInAddress,
                    tokenOutAddress=tokenOutAddress,
                    route=routeObject["route"],
                    method=routeObject["method"],
                    transactionHash=decodedTransaction["txHash"],
                    txTimestamp=decodedTransaction["timestamp"],
                    blockNumber=decodedTransaction["blockNumber"],
                    amountIn=routeObject["amountIn"],
                    amountOut=routeObject["amountOutMin"]
                )

                if routeId:

                    updatePairAnalysisByDbId(
                        pairDbId=transactionDetails["pairDetails"]["pair"]["db"]["dbId"],
                        analysisStatus=True
                    )

                    printLog(
                        msg=f'Added Route {pairName} On {dexName.title()} | {networkName.title()}'
                    )

                    return routeObject

                else:
                    printLog(
                        msg=f'Route Already Present {pairName} On {dexName.title()} | {networkName.title()}'
                    )

                    return None

        else:
            return None
    except:
        return None