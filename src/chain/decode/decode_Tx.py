import json
import logging

from web3 import Web3
from web3.middleware import geth_poa_middleware

from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex
from src.db.actions.actions_Routes import addRouteToDB
from src.db.actions.actions_Tokens import updatePairAnalysisByDbId
from src.db.actions.actions_Transactions import addTransactionToDB, deleteTransactionToDB
from src.db.querys.querys_Dexs import getDexByDbId
from src.db.querys.querys_Networks import getNetworkByDbId
from src.db.querys.querys_Pairs import getPairByDbId
from src.utils.data.data_ABI import loadLocalABI
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import printLog, getProjectLogger

logger = getProjectLogger()

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

    if transactionDbId and transactionDbId > 0:

        printLog(f"Added {transactionHash} To DB")

        return transactionDbId

    else:

        return None

def decodeTx(transactionDetails):

    printLog(f"1. DECODING TRANSACTION: {transactionDetails}")
    try:

        pairDetails = getPairByDbId(
            pairDbId=transactionDetails["pair_id"]
        )

        printLog(f"2. PAIR DETAILS: {pairDetails}")

        networkDetails = getNetworkByDbId(
            networkDbId=transactionDetails["network_id"]
        )

        printLog(f"3. NETWORK DETAILS: {networkDetails}")

        dexDetails = getDexByDbId(
            dexDbId=transactionDetails["dex_id"]
        )

        printLog(f"4. DEX DETAILS: {dexDetails}")

        routerAbi = loadLocalABI(
            path=dexDetails["router_s3_path"]
        )

        printLog(f"5. GOT ROUTER ABI")

        ###############################################
        # Pair Details
        ###############################################
        # Pair
        pairDbId = pairDetails["pair_id"]
        pairName = pairDetails["name"]

        printLog(f"6. PAIR VARS: pairName: {pairDbId} pairName: {pairName}")

        # Token
        tokenInDbId = pairDetails["primary_token_id"]
        tokenOutDbId = pairDetails["secondary_token_id"]

        printLog(f"7. TOKEN VARS: tokenInDbId: {tokenInDbId} tokenOutDbId: {tokenOutDbId}")

        # Network
        networkDbId = networkDetails["network_id"]
        rpcUrl = networkDetails["chain_rpc"]

        printLog(f"8. NETWORK VARS: networkDbId: {networkDbId} rpcUrl: {rpcUrl}")

        # Dex
        dexDbId = dexDetails["dex_id"]

        # Router
        routerAddress = dexDetails["router"].replace("\r", "")

        printLog(f"9. DEX VARS: dexDbId: {dexDbId} routerAddress: {routerAddress}")

        ###############################################
        # Tx Details
        ###############################################
        transactionHash = transactionDetails["transaction_hash"]

        printLog(f"10. transactionHash: {transactionHash}")

        routeId = None

        printLog(f"11. In Try")
        web3 = Web3(Web3.HTTPProvider(rpcUrl))
        printLog(f"12. Got Web 3")
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        printLog(f"13. Added Middleware")
        transaction = web3.eth.get_transaction(transactionHash)
        printLog(f"14. Got Transaction")
        if transaction["to"] == routerAddress:

            printLog(f"15. Transaction To Matches Router Address")
            inputData = transaction["input"]
            printLog(f"16. Got Input Data")
            blockNumber = int(transaction["blockNumber"])
            printLog(f"17. Got Block Number")
            (contract, routerAbi) = getContract(routerAddress, json.dumps(routerAbi))
            printLog(f"18. Got Router Contract")
            func_obj, func_params = contract.decode_function_input(inputData)
            printLog(f"19. DECODED CONTRACT!")
            target_schema = [a['inputs'] for a in routerAbi if 'name' in a and a['name'] == func_obj.fn_name][0]
            printLog(f"20. Got Schema")
            decoded_func_params = convertToHex(func_params, target_schema)
            printLog(f"21. Decoded Params")
            timestamp = web3.eth.getBlock(blockNumber).timestamp
            printLog(f"22. Got Timestamp")
            decodedTransaction = {
                "name": func_obj.fn_name,
                "params": decoded_func_params,
                "schema": target_schema,
                "blockNumber": blockNumber,
                "txHash": transaction["hash"],
                "timestamp": timestamp
            }
            printLog(f"23. Created decodedTransaction Object {decodedTransaction}")
            routeUsed = decodedTransaction["params"]["path"]
            printLog(f"24. Got Route Used")
            tokenInAddress = routeUsed[0]
            printLog(f"25. tokenInAddress {tokenInAddress}")
            tokenOutAddress = routeUsed[-1]
            printLog(f"26. tokenOutAddress {tokenOutAddress}")
            isLoopRoute = tokenInAddress == tokenOutAddress
            printLog(f"27. isLoopRoute {isLoopRoute}")
            if not isLoopRoute:
                printLog(f"28. Not Loop Route")
                routeObject = {
                    "method": decodedTransaction["name"],
                    "route": "-".join(routeUsed),
                    "blockNumber": decodedTransaction["blockNumber"]
                }
                printLog(f"29. routeObject {routeObject}")
                if "amountIn" in decodedTransaction["params"]:
                    routeObject["amountIn"] = decodedTransaction["params"]["amountIn"]
                else:
                    routeObject["amountIn"] = None
                printLog(f"30. Added amountIn {routeObject['amountIn']}")
                if "amountOutMin" in decodedTransaction["params"]:
                    routeObject["amountOutMin"] = decodedTransaction["params"]["amountOutMin"]
                else:
                    routeObject["amountOutMin"] = None
                printLog(f"31. Added amountOutMin {routeObject['amountOutMin']}")

                printLog(f"32. Executing addRouteToDB...")
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
                printLog(f"33. Executed addRouteToDB!")

                if routeId is not None and routeId > 0:

                    printLog(f"34. Route Added To DB {routeObject} - routeId: {routeId}")

                    printLog(
                        msg=f"Added Route For {pairName} ✅"
                    )

                    printLog(f"35. Updating Pair Analysis...")
                    updatePairAnalysisByDbId(
                        pairDbId=pairDbId,
                        analysisStatus=True
                    )
                    printLog(f"36. Updated Pair Analysis!")

        return routeId

    except Exception as e:
        printLog(f"Route Error: {e}")
        pass
        return None

    # printLog(f"37. Deleting Transaction!")
    # deleteTransactionToDB(
    #     transactionDbId=transactionDetails["transaction_id"]
    # )

