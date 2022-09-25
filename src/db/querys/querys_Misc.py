from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery

def checkDbInitialised(dbConnection):

    query = "" \
            "SELECT COUNT(*) AS tableCount " \
            "FROM `information_schema`.`tables` " \
            "WHERE `TABLE_SCHEMA` = 'atc' AND " \
            "`TABLE_NAME` IN ('dexs', 'pairs', 'tokens', 'networks')"

    cursor = getCursor(dbConnection=dbConnection)

    tableResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return tableResults[0]["tableCount"] >= 4

