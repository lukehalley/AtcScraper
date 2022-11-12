import json

from web3 import Web3
from web3.middleware import geth_poa_middleware

from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex
from src.db.actions.actions_Routes import addRouteToDB
from src.db.actions.actions_Tokens import updatePairAnalysisByDbId
from src.db.actions.actions_Transactions import addTransactionToDB
from src.utils.logging.logging_Setup import printLog

def uploadTx(transactionDetails):

    ###############################################
    # Pair Details
    ###############################################
    pairDetails = transactionDetails["pairDetails"]

    # Metadata ####################################
    # Pair
    pairDbId = pairDetails["pair"]["pair_id"]

    # Block
    blockNumber = transactionDetails["blockNumber"]
    blockTimestamp = transactionDetails["blockTimestamp"]

    # Token
    tokenInDbId = pairDetails["primaryToken"]["token_id"]
    tokenOutDbId = pairDetails["secondaryToken"]["token_id"]

    # Network
    networkDbId = pairDetails["network"]["db"]["dbId"]

    # Dex
    dexDbId = pairDetails["dex"]["db"]["dbId"]

    ###############################################
    # Tx Details
    ###############################################
    transactionHash = transactionDetails["txnHash"]

    transactionDbId = addTransactionToDB(
        networkDbId=networkDbId,
        dexDbId=dexDbId,
        pairDbId=pairDbId,
        tokenInDbId=tokenInDbId,
        tokenOutDbId=tokenOutDbId,
        transactionHash=transactionHash,
        blockNumber=blockNumber,
        blockTimestamp=blockTimestamp
    )

    if transactionDbId:

        printLog(f"Added {transactionHash} To DB")

        return transactionDbId

    else:

        return None

def decodeTx(transactionDetails):

    ###############################################
    # Pair Details
    ###############################################
    pairDetails = transactionDetails["pairDetails"]

    # Metadata ####################################
    # Pair
    pairDbId = pairDetails["pair"]["pair_id"]
    pairName = pairDetails["pair"]["name"]

    # Token
    tokenInDbId = pairDetails["primaryToken"]["token_id"]
    tokenOutDbId = pairDetails["secondaryToken"]["token_id"]

    # Network
    networkDbId = pairDetails["network"]["db"]["dbId"]
    networkName = pairDetails["network"]["network"]
    rpcUrl = pairDetails["network"]["rpcUrl"]

    # Dex
    dexName = pairDetails["dex"]["dex"]["name"]
    dexDbId = pairDetails["dex"]["db"]["dbId"]

    # Router
    routerAddress = pairDetails["dex"]["dex"]["abi"]["router"]
    routerAbi = pairDetails["dex"]["dex"]["abi"]["router_abi"]

    ###############################################
    # Tx Details
    ###############################################
    transactionHash = transactionDetails["txnHash"]

    try:

        web3 = Web3(Web3.HTTPProvider(rpcUrl))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        transaction = web3.eth.get_transaction(transactionHash)

        if transaction["to"] == routerAddress:

            inputData = transaction["input"]
            blockNumber = int(transaction["blockNumber"])

            (contract, routerAbi) = getContract(routerAddress, json.dumps(routerAbi))
            func_obj, func_params = contract.decode_function_input(inputData)
            target_schema = [a['inputs'] for a in routerAbi if 'name' in a and a['name'] == func_obj.fn_name][0]
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
                    pairDbId=pairDbId,
                    tokenInDbId=tokenInDbId,
                    tokenInAddress=tokenInAddress,
                    tokenOutDbId=tokenOutDbId,
                    tokenOutAddress=tokenOutAddress,
                    route=routeObject["route"],
                    method=routeObject["method"],
                    transactionHash=decodedTransaction["txHash"],
                    txTimestamp=decodedTransaction["timestamp"],
                    blockNumber=decodedTransaction["blockNumber"],
                    amountIn=routeObject["amountIn"],
                    amountOut=routeObject["amountOutMin"]
                )

                toReturn = None

                if routeId:
                    toReturn = routeObject

                    printLog(
                        msg=f"Added Route For {pairName} ✅"
                    )

                updatePairAnalysisByDbId(
                    pairDbId=pairDbId,
                    analysisStatus=True
                )

                return toReturn

        else:
            return None
    except:
        return None