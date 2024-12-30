"""General database query utilities.

This module provides generic query functions for database operations
including table existence checks and row lookups by value conditions.
"""
from typing import Any, Dict, List, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Required tables for database initialization check
# These tables form the core data model for the ATC scraper:
# - dexs: Decentralized exchanges (Uniswap, SushiSwap, etc.)
# - pairs: Trading pairs (ETH/USDC, BTC/ETH, etc.)
# - tokens: Individual cryptocurrency tokens
# - networks: Blockchain networks (Ethereum, Polygon, BSC, etc.)
REQUIRED_TABLES = ('dexs', 'pairs', 'tokens', 'networks')
REQUIRED_TABLE_COUNT = len(REQUIRED_TABLES)

# Database schema name - all ATC tables reside in this schema
DATABASE_SCHEMA = 'atc'

# Information schema constants for table existence verification
INFORMATION_SCHEMA = "information_schema"
INFORMATION_TABLES = "tables"
TABLE_SCHEMA_COLUMN = "TABLE_SCHEMA"
TABLE_NAME_COLUMN = "TABLE_NAME"

# SQL result column aliases for aggregate queries
TABLE_COUNT_ALIAS = "tableCount"
ROW_COUNT_ALIAS = "count"


def checkDbInitialised(dbConnection: Any) -> bool:
    """
    Check if the database has all required tables initialized.

    Queries the information_schema to verify that all essential tables
    (dexs, pairs, tokens, networks) exist in the database.

    Args:
        dbConnection: Active database connection object

    Returns:
        bool: True if all required tables exist, False otherwise
    """
    table_list = ", ".join(f"'{t}'" for t in REQUIRED_TABLES)
    query = (
        f"SELECT COUNT(*) AS {TABLE_COUNT_ALIAS} "
        f"FROM `{INFORMATION_SCHEMA}`.`{INFORMATION_TABLES}` "
        f"WHERE `{TABLE_SCHEMA_COLUMN}` = '{DATABASE_SCHEMA}' AND "
        f"`{TABLE_NAME_COLUMN}` IN ({table_list})"
    )

    cursor = getCursor(dbConnection=dbConnection)

    tableResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    table_count = tableResults[0][TABLE_COUNT_ALIAS]
    is_initialized = table_count >= REQUIRED_TABLE_COUNT
    logger.debug(f"Database init check: {table_count}/{REQUIRED_TABLE_COUNT} tables found")
    return is_initialized


def getRowByValue(
    dbConnection: Any,
    table: str,
    conditions: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single row from a table based on column conditions.

    Args:
        dbConnection: Active database connection object
        table: Name of the database table to query
        conditions: List of condition dictionaries, each with column:value pairs

    Returns:
        Dictionary containing the row data if found, None otherwise

    Example:
        getRowByValue(conn, 'tokens', [{'symbol': 'ETH'}, {'network_id': 1}])
    """
    cursor = getCursor(dbConnection=dbConnection)

    # Build WHERE clause from conditions list
    # Each condition dict is expected to have a single key-value pair
    # Multiple conditions are joined with AND for precise matching
    where_clauses = []
    for condition in conditions:
        # Extract the single key-value pair from each condition dict
        columnName = list(condition.keys())[0]
        rowValue = condition[columnName]
        where_clauses.append(f"{columnName}='{rowValue}'")

    where_statement = " AND ".join(where_clauses)
    query = f"SELECT * FROM {table} WHERE {where_statement}"

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return results[0] if results else None


def checkIfRowExistsByValue(
    dbConnection: Any,
    table: str,
    column: str,
    value: Any
) -> bool:
    """
    Check if a row exists in a table with the specified column value.

    Args:
        dbConnection: Active database connection object
        table: Name of the database table to query
        column: Name of the column to check
        value: Value to search for in the column

    Returns:
        bool: True if a matching row exists, False otherwise
    """
    cursor = getCursor(dbConnection=dbConnection)

    query = (
        f"SELECT COUNT(*) AS {ROW_COUNT_ALIAS} FROM {table} "
        f"WHERE {column}='{value}'"
    )

    results = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return bool(results[0][ROW_COUNT_ALIAS])

