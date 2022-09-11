from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def addNetworkToDB(dbConnection, networkName):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT INTO networks (name) " \
            f"VALUES ('{networkName}')"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

async def addDexToDB(dbConnection, networkDbId, dexName):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"INSERT INTO dexs (network_id, name) " \
            f"VALUES ('{networkDbId}', '{dexName}')"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )