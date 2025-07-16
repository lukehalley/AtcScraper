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
        Logs error messages for access denied or database not found errors
    """
    DB_USER = getAWSSecret("username")
    DB_PASSWORD = getAWSSecret("password")
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
            logger.error("Database access denied: invalid username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error(f"Database '{DB_NAME}' does not exist")
        else:
            logger.error(f"Database connection error: {err}")
        return None
    else:
        logger.info(f"Connected to database: {DB_NAME}")
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