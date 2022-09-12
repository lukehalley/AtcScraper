from mysql.connector import OperationalError
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def executeReadQuery(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

def executeWriteQuery(dbConnection, cursor, query):
    cursor.execute(query)
    dbConnection.commit()

def executeScriptsFromFile(dbConnection, filename):
    from src.db.db_Setup import getCursor

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
            print("Command skipped: ", msg)