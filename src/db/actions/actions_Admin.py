from src.db.actions.actions_General import executeWriteQuery
from src.utils.data.data_Clean import cleanString
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def createDatabase(databaseName="atc"):

    query = f"CREATE DATABASE IF NOT EXISTS {cleanString(databaseName)}"

    executeWriteQuery(
        query=query
    )

def dropDatabase(databaseName="atc"):

    query = f"DROP DATABASE IF EXISTS {cleanString(databaseName)}"

    executeWriteQuery(
        query=query
    )

def useDatabase(databaseName="atc"):

    query = f"USE {cleanString(databaseName)}"

    executeWriteQuery(
        query=query
    )