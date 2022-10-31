import json
from web3.middleware import geth_poa_middleware
from web3 import Web3, HTTPProvider
from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex
from src.db.actions.actions_Routes import addRouteToDB
from src.db.actions.actions_Setup import initDBConnection


def decodeTx(transactionDetails):

    # Init MySQL DB
    dbConnection = initDBConnection()

    networkDbId = transactionDetails["networkDbId"]
    dexDbId = transactionDetails["dexDbId"]
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

                addRouteToDB(
                    dbConnection=dbConnection,
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
        else:
            return None
    except:
        return None