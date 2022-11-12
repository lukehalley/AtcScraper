from mysql.connector import OperationalError

from src.db.actions.actions_Setup import initDBConnection, getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def executeScriptsFromFile(filename):

    dbConnection = initDBConnection()
    cursor = getCursor(dbConnection=dbConnection)

    # Open and read the file as a single buffer
    fd = open(f"src/db/sql/{filename}", 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    try:
        cursor.execute(sqlCommands[0])
        result = cursor.fetchall()
        dbConnection.close()
        return result
    except OperationalError as msg:
        logger.warning("Command skipped: ", msg)
        dbConnection.close()
        return None

