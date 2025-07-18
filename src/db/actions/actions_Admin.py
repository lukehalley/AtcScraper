"""
Database administration operations for creating, dropping, and selecting databases.
"""
from typing import Any

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default database name
DEFAULT_DATABASE = "atc"


def createDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Create a new database if it doesn't already exist.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to create (default: 'atc')
    """
    cursor = getCursor(dbConnection=dbConnection)

    query = f"CREATE DATABASE IF NOT EXISTS {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


def dropDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Drop a database if it exists.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to drop (default: 'atc')

    Warning:
        This operation is destructive and cannot be undone.
    """
    cursor = getCursor(dbConnection=dbConnection)

    query = f"DROP DATABASE IF EXISTS {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


def useDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Switch to the specified database for subsequent queries.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to use (default: 'atc')
    """
    cursor = getCursor(dbConnection=dbConnection)

    query = f"USE {databaseName}"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )