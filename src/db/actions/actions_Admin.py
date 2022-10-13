from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def createDatabase(dbConnection, databaseName="atc"):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"CREATE DATABASE IF NOT EXISTS {cleanString(databaseName)}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def dropDatabase(dbConnection, databaseName="atc"):
    cursor = getCursor(dbConnection=dbConnection)

    query = f"DROP DATABASE IF EXISTS {cleanString(databaseName)}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def useDatabase(dbConnection, databaseName="atc"):
    cursor = getCursor(dbConnection=dbConnection)

    query = f"USE {cleanString(databaseName)}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )