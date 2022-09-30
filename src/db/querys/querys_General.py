from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

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

def getRowByValue(dbConnection, table, conditions):

    cursor = getCursor(dbConnection=dbConnection)

    amountOfConditions = len(conditions)

    columnName = list(conditions[0].keys())[0]
    rowValue = conditions[0][columnName]

    query = f"SELECT * FROM " \
            f"{table} WHERE " \
            f"{columnName}='{rowValue}'"

    if amountOfConditions > 1:

        del conditions[0]

        for condition in conditions:
            columnName = list(condition.keys())[0]
            rowValue = condition[columnName]

            query = \
                query + \
                " AND WHERE " \
                f"{columnName}='{rowValue}'"

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    if results:
        return results[0]
    else:
        return None

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

