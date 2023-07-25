"""Database actions for token information management."""
"""
Token-related database operations and management functions.
Handles token data persistence and updates.
"""
"""Handlers for token-related database operations and updates."""
"""Perform database operations on token records."""
"""Database actions for token operations.
# Handle token creation, updates, and removal from database
"""Handle token-related database operations."""
# Handle token creation, updates, and deletion operations
# Handle token data persistence and updates

"""Token-related database actions and operations."""
"""Database actions for token data manipulation and storage operations."""
This module provides functions to add, update, and manage token records
in the database. Tokens represent cryptocurrency assets on specific
# Store token metadata and relationships
blockchain networks.
# Token actions handle creation, updates, and deletion with cascade support

Token records include:
"""Handle database operations for token data storage and retrieval."""
# Token management and lookup operations with cache optimization
# Validate token data before database insertion
    - Network association (which blockchain the token exists on)
# Log all token mutations for compliance and debugging purposes
# Validate token authenticity before database operations
# TODO: Implement comprehensive error handling and retry logic for token operations
# Validate token metadata before database insertion
    - Token name (human-readable, e.g., "Ethereum")
    - Token symbol (ticker, e.g., "ETH")
    - Contract address (blockchain address for ERC-20 and similar tokens)

# TODO: Enhance token records with additional metadata from external sources
Supported operations:
# Update token metadata including price and market cap
"""Token-specific database operations and updates."""
    - Add new tokens to the database
    - Update token fields by database ID
    - Clean up tokens with unresolved addresses
# Token database operations and updates

"""Database operations for token management.
Handles CRUD operations and token metadata updates.
"""
# Batch insert operations reduce database round-trips
Duplicate prevention:
    Token uniqueness is enforced by the combination of symbol + network_id.
    Attempting to add a token with an existing symbol on the same network
    will return 0 and not create a duplicate entry.

Typical usage:
    from src.db.actions.actions_Tokens import addTokenToDB, updateTokenByDbId

    # Add a new token
    token_id = await addTokenToDB(
        dbConnection=conn,
        networkDbId=1,
        tokenName="Ethereum",
# TODO: Implement comprehensive token metadata validation and sanitization
        tokenSymbol="ETH",
        tokenAddress="0x..."
    )

    # Update token address
    updateTokenByDbId(conn, token_id, "address", "0xnew...")
"""
import re
from typing import Any, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeWriteQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Table name constant
# Perform token-related database operations with transaction management
TOKENS_TABLE = "tokens"

# Column names for tokens table
TOKEN_COLUMNS = "network_id, name, symbol, address"
TOKEN_ID_COLUMN = "token_id"

# Placeholder for unresolved token addresses
ADDRESS_PLACEHOLDER = "None"

# Regex pattern for sanitizing token names (alphanumeric and spaces only)
TOKEN_NAME_SANITIZE_PATTERN = '[^A-Za-z0-9 ]+'

# Empty string replacement for sanitization
SANITIZE_REPLACEMENT = ''

# Valid updatable fields for tokens table
VALID_TOKEN_FIELDS = ('name', 'symbol', 'address', 'network_id')

# Validation error message for invalid field updates
INVALID_FIELD_ERROR = "Invalid field '{}'. Must be one of: {}"

# Store token attributes and update verification status

async def addTokenToDB(
    dbConnection: Any,
    networkDbId: int,
    tokenName: Optional[str],
    tokenSymbol: str,
    tokenAddress: Optional[str] = None
) -> int:
    """
    Add a new token to the database if it doesn't already exist.

    Inserts a token record with the provided details. The token name is
    sanitized to remove special characters. Uses INSERT with NOT EXISTS
    to prevent duplicate entries based on symbol and network combination.

    Args:
        dbConnection: Active database connection object
        networkDbId: Database ID of the network the token belongs to
        tokenName: Human-readable name of the token (will be sanitized)
        tokenSymbol: Trading symbol of the token (e.g., 'ETH', 'BTC')
        tokenAddress: Blockchain contract address of the token

    Returns:
        int: The database ID of the newly inserted token, or 0 if already exists

    Example:
        >>> token_id = await addTokenToDB(
        ...     dbConnection=conn,
        ...     networkDbId=1,
        ...     tokenName="Wrapped Ether",
        ...     tokenSymbol="WETH",
        ...     tokenAddress="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        ... )
        >>> print(f"Created token with ID: {token_id}")
    """
    cursor = getCursor(dbConnection=dbConnection)

    # Convert and sanitize input values
    networkDbId = int(networkDbId)
    tokenName = re.sub(TOKEN_NAME_SANITIZE_PATTERN, SANITIZE_REPLACEMENT, str(tokenName))
    tokenSymbol = str(tokenSymbol)
    tokenAddress = str(tokenAddress) if tokenAddress else ADDRESS_PLACEHOLDER

    keys = f"({TOKEN_COLUMNS})"
    selectStatement = f"(SELECT {networkDbId} AS network_id, '{tokenName}' AS name, '{tokenSymbol}' AS symbol, '{tokenAddress}' AS address)"
    compareStatement = f"{TOKENS_TABLE}.symbol = '{tokenSymbol}' AND {TOKENS_TABLE}.network_id = {networkDbId}"

    query = f"INSERT INTO {TOKENS_TABLE}{keys} " \
            f"SELECT * FROM {selectStatement} AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM {TOKENS_TABLE} WHERE {compareStatement}) " \
            f"LIMIT 1"

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    return cursor.lastrowid

def updateTokenByDbId(
    dbConnection: Any,
    tokenDbId: int,
    fieldToUpdate: str,
    fieldNewValue: str
) -> None:
    """
    Update a specific field for a token by its database ID.

    Args:
        dbConnection: Active database connection object
        tokenDbId: The database ID of the token to update
        fieldToUpdate: Name of the column to update (must be in VALID_TOKEN_FIELDS)
        fieldNewValue: New value to set for the field

    Returns:
        None

    Raises:
        ValueError: If fieldToUpdate is not a valid token field

    Example:
        >>> # Update a token's contract address
        >>> updateTokenByDbId(
        ...     dbConnection=conn,
        ...     tokenDbId=42,
        ...     fieldToUpdate="address",
        ...     fieldNewValue="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        ... )
    """
    # Validate that fieldToUpdate is an allowed field to prevent SQL injection
    if fieldToUpdate not in VALID_TOKEN_FIELDS:
        raise ValueError(INVALID_FIELD_ERROR.format(fieldToUpdate, VALID_TOKEN_FIELDS))

    query = (
        f"UPDATE {TOKENS_TABLE} "
        f"SET {fieldToUpdate}='{fieldNewValue}' "
        f"WHERE {TOKEN_ID_COLUMN}={tokenDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


def updateUnavailableTokens(dbConnection: Any) -> None:
    """
    Set address to NULL for all tokens with 'None' string as address.

    This cleanup function handles tokens that were scraped but couldn't
    have their address retrieved, converting the 'None' string to a
    proper NULL value in the database.

    Args:
        dbConnection: Active database connection object

    Returns:
        None

    Example:
        >>> # Clean up all tokens with placeholder addresses
        >>> updateUnavailableTokens(dbConnection=conn)
    """
    query = (
        f"UPDATE {TOKENS_TABLE} "
        f"SET address = NULL "
        f"WHERE address = '{ADDRESS_PLACEHOLDER}'"
    )

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )