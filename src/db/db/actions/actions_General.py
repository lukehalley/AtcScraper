from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def executeReadQuery(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

def executeWriteQuery(dbConnection, cursor, query):
    cursor.execute(query)
    dbConnection.commit()