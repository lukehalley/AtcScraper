from src.db.actions.actions_General import executeWriteQuery
from src.db.querys.querys_Tokens import getTokenByNetworkIdAndAddress
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()


def addRouteToDB(networkDbId, dexDbId, tokenInAddress, tokenOutAddress, route, method, transactionHash,
                 txTimestamp, blockNumber, amountIn, amountOut):

    keys = f"network_id, dex_id, token_in_id, token_in_address, token_out_id, token_out_address, route, method, transaction_hash, block_number, "

    tokenInDetails = getTokenByNetworkIdAndAddress(
        networkDbId=networkDbId,
        tokenAddress=tokenInAddress
    )

    tokenOutDetails = getTokenByNetworkIdAndAddress(
        networkDbId=networkDbId,
        tokenAddress=tokenOutAddress
    )

    transactionHash = transactionHash.hex()

    if tokenInDetails and tokenOutDetails:

        tokenInId = tokenInDetails["token_id"]
        tokenOutId = tokenOutDetails["token_id"]

        if tokenInId and tokenOutId:

            selectStatement = f"SELECT """ \
                              fr"""{networkDbId} AS network_id, """ \
                              fr"""{dexDbId} AS dex_id, """ \
                              fr"""{tokenInId} AS token_in_id, """ \
                              fr"""'{tokenInAddress}' AS token_in_address, """ \
                              fr"""{tokenOutId} AS token_out_id, """ \
                              fr"""'{tokenOutAddress}' AS token_out_address, """ \
                              fr"""'{route}' AS route, """ \
                              fr"""'{method}' AS method, """ \
                              fr"""'{transactionHash}' AS transaction_hash, """ \
                              fr"""{blockNumber} AS block_number, """

            compareStatement = f"network_id = {networkDbId} AND " \
                               f"dex_id = {dexDbId} AND " \
                               f"token_in_id = '{tokenInId}' AND " \
                               f"token_in_address = '{tokenInAddress}' AND " \
                               f"token_out_id = '{tokenOutId}' AND " \
                               f"token_out_address = '{tokenOutAddress}' AND " \
                               f"route = '{route}' AND " \
                               f"method = '{method}' AND " \
                               f"transaction_hash = '{transactionHash}' AND " \
                               f"block_number = {blockNumber} AND "

            if amountIn:
                selectStatement = selectStatement + f"{amountIn} AS amount_in, "
                compareStatement = compareStatement + f"amount_in = {amountIn} AND "
                keys = keys + "amount_in, "

            if amountOut:
                selectStatement = selectStatement + f"{amountOut} AS amount_out, "
                compareStatement = compareStatement + f"amount_out = {amountOut} AND "
                keys = keys + "amount_out, "

            selectStatement = selectStatement + f"'{txTimestamp}' AS tx_timestamp"
            compareStatement = compareStatement + f"tx_timestamp = {txTimestamp}"
            keys = keys + " tx_timestamp"

            query = f"INSERT INTO routes ({keys}) " \
                    f"SELECT * FROM ({selectStatement}) AS tmp " \
                    f"WHERE NOT EXISTS " \
                    f"(SELECT * FROM routes WHERE {compareStatement}) " \
                    f"LIMIT 1"

            lastRowID = executeWriteQuery(
                query=query
            )

            return lastRowID
