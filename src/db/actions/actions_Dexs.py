from src.db.actions.actions_General import executeWriteQuery
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def addDexToDB(networkDbId, dexName):

    query = f"INSERT IGNORE INTO dexs (network_id, name, factory, router) " \
            f"VALUES ('{networkDbId}', '{cleanString(dexName)}', NULL, NULL)"

    lastRowID = executeWriteQuery(
        query=query
    )

    return lastRowID

