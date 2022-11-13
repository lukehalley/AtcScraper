import sys
from random import randint
from time import sleep

import mysql
from mysql.connector import OperationalError

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

def executeWriteQuery(query):

    dbConnection = initDBConnection()
    cursor = getCursor(dbConnection=dbConnection)

    try:
        cursor.execute(query)
        dbConnection.commit()
    except mysql.connector.errors.InternalError as error:
        deadlockDetected = "Deadlock" in error.msg
        if deadlockDetected:
            deadlockResolved = False
            while not deadlockResolved:
                sleep(randint(1, 5))
                try:
                    cursor.execute(query)
                    dbConnection.commit()
                    deadlockResolved = True
                except mysql.connector.errors.InternalError:
                    pass
        else:
            sys.exit(f"Write DB Error: {error}")
    except Exception:
        pass

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
            logger.warning("Command skipped: ", msg)