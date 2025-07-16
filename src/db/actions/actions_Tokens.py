import re
from typing import Any, Optional

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeWriteQuery


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
    """
    cursor = getCursor(dbConnection=dbConnection)

    networkDbId = int(networkDbId)
    tokenName = re.sub('[^A-Za-z0-9 ]+', '', str(tokenName))
    tokenSymbol = tokenSymbol
    tokenAddress = tokenAddress

    keys = f"(network_id, name, symbol, address)"
    selectStatement = f"(SELECT {networkDbId} AS network_id, '{tokenName}' AS name, '{tokenSymbol}' AS symbol, '{tokenAddress}' AS address)"
    compareStatement = f"tokens.symbol = '{tokenSymbol}' AND tokens.network_id = {networkDbId}"

    query = f"INSERT INTO tokens{keys} " \
            f"SELECT * FROM {selectStatement} AS tmp " \
            f"WHERE NOT EXISTS " \
            f"(SELECT * FROM tokens WHERE {compareStatement}) " \
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
        fieldToUpdate: Name of the column to update
        fieldNewValue: New value to set for the field

    Returns:
        None
    """
    query = (
        f"UPDATE tokens "
        f"SET {fieldToUpdate}='{fieldNewValue}' "
        f"WHERE token_id={tokenDbId}"
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
    """
    query = (
        "UPDATE tokens "
        "SET address = NULL "
        "WHERE address = 'None'"
    )

    cursor = getCursor(dbConnection=dbConnection)

    return executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )