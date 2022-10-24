from src.chain.decode.decode_Tx import decodeTx
from src.db.actions.actions_Routes import addRouteToDB
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def decodeTransactions(dbConnection, networkName, networkDbId, dexName, dexDbId, dexTransactions, dexRouterAddress, dexRouterABI):

    dexTransactionCount = len(dexTransactions)

    # Create the dict of decode tasks
    decodedTransactions = [decodeTx(address=dexRouterAddress, transaction=transaction, abi=dexRouterABI) for transaction
                           in dexTransactions]

    # Filter out the invalid results
    finalDecodedTransactions = [decodedTransaction for decodedTransaction in decodedTransactions if
                                isinstance(decodedTransaction, dict) and "path" in decodedTransaction["params"]]

    collectedRoutes = {}

    for finalDecodedTransaction in finalDecodedTransactions:

        transactionIndex = finalDecodedTransactions.index(finalDecodedTransaction)

        routeUsed = finalDecodedTransaction["params"]["path"]

        tokenInAddress = routeUsed[0]
        tokenOutAddress = routeUsed[-1]

        routeName = f"{tokenInAddress}-{tokenOutAddress}"

        isLoopRoute = tokenInAddress == tokenOutAddress

        if not isLoopRoute:

            if routeName not in collectedRoutes:
                collectedRoutes[routeName] = []

            routeObject = {
                "method": finalDecodedTransaction["name"],
                "route": "-".join(routeUsed),
                "blockNumber": finalDecodedTransaction["blockNumber"]
            }

            if "amountIn" in finalDecodedTransaction["params"]:
                routeObject["amountIn"] = finalDecodedTransaction["params"]["amountIn"]
            else:
                routeObject["amountIn"] = None

            if "amountOutMin" in finalDecodedTransaction["params"]:
                routeObject["amountOutMin"] = finalDecodedTransaction["params"]["amountOutMin"]
            else:
                routeObject["amountOutMin"] = None

            if routeObject not in collectedRoutes[routeName]:
                collectedRoutes[routeName].append(routeObject)

            addRouteToDB(
                dbConnection=dbConnection,
                networkDbId=networkDbId,
                dexDbId=dexDbId,
                tokenInAddress=tokenInAddress,
                tokenOutAddress=tokenOutAddress,
                route=routeObject["route"],
                method=routeObject["method"],
                transactionHash=finalDecodedTransaction["txHash"],
                txTimestamp=finalDecodedTransaction["timestamp"],
                blockNumber=finalDecodedTransaction["blockNumber"],
                amountIn=routeObject["amountIn"],
                amountOut=routeObject["amountOutMin"]
            )

            logger.info(f"{dexName} {transactionIndex + 1}/{dexTransactionCount}")

    printSeparator(True)