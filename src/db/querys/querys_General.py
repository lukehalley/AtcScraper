from src.db.actions.actions_General import executeReadQuery
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def checkDbInitialised():

    query = "" \
            "SELECT COUNT(*) AS tableCount " \
            "FROM `information_schema`.`tables` " \
            "WHERE `TABLE_SCHEMA` = 'atc' AND " \
            "`TABLE_NAME` IN ('dexs', 'pairs', 'tokens', 'networks')"

    tableResults = executeReadQuery(
        query=query
    )

    return tableResults[0]["tableCount"] >= 4

def getRowByValue(table, conditions):

    amountOfConditions = len(conditions)

    columnName = list(conditions[0].keys())[0]
    rowValue = cleanString(conditions[0][columnName])

    query = f"SELECT * FROM " \
            f"{table} WHERE " \
            f"{columnName}='{rowValue}'"

    if amountOfConditions > 1:

        del conditions[0]

        for condition in conditions:
            columnName = list(condition.keys())[0]
            rowValue = cleanString(condition[columnName])

            query = \
                query + \
                " AND WHERE " \
                f"{columnName}='{rowValue}'"

    results = executeReadQuery(
        query=query
    )

    if results:
        return results[0]
    else:
        return None

def checkIfRowExistsByValue(table, column, value):

    query = f"SELECT COUNT(*) count FROM " \
            f"{table} WHERE " \
            f"{cleanString(column)}='{cleanString(value)}'"

    results = executeReadQuery(
        query=query
    )

    return bool(results[0]["count"])

