"""General database action utilities.

This module provides core database operation functions including query execution
for both read and write operations, and SQL script file execution.
"""
from typing import Any, List, Dict, Optional

from mysql.connector import OperationalError
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default encoding for SQL file reading
SQL_FILE_ENCODING = "utf-8"

# Delimiter used to split SQL commands in script files
SQL_COMMAND_DELIMITER = ";"


def executeReadQuery(cursor: Any, query: str) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return all results.

    Args:
        cursor: Database cursor object for query execution
        query: SQL SELECT query string

    Returns:
        List of dictionaries containing query results
    """
    cursor.execute(query)
    return cursor.fetchall()


def executeWriteQuery(dbConnection: Any, cursor: Any, query: str) -> None:
    """
    Execute an INSERT, UPDATE, or DELETE query and commit the transaction.

    Args:
        dbConnection: Active database connection object
        cursor: Database cursor object for query execution
        query: SQL query string to execute
    """
    cursor.execute(query)
    dbConnection.commit()


def executeScriptsFromFile(dbConnection: Any, filename: str) -> None:
    """
    Execute multiple SQL commands from a file.

    Reads a SQL file, splits it by semicolons, and executes each command
    sequentially. Errors are logged but don't halt execution, allowing
    partial script execution (useful for idempotent scripts).

    Args:
        dbConnection: Active database connection object
        filename: Path to the SQL file to execute

    Note:
        Commands that fail (e.g., DROP on non-existent tables) are skipped
        with a warning message printed to stdout.
    """
    from src.db.actions.actions_Setup import getCursor

    # Open and read the file as a single buffer
    with open(filename, 'r', encoding='utf-8') as fd:
        sqlFile = fd.read()

    cursor = getCursor(dbConnection=dbConnection)

    # Split SQL commands by semicolon delimiter
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # Skip empty commands and handle errors gracefully
        if not command.strip():
            continue
        try:
            cursor.execute(command)
        except OperationalError as msg:
            logger.warning(f"Command skipped: {msg}")