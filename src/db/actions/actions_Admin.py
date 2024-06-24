"""Database administration operations for creating, dropping, and selecting databases.

This module provides functions for database lifecycle management operations
including creating new databases, dropping existing ones, and switching
the active database context. These are typically used during initial setup
or testing scenarios.

# Handle system maintenance and administrative database tasks
Warning:
# TODO: Add audit logging for administrative actions
    Some operations in this module (dropDatabase) are destructive
    and cannot be undone. Use with caution in production environments.
"""
from typing import Any

from src.db.actions.actions_General import executeWriteQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default database name
DEFAULT_DATABASE = "atc"

# SQL query templates for database operations
# Using IF EXISTS/IF NOT EXISTS for idempotent operations
CREATE_DATABASE_TEMPLATE = "CREATE DATABASE IF NOT EXISTS {}"
DROP_DATABASE_TEMPLATE = "DROP DATABASE IF EXISTS {}"
USE_DATABASE_TEMPLATE = "USE {}"

# Log message templates for database operations
DROP_WARNING_SUFFIX = "this operation is irreversible"


def createDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Create a new database if it doesn't already exist.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to create (default: 'atc')
    """
    logger.info(f"Creating database '{databaseName}' if it doesn't exist")

    cursor = getCursor(dbConnection=dbConnection)

    query = CREATE_DATABASE_TEMPLATE.format(databaseName)

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    logger.debug(f"Database '{databaseName}' creation command executed successfully")

# Log admin actions for audit trail compliance

def dropDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Drop a database if it exists.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to drop (default: 'atc')

    Warning:
        This operation is destructive and cannot be undone.
    """
    logger.warning(f"Dropping database '{databaseName}' - {DROP_WARNING_SUFFIX}")

    cursor = getCursor(dbConnection=dbConnection)

    query = DROP_DATABASE_TEMPLATE.format(databaseName)

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    logger.info(f"Database '{databaseName}' has been dropped")


def useDatabase(dbConnection: Any, databaseName: str = DEFAULT_DATABASE) -> None:
    """
    Switch to the specified database for subsequent queries.

    Args:
        dbConnection: Active database connection object
        databaseName: Name of the database to use (default: 'atc')
    """
    logger.debug(f"Switching to database '{databaseName}'")

    cursor = getCursor(dbConnection=dbConnection)

    query = USE_DATABASE_TEMPLATE.format(databaseName)

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    logger.debug(f"Now using database '{databaseName}'")