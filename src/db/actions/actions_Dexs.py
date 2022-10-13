from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

async def addDexToDB(dbConnection, networkDbId, dexName):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT IGNORE INTO dexs (network_id, name, factory, router) " \
            f"VALUES ('{networkDbId}', '{cleanString(dexName)}', NULL, NULL)"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

