from functools import wraps

from mysql.connector import OperationalError
from retry import retry

from src.db.actions.actions_Setup import initDBConnection, getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

MAXIMUM_RETRY_ON_DEADLOCK = 8

def retry_on_deadlock_decorator(func):
    lock_messages_error = ['Deadlock found', 'Lock wait timeout exceeded']

    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt_count = 0
        while attempt_count < MAXIMUM_RETRY_ON_DEADLOCK:
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if any(msg in e.msg for msg in lock_messages_error) \
                        and attempt_count <= MAXIMUM_RETRY_ON_DEADLOCK:
                    logger.error('Deadlock detected. Trying sql transaction once more. Attempts count: %s'
                                 % (attempt_count + 1))
                else:
                    raise
            attempt_count += 1

    return wrapper

@retry_on_deadlock_decorator
def deadlock_safe_execute(db, stmt, *args, **kw):
    return db.execute(stmt, *args, **kw)

def executeReadQuery(query):
    dbConnection = initDBConnection()
    cursor = getCursor(dbConnection=dbConnection)

    deadlock_safe_execute(cursor, query)

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
            print("Command skipped: ", msg)
