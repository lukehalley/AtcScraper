from src.db.actions.actions_General import executeWriteQuery
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def addNetworkToDB(networkName):

    keys = f"name, chain_number, chain_rpc, explorer_api_prefix, explorer_api_key, explorer_tx_url, explorer_type, symbol, max_gas, min_gas, is_valid"
    values = f"'{cleanString(networkName)}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL"

    query = f"INSERT INTO networks ({keys}) " \
            f"VALUES ({values})"

    lastRowID = executeWriteQuery(
        query=query
    )

    return lastRowID

