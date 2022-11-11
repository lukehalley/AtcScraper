from mysql.connector import OperationalError
from retry import retry

from src.db.actions.actions_Setup import initDBConnection, getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def executeReadQuery(query):

    dbConnection = initDBConnection()
    cursor = getCursor(dbConnection=dbConnection)

    cursor.execute(query)

    result = cursor.fetchall()

    dbConnection.close()

    return result

@retry()
def executeWriteQuery(query):

    dbConnection = initDBConnection()
    cursor = getCursor(dbConnection=dbConnection)

    cursor.execute(query)
    dbConnection.commit()

    lastRowID = cursor.lastrowid

    dbConnection.close()

    return lastRowID

def executeScriptsFromFile(dbConnection, filename):
    from src.db.actions.actions_Setup import getCursor

    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    cursor = getCursor(dbConnection=dbConnection)

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            cursor.execute(command)
        except OperationalError as msg:
            logger.warn("Command skipped: ", msg)