from src.db.db_Setup import getCursor
from src.db.db_Utils import executeQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def makeDBQuery(cnx):
    cursor = cnx.cursor()

    query = ("SELECT first_name, last_name, hire_date FROM employees "
             "WHERE hire_date BETWEEN %s AND %s")

    cursor.execute(query)

def checkIfRowExistsByValue(cnx, table, column, value):

    cursor = getCursor(cnx=cnx)

    query = f"" \
            f"SELECT COUNT(*) count FROM " \
            f"{table} WHERE " \
            f"{column}='{value}'"

    results = executeQuery(
        cursor=cursor,
        query=query
    )

    return bool(results[0]["count"])