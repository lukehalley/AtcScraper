from src.db.db_Setup import getCursor
from src.db.db_Utils import executeWriteQuery, executeScriptsFromFile
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def createDatabase(dbConnection, databaseName="atc"):

    cursor = getCursor(dbConnection=dbConnection)

    query = f"CREATE DATABASE IF NOT EXISTS {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def dropDatabase(dbConnection, databaseName="atc"):
    cursor = getCursor(dbConnection=dbConnection)

    query = f"DROP DATABASE IF EXISTS {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def useDatabase(dbConnection, databaseName="atc"):
    cursor = getCursor(dbConnection=dbConnection)

    query = f"USE {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

def InitialiseDb(dbConnection):
    executeScriptsFromFile(
        dbConnection=dbConnection,
        filename="./db/sql/sql_Init.sql"
    )