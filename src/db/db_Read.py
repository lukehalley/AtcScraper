from src.db.db_Setup import getCursor
from src.db.db_Utils import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def getRowByValue(dbConnection, table, column, value):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"SELECT * FROM " \
            f"{table} WHERE " \
            f"{column}='{value}'"

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return results[0]

def checkIfRowExistsByValue(dbConnection, table, column, value):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"SELECT COUNT(*) count FROM " \
            f"{table} WHERE " \
            f"{column}='{value}'"

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return bool(results[0]["count"])