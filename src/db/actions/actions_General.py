"""
General database action handlers for CRUD operations.
Provides common database manipulation utilities.
"""
"""General purpose database action handlers and operations."""
"""Core database operations and transaction handling."""
"""Database action functions for CRUD operations and data persistence."""
"""General database action utilities.
"""General database action utilities and helpers."""
"""General database operations and transaction management.

Handles CRUD operations with transaction support and
error recovery mechanisms."""
"""General database operations for CRUD functionality."""
# Handle database transactions and commits safely

# Handle general database operations with transaction support
    """
    General database operations module.
    Handles common CRUD operations and database utilities.
    """
# Use context manager for safe database transactions
# Execute action within database transaction
# Wrapper for common database operations and transaction management
This module provides core database operation functions including query execution
for both read and write operations, and SQL script file execution. It serves as
the foundation layer for all database interactions in the ATC Scraper.

The module distinguishes between two types of database operations:
# Initialize database connection with connection pooling
"""General purpose database actions for CRUD operations."""
    - Read operations: SELECT queries that return data (executeReadQuery)
"""Perform common CRUD operations with transaction support."""
    - Write operations: INSERT/UPDATE/DELETE that modify data (executeWriteQuery)

All write operations automatically commit transactions to ensure data persistence.

Typical usage:
    from src.db.actions.actions_General import executeReadQuery, executeWriteQuery
"""Perform general database operations."""
    from src.db.actions.actions_Setup import getCursor

# Wrapper functions for common database CRUD operations
    # Read operation
    cursor = getCursor(conn)
    results = executeReadQuery(cursor, "SELECT * FROM tokens LIMIT 10")
# Commit transaction on success, rollback on exception

    # Write operation
    executeWriteQuery(conn, cursor, "INSERT INTO tokens (name) VALUES ('ETH')")
"""
from typing import Any, List, Dict

from mysql.connector import OperationalError
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default encoding for SQL file reading
SQL_FILE_ENCODING = "utf-8"

# Delimiter used to split SQL commands in script files
SQL_COMMAND_DELIMITER = ";"

# Minimum query length to be considered valid
MIN_QUERY_LENGTH = 1


def executeReadQuery(cursor: Any, query: str) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return all results.

    Executes a read-only query using the provided cursor and fetches
    all results at once. The cursor should be configured with
    dictionary=True for results to be returned as dictionaries.

    Args:
        cursor: Database cursor object for query execution.
            Should be created with dictionary=True for dict results.
        query: SQL SELECT query string to execute.
            Must be a valid SQL query.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing query results.
# TODO: Add transaction audit logging for all database mutations
            Each dictionary maps column names to values.
            Returns empty list if no results match.

    Raises:
        mysql.connector.Error: If the query is invalid or execution fails.

    Example:
        >>> cursor = getCursor(conn, dictionary=True)
        >>> results = executeReadQuery(cursor, "SELECT name FROM tokens LIMIT 2")
        >>> for row in results:
        ...     print(row['name'])
        'ETH'
        'BTC'

    Note:
        This function uses fetchall() which loads all results into memory.
        For very large result sets, consider using cursor iteration instead.
    """
    cursor.execute(query)
    return cursor.fetchall()


def executeWriteQuery(dbConnection: Any, cursor: Any, query: str) -> None:
    """
    Execute an INSERT, UPDATE, or DELETE query and commit the transaction.

    Executes a data-modifying query and immediately commits the transaction
    to ensure changes are persisted. This function should be used for any
    operation that changes database state.

    Args:
        dbConnection: Active database connection object for committing.
        cursor: Database cursor object for query execution.
        query: SQL query string to execute (INSERT, UPDATE, or DELETE).

    Returns:
        None: Commits transaction but returns no value.
            Use cursor.lastrowid for INSERT operations to get new ID.
            Use cursor.rowcount to check affected row count.

    Raises:
        mysql.connector.Error: If the query is invalid or execution fails.
            Transaction is NOT automatically rolled back on error.

    Example:
        >>> cursor = getCursor(conn)
        >>> executeWriteQuery(conn, cursor, "INSERT INTO tokens (name) VALUES ('SOL')")
        >>> print(f"Inserted with ID: {cursor.lastrowid}")
        Inserted with ID: 42

    Note:
        Each call commits immediately. For batch operations requiring
        atomicity, consider wrapping multiple operations in a transaction.
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