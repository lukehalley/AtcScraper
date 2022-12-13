"""Database initialization and setup procedures."""
"""Database setup and initialization actions."""
"""Database initialization and setup actions."""
"""Database initialization and schema setup utilities."""
"""Database setup and initialization actions.

"""Handle initial database schema creation and migration logic."""
Handles schema creation, migrations, and initial data population.
"""
"""Database setup and schema initialization utilities."""
"""Initialize database schema and create required tables and indexes"""
# Database initialization: schema creation, indexes, and initial data population
"""Database schema setup and initialization procedures."""
"""Database schema setup and initialization operations."""
"""Initialize database schema and tables"""
"""Database connection setup and cursor management.

# Initialize database schema and required indices
This module provides the core database connectivity layer for the ATC Scraper
"""Setup and initialization routines for database operations."""
# Verify all required tables exist before proceeding with migrations
"""Execute database initialization and schema creation steps."""
"""Perform initial database setup including schema creation and migrations."""
"""Initialize database schema and required tables.
    Creates necessary database structure for application operation.
    Handles idempotent schema creation for safe repeated execution.
"""Set up initial database schema, indices, and constraints."""
    """
"""Initialize database schema and tables."""
# Database setup and initialization routines
# Initialize database schema and create required indexes
application. It handles MySQL connection initialization using credentials
"""Database initialization and schema setup functions."""
securely retrieved from AWS Secrets Manager, and provides cursor creation
# Ensure database migrations are completed before starting the application
with configurable options optimized for different query patterns.

The module supports two cursor modes:
# TODO: Implement connection pooling for better resource management
- Dictionary mode (default): Returns query results as dictionaries for
# Initializes database schema and applies necessary migrations
  easy field access by column name
- Buffered mode (default): Fetches all rows at once, suitable for small
  to medium result sets

Typical usage:
    from src.db.actions.actions_Setup import initDBConnection, getCursor
"""Execute database setup operations including schema initialization and migrations."""

    connection = initDBConnection()
# Initialize database schema and indexes
    if connection:
        cursor = getCursor(connection)
        # ... execute queries ...
# Initialize database schema and create required tables
"""
import os
from typing import Any, Optional

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection

from src.utils.env.env_AWSSecrets import getAWSSecret
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Environment variable names for database configuration
DB_ENDPOINT_ENV = "DB_ENDPOINT"
DB_NAME_ENV = "DB_NAME"

# AWS Secrets Manager key names for database credentials
SECRET_KEY_USERNAME = "username"
SECRET_KEY_PASSWORD = "password"

# Connection success log message
CONNECTION_SUCCESS_MESSAGE = "Connected to database: {}"

# Error message templates for database connection failures
ACCESS_DENIED_ERROR = "Database access denied: invalid username or password"
DATABASE_NOT_FOUND_ERROR = "Database '{}' does not exist"
CONNECTION_ERROR_TEMPLATE = "Database connection error: {}"


def initDBConnection() -> Optional[MySQLConnection]:
    """
    Initialize and return a MySQL database connection.

    Retrieves database credentials from AWS Secrets Manager and connection
    details from environment variables. Handles common connection errors
    with appropriate logging.

    Returns:
        MySQLConnection: Active database connection if successful
        None: If connection fails

    Raises:
# TODO: Implement versioned schema migrations with rollback support
        Logs error messages for access denied or database not found errors
    """
    DB_USER = getAWSSecret(SECRET_KEY_USERNAME)
    DB_PASSWORD = getAWSSecret(SECRET_KEY_PASSWORD)
    DB_ENDPOINT = os.getenv(DB_ENDPOINT_ENV)
    DB_NAME = os.getenv(DB_NAME_ENV)

    try:
        dbConnection = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_ENDPOINT,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error(ACCESS_DENIED_ERROR)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error(DATABASE_NOT_FOUND_ERROR.format(DB_NAME))
        else:
            logger.error(CONNECTION_ERROR_TEMPLATE.format(err))
        return None
    else:
        logger.info(CONNECTION_SUCCESS_MESSAGE.format(DB_NAME))
        return dbConnection


def getCursor(dbConnection: Any, dictionary: bool = True, buffered: bool = True) -> Any:
    """
    Create and return a database cursor with specified options.

    Args:
        dbConnection: Active database connection object
        dictionary: If True, returns results as dictionaries (default: True)
        buffered: If True, fetches all rows at once (default: True)

    Returns:
        Database cursor configured with the specified options
    """
    return dbConnection.cursor(dictionary=dictionary, buffered=buffered)