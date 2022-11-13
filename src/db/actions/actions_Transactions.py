from src.db.actions.actions_General import executeWriteQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def addTransactionToDB(networkDbId, dexDbId, pairDbId, tokenInDbId, tokenOutDbId, transactionHash,
                 blockNumber, blockTimestamp):

    keys = f"network_id, dex_id, pair_id, token_in_id, token_out_id, transaction_hash, block_number, block_timestamp"

    selectStatement = f"SELECT """ \
                      fr"""{networkDbId} AS network_id, """ \
                      fr"""{dexDbId} AS dex_id, """ \
                      fr"""{pairDbId} AS pair_id, """ \
                      fr"""{tokenInDbId} AS token_in_id, """ \
                      fr"""{tokenOutDbId} AS token_out_id, """ \
                      fr"""'{transactionHash}' AS transaction_hash, """ \
                      fr"""{blockNumber} AS block_number, """ \
                      fr"""{blockTimestamp} AS block_timestamp"""

    compareStatement = f"network_id = {networkDbId} AND " \
                       f"dex_id = {dexDbId} AND " \
                       f"pair_id = {pairDbId} AND " \
                       f"token_in_id = '{tokenInDbId}' AND " \
                       f"token_out_id = '{tokenOutDbId}' AND " \
                       f"transaction_hash = '{transactionHash}' AND " \
                       f"block_number = {blockNumber} AND " \
                       f"block_timestamp = {blockTimestamp}"

    query = f"INSERT INTO transactions ({keys}) " \
            f"SELECT * FROM ({selectStatement}) AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM transactions WHERE {compareStatement}) " \
            f"LIMIT 1"

    lastRowID = executeWriteQuery(
        query=query
    )

    return lastRowID

def deleteTransactionToDB(transactionDbId):

     query = f"DELETE FROM transactions " \
             f"WHERE transactions.transaction_id={transactionDbId}"

     deletedRow = executeWriteQuery(
         query=query
     )

     return deletedRow